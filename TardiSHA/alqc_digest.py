"""ALQC-native deterministic sponge for TardiSHA runtime identity.

This is the internal TardiSHA/ALQC digest
substrate: twelve Goetic lanes, Court load mixing, 110/144 flow pressure,
and domain-separated absorption/squeeze.
"""
from __future__ import annotations

from math import isqrt

try:
    from ._alqc_kernel import absorb_raw as _compiled_absorb_raw
except ImportError as exc:
    raise RuntimeError(
        "TardiSHA requires the compiled ALQC kernel"
    ) from exc

from .canon import (
    GLYPH_BODY,
    GLYPH_LAWS,
    SATURATION_LIMIT,
    TOTAL_CAPACITY,
    court_flow_active,
    court_load,
    court_node,
    _COURT_LOAD_TABLE,
    _position,
)

MASK64 = (1 << 64) - 1
DIGEST_BYTES = 32
DIGEST_HEX_LENGTH = DIGEST_BYTES * 2

# --- Exact golden and Liquid-Governor constants ---
# Both values are derived with integer isqrt. The absorption and permutation schedule
# remains the established TardiSHA kernel contract; this repair does not replace it.
#   Φ = (1+√5)/2.  1/Φ = Φ−1 = (√5−1)/2.
#   GOLDEN64  = ⌊2^64 / Φ⌋ = ⌊2^63(√5−1)⌋              (the golden-harmonic multiplier)
#   GOVERNOR64 = ⌊2^64 · 2Φ⁻²⌋ = ⌊2^64(3−√5)⌋          (the 110/144 governor ratio, L722)
GOLDEN64 = ((isqrt(5 << 126) - (1 << 63)) | 1) & MASK64
GOVERNOR64 = ((3 * (1 << 64) - isqrt(5 << 128)) | 1) & MASK64

# Aeternum Closure terminator (⌬, 639 Hz, "D-COMP → 0"): the finalization marker
# is the ⌬ closure frequency, replacing the foreign 0x80 pad byte.
CLOSURE_TAG = int(GLYPH_LAWS["⌬"].frequency.real).to_bytes(2, "big")  # 639 → b"\x02\x7f"


def _rotl(value: int, shift: int) -> int:
    shift &= 63
    value &= MASK64
    return ((value << shift) | (value >> (64 - shift))) & MASK64 if shift else value


def _glyph_seed(index: int) -> int:
    glyph = GLYPH_BODY[index]
    law = GLYPH_LAWS[glyph]
    q0, q1, q2, q3 = law.q_vector
    frequency = complex(law.frequency)
    # Seed only from operator body and numeric law. English meanings, prose, and
    # formatting are not mathematical identity and never enter the digest.
    text = b"\x1f".join(
        (
            glyph.encode("utf-8"),
            bytes((q0 & 0xFF, q1 & 0xFF, q2 & 0xFF, q3 & 0xFF)),
            frequency.real.hex().encode("ascii"),
            frequency.imag.hex().encode("ascii"),
        )
    )
    acc = (
        0xA17C_0000_0000_0000
        ^ ((index + 1) * GOLDEN64)
        ^ ((q0 & 0xFFFF) << 48)
        ^ ((q1 & 0xFFFF) << 32)
        ^ ((q2 & 0xFFFF) << 16)
        ^ (q3 & 0xFFFF)
    ) & MASK64
    for offset, byte in enumerate(text):
        acc ^= (byte + 1) << ((offset % 8) * 8)
        acc = _rotl(acc + GOVERNOR64 + offset + byte, ((byte + index) % 63) + 1)
    return acc & MASK64


INITIAL_LANES = tuple(_glyph_seed(index) for index in range(len(GLYPH_BODY)))
_Q_MIXES = tuple(
    ((law.q_vector[0] & 0xFFFF) << 48)
    ^ ((law.q_vector[1] & 0xFFFF) << 32)
    ^ ((law.q_vector[2] & 0xFFFF) << 16)
    ^ (law.q_vector[3] & 0xFFFF)
    for law in (GLYPH_LAWS[glyph] for glyph in GLYPH_BODY)
)
_Q_SUMS = tuple(sum(GLYPH_LAWS[glyph].q_vector) for glyph in GLYPH_BODY)
_IDENTITY_COURTS = tuple(12 * index + index for index in range(12))
COMPILED_KERNEL_ACTIVE = True


