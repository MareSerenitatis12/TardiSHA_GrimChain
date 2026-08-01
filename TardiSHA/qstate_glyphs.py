"""Canonical Q-state language and the Stave I visible glyph seam.

The ALQC Canon physical pages 48-51 fix the four-state domain, its order,
and its meanings. Stave I supplies the visible written bodies:
Q0->🜔, Q1->🜕, Q2->🜖, Q3->🜗.

The four coordinate offices remain ``Q0,Q1,Q2,Q3``.  A resolved Court
supplies both its Q-bias and its four intensity settings.  The Domus visible
body is derived from that complete Court witness: the Q-bias is seamed once,
and each intensity is seamed in its original ordered position.  Thus
``(1,1,1,3)`` yields ``(🜕,🜕,🜕,🜗)``, while another resolved Court yields its
own body.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable

Q_STATES: Final[tuple[str, str, str, str]] = ("Q0", "Q1", "Q2", "Q3")
Q_STATE_NAMES: Final[dict[str, str]] = {
    "Q0": "FORM",
    "Q1": "TRUTH",
    "Q2": "SHADOW",
    "Q3": "RECURSION",
}

_PSI: Final[dict[str, str]] = {
    "Q0": "🜔",
    "Q1": "🜕",
    "Q2": "🜖",
    "Q3": "🜗",
}
_PSI_INV: Final[dict[str, str]] = {glyph: state for state, glyph in _PSI.items()}


@dataclass(frozen=True, slots=True)
class QStateSlot:
    """One fixed Q-coordinate office carrying its current numeric component."""

    state: str
    name: str
    glyph: str
    value: int


@dataclass(frozen=True, slots=True)
class DomusQBodyWitness:
    """Recoverable Court-derived bias and ordered visible Domus Q-body."""

    q_bias: str
    bias_glyph: str
    q_states: tuple[str, str, str, str]
    q_vector: tuple[int, int, int, int]
    q_glyphs: tuple[str, str, str, str]


def psi_q(q_state: str) -> str:
    """Forward Stave-I map: Q0/Q1/Q2/Q3 -> 🜔/🜕/🜖/🜗."""
    try:
        return _PSI[q_state]
    except KeyError as exc:
        raise ValueError(f"not a Q-state label: {q_state!r}") from exc


def q_state_of(glyph: str) -> str:
    """Reverse Stave-I map: 🜔/🜕/🜖/🜗 -> Q0/Q1/Q2/Q3."""
    try:
        return _PSI_INV[glyph]
    except KeyError as exc:
        raise ValueError(f"not a Q-state glyph: {glyph!r}") from exc


def type_q_value(value: int) -> str:
    """Resolve one canonical 0..3 Q-setting to its Q-state label."""
    if not isinstance(value, int) or isinstance(value, bool) or value not in (0, 1, 2, 3):
        raise ValueError(f"Q-state index must be one of 0,1,2,3; got {value!r}")
    return f"Q{value}"


def glyph_of_value(value: int) -> str:
    """Resolve one canonical 0..3 Q-setting through the First Seam."""
    return psi_q(type_q_value(value))


def value_of_glyph(glyph: str) -> int:
    """Return the 0..3 setting carried by one First-Seam glyph."""
    return int(q_state_of(glyph)[1])


def name_of(q_state: str) -> str:
    """Return the canonical state-name without deriving it from an Aeon."""
    try:
        return Q_STATE_NAMES[q_state]
    except KeyError as exc:
        raise ValueError(f"not a Q-state label: {q_state!r}") from exc


def _q_vector_values(q_vector: Iterable[int]) -> tuple[int, int, int, int]:
    values = tuple(q_vector)
    if len(values) != 4:
        raise ValueError(f"Q-vector must contain exactly four components; got {len(values)}")
    if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
        raise ValueError("TardiSHA canonical Q-vector components must be integers")
    if any(value not in (0, 1, 2, 3) for value in values):
        raise ValueError("TardiSHA canonical Q-vector components must lie in 0..3")
    return values  # type: ignore[return-value]


def q_state_slots(q_vector: Iterable[int]) -> tuple[QStateSlot, QStateSlot, QStateSlot, QStateSlot]:
    """Bind one exact vector to the four fixed Q-coordinate offices."""
    values = _q_vector_values(q_vector)
    slots = tuple(
        QStateSlot(state, name_of(state), psi_q(state), value)
        for state, value in zip(Q_STATES, values)
    )
    return slots  # type: ignore[return-value]


def q_vector_glyphs(q_vector: Iterable[int]) -> tuple[str, str, str, str]:
    """Derive the changing visible Domus Q-body in unchanged vector order."""
    values = _q_vector_values(q_vector)
    glyphs = tuple(glyph_of_value(value) for value in values)
    return glyphs  # type: ignore[return-value]


def derive_domus_q_body(q_bias: str, q_vector: Iterable[int]) -> DomusQBodyWitness:
    """Apply the First Seam to one resolved Court bias and Q-vector.

    The Court determines ``q_bias`` and ``q_vector``.  This function neither
    chooses a parent nor mutates their order; it exposes the exact visible
    Domus body and proves that the seam returns to the same values.
    """
    bias_glyph = psi_q(q_bias)
    values = _q_vector_values(q_vector)
    glyphs = q_vector_glyphs(values)
    if q_state_of(bias_glyph) != q_bias:
        raise RuntimeError("Domus Q-bias failed First-Seam return")
    if tuple(value_of_glyph(glyph) for glyph in glyphs) != values:
        raise RuntimeError("Domus Q-vector failed First-Seam return")
    return DomusQBodyWitness(q_bias, bias_glyph, Q_STATES, values, glyphs)