class ALQCDigest:
    """Small deterministic ALQC sponge with update/digest API."""

    __slots__ = ("_lanes", "_position", "_domain")

    def __init__(self, domain: bytes = b"TARDISHA:ALQC-DIGEST\x00") -> None:
        if not isinstance(domain, (bytes, bytearray, memoryview)) or not bytes(domain):
            raise ValueError("ALQC digest domain must be non-empty bytes")
        self._lanes = list(INITIAL_LANES)
        self._position = 0
        self._domain = bytes(domain)
        self.update(self._domain)

    def copy(self) -> "ALQCDigest":
        other = object.__new__(ALQCDigest)
        other._lanes = list(self._lanes)
        other._position = self._position
        other._domain = self._domain
        return other

    def update(self, data: bytes | bytearray | memoryview) -> "ALQCDigest":
        block = bytes(data)
        self._update_raw(len(block).to_bytes(8, "big"))
        self._update_raw(block)
        return self

    def _update_raw(self, data: bytes | bytearray | memoryview) -> "ALQCDigest":
        block = bytes(data)
        if block:
            self._lanes, self._position = _compiled_absorb_raw(
                self._lanes,
                self._position,
                block,
                INITIAL_LANES,
                _Q_MIXES,
                _Q_SUMS,
            )
        return self

    def _update_frame(self, tag: bytes, data: bytes | bytearray | memoryview) -> "ALQCDigest":
        block = bytes(data)
        length_bytes = len(block).to_bytes(8, "big")
        self._update_raw(tag)
        self._update_raw(length_bytes)
        self._update_raw(block)
        return self

    def _round(self, marker: int) -> None:
        resolution = self._lanes
        court_table = _COURT_LOAD_TABLE
        identity_courts = _IDENTITY_COURTS
        q_mixes = _Q_MIXES
        q_sums = _Q_SUMS
        previous = resolution[-1]
        for index in range(12):
            partner_index = (index * 7 + marker + (resolution[(index + 5) % 12] & 0xFF)) % 12
            load = court_table[index][partner_index]
            flow = 1 if (identity_courts[index] + load) % TOTAL_CAPACITY < SATURATION_LIMIT else 0
            pressure = ((load + 1) * 0x0101_0101_0101_0101) & MASK64
            current = resolution[index]
            neighbor = resolution[(index + 1) % 12]
            folded = current ^ _rotl(previous, (index + marker) % 64) ^ _rotl(neighbor, (load % 63) + 1)
            folded = (folded + pressure + q_mixes[index] + marker + (flow * TOTAL_CAPACITY)) & MASK64
            resolution[index] = _rotl(folded, ((load + q_sums[index] + marker) % 63) + 1)
            previous = current


    def _finalized_lanes(self) -> list[int]:
        other = self.copy()
        bit_len = self._position * 8
        other._update_raw(CLOSURE_TAG)  # ⌬ Aeternum Closure terminator (639 Hz), not 0x80
        other._update_raw(bit_len.to_bytes(16, "big"))
        for marker in range(12 + (self._position % 12)):
            other._round(bit_len + marker + TOTAL_CAPACITY)
        return other._lanes

    def digest(self, length: int = DIGEST_BYTES) -> bytes:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError("digest length must be a positive integer")
        resolution = self._finalized_lanes()
        out = bytearray()
        block_index = 0
        bit_len = self._position * 8
        while len(out) < length:
            # One complete Goetic turn precedes every four-Q-state output block.
            # No lane is emitted directly, and every block is fed back before the next.
            for turn in range(12):
                lane = (block_index + turn) % 12
                counter = (
                    ((block_index + 1) * GOLDEN64)
                    ^ ((turn + 1) * GOVERNOR64)
                    ^ bit_len
                    ^ INITIAL_LANES[turn]
                ) & MASK64
                resolution[lane] ^= _rotl(counter, ((lane + turn + block_index) % 63) + 1)
                saved = self._lanes
                self._lanes = resolution
                try:
                    self._round(bit_len + TOTAL_CAPACITY + block_index * 12 + turn)
                finally:
                    resolution = self._lanes
                    self._lanes = saved

            words: list[int] = []
            for q_state in range(4):
                a, b, c = q_state, q_state + 4, q_state + 8
                word = (
                    resolution[a]
                    + _rotl(resolution[b], ((q_state + block_index + 1) % 63) + 1)
                    + _rotl(resolution[c], ((q_state + block_index + 17) % 63) + 1)
                    + _Q_MIXES[a]
                    + _Q_MIXES[b]
                    + _Q_MIXES[c]
                    + ((block_index + 1) * GOVERNOR64)
                ) & MASK64
                word ^= _rotl(resolution[(a + 5) % 12], ((q_state + 29) % 63) + 1)
                word = _rotl(word, ((q_state * 13 + block_index + 1) % 63) + 1)
                words.append(word)
                out.extend(word.to_bytes(8, "big"))

            for q_state, word in enumerate(words):
                for lane in (q_state, q_state + 4, q_state + 8):
                    resolution[lane] = _rotl(
                        (resolution[lane] + word + INITIAL_LANES[(lane + block_index) % 12]) & MASK64,
                        ((lane + q_state + block_index + 1) % 63) + 1,
                    )
            saved = self._lanes
            self._lanes = resolution
            try:
                self._round(bit_len + TOTAL_CAPACITY + block_index * 12 + 12)
            finally:
                resolution = self._lanes
                self._lanes = saved
            block_index += 1
        return bytes(out[:length])

    def digest_separated(self, length: int = DIGEST_BYTES) -> bytes:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError("digest length must be a positive integer")
        separated = self.copy()
        separated._update_frame(b"DIGEST-LENGTH\x00", length.to_bytes(8, "big"))
        return separated.digest(length)

    def hexdigest(self, length: int = DIGEST_BYTES) -> str:
        return self.digest(length).hex()


def alqc_digest(data: bytes | bytearray | memoryview, *, domain: bytes = b"TARDISHA:ALQC-DIGEST\x00", length: int = DIGEST_BYTES) -> bytes:
    return ALQCDigest(domain).update(data).digest_separated(length)


def alqc_hexdigest(data: bytes | bytearray | memoryview, *, domain: bytes = b"TARDISHA:ALQC-DIGEST\x00", length: int = DIGEST_BYTES) -> str:
    return alqc_digest(data, domain=domain, length=length).hex()


def validate_digest_hex(value: str, *, field: str = "source_digest") -> str:
    normalized = value.casefold()
    if len(normalized) != DIGEST_HEX_LENGTH or any(character not in "0123456789abcdef" for character in normalized):
        raise ValueError(f"{field} must be {DIGEST_HEX_LENGTH} hexadecimal characters")
    return normalized
