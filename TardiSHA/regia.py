"""Silent Regia / Revivocus repair and pre-inscription warp for TardiSHA.

Phase 2 defines the pure repair law over a visible candidate body.
Phase 3 adds the bounded pending field that applies that same law before a Domus center
is committed. Raw coordinate generation remains untouched.

Gate A is tested before Gate B.
Gate A refuses an Enoch stack that reaches before written history.
Gate B refuses the seventh backward reach when that landing body exists.

Trigger set and deletion set are intentionally different:
- only ཪ ☍ ߷ 🜚 🜛 deepen backward reach;
- every generated Enoch in the affected repair span is removed on either gate.
Aeons are never erased. Regia emits no marker. One Q0/Form glyph is left at the repair
point and continuation proceeds from Form.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable, Iterator

from .enoch import GENERATED_ENOCH_GLYPHS, is_generated_enoch, reaches_backward
from .qstate_glyphs import psi_q


FORM_GLYPH: Final[str] = psi_q("Q0")
REVIVOCUS_REACH: Final[int] = 7
_GENERATED_ENOCH_SET: Final[frozenset[str]] = frozenset(GENERATED_ENOCH_GLYPHS)


@dataclass(frozen=True, slots=True)
class RegiaDecision:
    """One Gate-A/Gate-B decision for a maximal Enoch stack."""

    gate: str
    backward_reach: int
    available_history: int
    landing_history_distance: int


@dataclass(frozen=True, slots=True)
class RegiaEvent:
    """One deterministic silent repair decision over the original visible body."""

    gate: str
    stack_start: int
    stack_stop: int
    repair_start: int
    backward_reach: int
    available_history: int
    removed_enochs: tuple[str, ...]
    preserved_body: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RegiaResult:
    """Corrected visible body plus the event record used for replay/tests."""

    source: str
    corrected: str
    events: tuple[RegiaEvent, ...]


def _validate_body(body: str) -> None:
    if not isinstance(body, str):
        raise TypeError("Regia requires one visible GrimChain body as str")


def decide_enoch_stack(stack: str, available_history: int) -> RegiaDecision | None:
    """Apply the single Regia gate law to one complete maximal Enoch stack.

    ``available_history`` counts Aeon bodies preceding this stack. Gate A is absolute and
    is evaluated before the Revivocus depth boundary. Cadence Enochs remain part of the
    stack but do not increment backward reach.
    """
    if not isinstance(stack, str):
        raise TypeError("Enoch stack must be a string")
    if isinstance(available_history, bool) or not isinstance(available_history, int) or available_history < 0:
        raise ValueError("available_history must be a non-negative integer")
    if not stack:
        return None
    if any(not is_generated_enoch(glyph) for glyph in stack):
        raise ValueError("Regia stack classification requires only generated Enoch glyphs")

    # Any Enoch structure at the written beginning has no body before it.
    if available_history == 0:
        return RegiaDecision("A", 0, 0, 0)

    reach = 0
    for glyph in reversed(stack):
        if not reaches_backward(glyph):
            continue
        reach += 1
        if reach > available_history:
            return RegiaDecision("A", reach, available_history, available_history)
        if reach == REVIVOCUS_REACH:
            return RegiaDecision("B", reach, available_history, REVIVOCUS_REACH)
    return None


def _maximal_enoch_stacks(body: str) -> tuple[tuple[int, int], ...]:
    """Return half-open spans for maximal runs of generated Enoch glyphs."""
    spans: list[tuple[int, int]] = []
    i = 0
    while i < len(body):
        if not is_generated_enoch(body[i]):
            i += 1
            continue
        start = i
        i += 1
        while i < len(body) and is_generated_enoch(body[i]):
            i += 1
        spans.append((start, i))
    return tuple(spans)


def _history_indices(body: str, stop: int) -> tuple[int, ...]:
    """Indices of preserved Aeon bodies before ``stop``, in written order."""
    return tuple(i for i in range(stop) if not is_generated_enoch(body[i]))


def _classify_stack(body: str, start: int, stop: int) -> tuple[str, int, int, int] | None:
    """Map the shared stack decision back onto source-body coordinates."""
    history = _history_indices(body, start)
    decision = decide_enoch_stack(body[start:stop], len(history))
    if decision is None:
        return None

    if decision.gate == "A":
        if not history:
            repair_start = next(
                (i for i in range(stop, len(body)) if not is_generated_enoch(body[i])),
                len(body),
            )
        else:
            repair_start = history[0]
    else:
        repair_start = history[-decision.landing_history_distance]
    return (
        decision.gate,
        repair_start,
        decision.backward_reach,
        decision.available_history,
    )


def _repair_once(body: str, event: RegiaEvent) -> str:
    """Apply one event to the original body, preserving every Aeon glyph."""
    start = event.repair_start
    stop = event.stack_stop
    if start >= stop:
        prefix = body[:event.stack_start]
        suffix = body[event.stack_stop:]
        return prefix + FORM_GLYPH + suffix
    span = body[start:stop]
    preserved = "".join(g for g in span if not is_generated_enoch(g))
    return body[:start] + FORM_GLYPH + preserved + body[stop:]


def apply_regia(body: str) -> RegiaResult:
    """Apply the Phase-2 silent Regia law to one finite visible candidate body."""
    _validate_body(body)
    if not body:
        return RegiaResult(body, body, ())

    pending: list[RegiaEvent] = []
    covered_until = len(body)
    for start, stop in reversed(_maximal_enoch_stacks(body)):
        decision = _classify_stack(body, start, stop)
        if decision is None:
            continue
        gate, repair_start, reach, available = decision
        if stop > covered_until:
            continue
        affected = body[start:stop] if repair_start >= stop else body[repair_start:stop]
        removed = tuple(g for g in affected if is_generated_enoch(g))
        preserved = tuple(g for g in affected if not is_generated_enoch(g))
        pending.append(
            RegiaEvent(
                gate=gate,
                stack_start=start,
                stack_stop=stop,
                repair_start=repair_start,
                backward_reach=reach,
                available_history=available,
                removed_enochs=removed,
                preserved_body=preserved,
            )
        )
        covered_until = min(covered_until, repair_start if repair_start < stop else start)

    corrected = body
    for event in pending:
        corrected = _repair_once(corrected, event)
    return RegiaResult(body, corrected, tuple(reversed(pending)))


def regia_corrected(body: str) -> str:
    """Return only the Phase-2 corrected visible body."""
    return apply_regia(body).corrected


@dataclass(frozen=True, slots=True)
class RemissedCoordinate:
    """One raw Enoch coordinate refused by Regia and bound to its Q0 scar."""

    raw_coordinate: int
    glyph: str
    scar_glyph: str
    event_sequence: int


@dataclass(frozen=True, slots=True)
class RegiaLineageEvent:
    """Immutable append-only witness for one Regia/Revivocus transition."""

    sequence: int
    gate: str
    scar_glyph: str
    trigger_raw_coordinate: int
    remissed: tuple[RemissedCoordinate, ...]
    preserved_aeon_coordinates: tuple[int, ...]
    consumed_prior_scars: tuple[int, ...]
    before_pending: tuple[tuple[str, bool, int | None, int | None], ...]
    after_pending: tuple[tuple[str, bool, int | None, int | None], ...]


@dataclass(slots=True)
class _WarpToken:
    glyph: str
    aeon: bool
    raw_coordinate: int | None
    scar_event: int | None = None

    def snapshot(self) -> tuple[str, bool, int | None, int | None]:
        return (self.glyph, self.aeon, self.raw_coordinate, self.scar_event)


class RegiaWarpState:
    """Bounded pre-inscription field with append-only Regia lineage.

    The field retains the last seven Aeons and every Enoch between them. Anything before
    that horizon can no longer be reached by Gate B and is therefore safe to commit.
    Every repair appends one immutable lineage event; no prior event is rewritten.
    """

    __slots__ = (
        "_pending", "_stack_start", "_source_aeons", "_raw_coordinate", "_lineage"
    )

    def __init__(self) -> None:
        self._pending: list[_WarpToken] = []
        self._stack_start: int | None = None
        self._source_aeons = 0
        self._raw_coordinate = 0
        self._lineage: list[RegiaLineageEvent] = []

    @property
    def source_aeons(self) -> int:
        return self._source_aeons

    @property
    def raw_coordinates_consumed(self) -> int:
        return self._raw_coordinate

    @property
    def pending_glyphs(self) -> str:
        return "".join(token.glyph for token in self._pending)

    @property
    def lineage(self) -> tuple[RegiaLineageEvent, ...]:
        """Return an immutable view of the append-only event sequence."""
        return tuple(self._lineage)

    def _source_aeon_indices(self) -> list[int]:
        return [i for i, token in enumerate(self._pending) if token.aeon]

    def _resolve_stack(self) -> None:
        if self._stack_start is None:
            return
        start = self._stack_start
        stack = "".join(token.glyph for token in self._pending[start:])
        decision = decide_enoch_stack(stack, self._source_aeons)
        if decision is not None:
            aeon_indices = self._source_aeon_indices()
            if decision.gate == "A":
                repair = aeon_indices[0] if aeon_indices else start
            else:
                repair = aeon_indices[-decision.landing_history_distance]

            before = tuple(token.snapshot() for token in self._pending)
            affected = self._pending[repair:]
            sequence = len(self._lineage)

            remissed_tokens = [
                token for token in affected
                if not token.aeon and token.raw_coordinate is not None
            ]
            remissed = tuple(
                RemissedCoordinate(
                    raw_coordinate=token.raw_coordinate,
                    glyph=token.glyph,
                    scar_glyph=FORM_GLYPH,
                    event_sequence=sequence,
                )
                for token in remissed_tokens
            )
            preserved_coords = tuple(
                token.raw_coordinate for token in affected
                if token.aeon and token.raw_coordinate is not None
            )
            consumed_prior_scars = tuple(
                token.scar_event for token in affected
                if not token.aeon and token.raw_coordinate is None and token.scar_event is not None
            )

            # Cleanup is total across Enochs in the affected repair span. Every raw Aeon
            # remains in written order. The new Q0 scar is synthetic and points back to
            # this immutable lineage event rather than pretending to be a raw coordinate.
            preserved = [token for token in affected if token.aeon]
            scar = _WarpToken(FORM_GLYPH, False, None, sequence)
            self._pending[repair:] = [scar, *preserved]
            after = tuple(token.snapshot() for token in self._pending)

            trigger_raw = max(
                (token.raw_coordinate for token in self._pending[:repair] + remissed_tokens
                 if token.raw_coordinate is not None),
                default=max(self._raw_coordinate - 1, 0),
            )
            self._lineage.append(
                RegiaLineageEvent(
                    sequence=sequence,
                    gate=decision.gate,
                    scar_glyph=FORM_GLYPH,
                    trigger_raw_coordinate=trigger_raw,
                    remissed=remissed,
                    preserved_aeon_coordinates=preserved_coords,
                    consumed_prior_scars=consumed_prior_scars,
                    before_pending=before,
                    after_pending=after,
                )
            )
        self._stack_start = None

    def _commit_safe_prefix(self) -> str:
        aeon_indices = self._source_aeon_indices()
        if len(aeon_indices) <= REVIVOCUS_REACH:
            return ""
        # Keep the newest seven Aeons. A future seventh reach may insert Form immediately
        # before the oldest of these, but can never alter anything before it.
        cut = aeon_indices[-REVIVOCUS_REACH]
        stable = "".join(token.glyph for token in self._pending[:cut])
        del self._pending[:cut]
        if self._stack_start is not None:
            self._stack_start -= cut
        return stable

    def feed(self, body: str) -> str:
        """Consume raw glyphs and return only the newly irreversible visible prefix."""
        _validate_body(body)
        committed: list[str] = []
        for glyph in body:
            raw_coordinate = self._raw_coordinate
            self._raw_coordinate += 1
            if is_generated_enoch(glyph):
                if self._stack_start is None:
                    self._stack_start = len(self._pending)
                self._pending.append(_WarpToken(glyph, False, raw_coordinate))
                continue

            # An Aeon closes the maximal Enoch stack immediately before it.
            self._resolve_stack()
            self._pending.append(_WarpToken(glyph, True, raw_coordinate))
            self._source_aeons += 1
            stable = self._commit_safe_prefix()
            if stable:
                committed.append(stable)
        return "".join(committed)

    def finish(self) -> str:
        """Finish a finite source body without mutating prior lineage entries."""
        self._resolve_stack()
        stable = "".join(token.glyph for token in self._pending)
        self._pending.clear()
        self._stack_start = None
        return stable


def lineage_regia_body(body: str) -> tuple[str, tuple[RegiaLineageEvent, ...]]:
    """Correct one finite raw body and return its immutable append-only lineage."""
    state = RegiaWarpState()
    corrected = state.feed(body) + state.finish()
    return corrected, state.lineage


def verify_regia_lineage(
    body: str,
    corrected: str,
    lineage: tuple[RegiaLineageEvent, ...],
) -> bool:
    """Replay raw→corrected and require exact immutable event-by-event lineage."""
    if not isinstance(lineage, tuple):
        return False
    try:
        replay_corrected, replay_lineage = lineage_regia_body(body)
    except (TypeError, ValueError, RuntimeError):
        return False
    if replay_corrected != corrected or replay_lineage != lineage:
        return False
    if tuple(event.sequence for event in lineage) != tuple(range(len(lineage))):
        return False
    for event in lineage:
        if event.scar_glyph != FORM_GLYPH:
            return False
        if any(item.event_sequence != event.sequence or item.scar_glyph != FORM_GLYPH for item in event.remissed):
            return False
        if tuple(item.raw_coordinate for item in event.remissed) != tuple(sorted(item.raw_coordinate for item in event.remissed)):
            return False
    return True



def warp_regia_body(body: str) -> str:
    """Streaming-equivalent Phase-3 correction for one finite test/body."""
    state = RegiaWarpState()
    return state.feed(body) + state.finish()


def iter_regia_middle(
    seed: bytes,
    middle_length: int,
    *,
    chunk_characters: int = 8192,
    raw_window_characters: int = 8192,
) -> Iterator[str]:
    """Yield the corrected visible GrimChain prefix without touching raw generation.

    Raw coordinates are pulled through ``hashing.iter_middle_window`` in successive
    windows. Only irreversible output is yielded. More raw coordinates are consumed as
    needed so the requested *visible* extent remains exact after Regia repairs.
    """
    from .hashing import iter_middle_window, validate_middle_length

    width = validate_middle_length(middle_length)
    if isinstance(chunk_characters, bool) or not isinstance(chunk_characters, int) or chunk_characters <= 0:
        raise ValueError("chunk_characters must be a positive integer")
    if isinstance(raw_window_characters, bool) or not isinstance(raw_window_characters, int) or raw_window_characters <= 0:
        raise ValueError("raw_window_characters must be a positive integer")
    if width == 0:
        return

    state = RegiaWarpState()
    raw_cursor = 0
    emitted = 0
    output = ""
    while emitted < width:
        raw = "".join(
            iter_middle_window(
                seed,
                raw_cursor,
                raw_window_characters,
                chunk_characters=raw_window_characters,
            )
        )
        if len(raw) != raw_window_characters:
            raise RuntimeError("raw TardiSHA continuation window ended unexpectedly")
        raw_cursor += raw_window_characters
        output += state.feed(raw)

        while output and emitted < width:
            take = min(chunk_characters, width - emitted, len(output))
            if take <= 0:
                break
            piece = output[:take]
            output = output[take:]
            emitted += len(piece)
            yield piece



def iter_regia_window(
    seed: bytes,
    start_coordinate: int,
    span_length: int,
    *,
    chunk_characters: int = 8192,
    raw_window_characters: int = 8192,
) -> Iterator[str]:
    """Yield one corrected visible window by replaying from the stable origin checkpoint.

    Raw random access remains untouched. Corrected coordinates are stateful, so a visible
    window must carry the Enoch/Regia state that precedes it. Phase 4 uses coordinate zero
    as the canonical stable checkpoint: the same ``RegiaWarpState`` is replayed until
    ``start_coordinate`` corrected glyphs have been crossed, then exactly ``span_length``
    corrected glyphs are yielded. This is deterministic and cannot invent a second law.
    """
    from .hashing import iter_middle_window, validate_middle_length

    if isinstance(start_coordinate, bool) or not isinstance(start_coordinate, int) or start_coordinate < 0:
        raise ValueError("corrected start_coordinate must be a non-negative integer")
    width = validate_middle_length(span_length)
    if isinstance(chunk_characters, bool) or not isinstance(chunk_characters, int) or chunk_characters <= 0:
        raise ValueError("chunk_characters must be a positive integer")
    if isinstance(raw_window_characters, bool) or not isinstance(raw_window_characters, int) or raw_window_characters <= 0:
        raise ValueError("raw_window_characters must be a positive integer")
    if width == 0:
        return

    state = RegiaWarpState()
    raw_cursor = 0
    visible_cursor = 0
    target_stop = start_coordinate + width
    buffered = ""

    while visible_cursor < target_stop:
        raw = "".join(
            iter_middle_window(
                seed, raw_cursor, raw_window_characters,
                chunk_characters=raw_window_characters,
            )
        )
        if len(raw) != raw_window_characters:
            raise RuntimeError("raw TardiSHA continuation window ended unexpectedly")
        raw_cursor += raw_window_characters
        buffered += state.feed(raw)

        if visible_cursor + len(buffered) <= start_coordinate:
            visible_cursor += len(buffered)
            buffered = ""
            continue

        if visible_cursor < start_coordinate:
            skip = start_coordinate - visible_cursor
            buffered = buffered[skip:]
            visible_cursor = start_coordinate

        while buffered and visible_cursor < target_stop:
            take = min(chunk_characters, target_stop - visible_cursor, len(buffered))
            piece = buffered[:take]
            buffered = buffered[take:]
            visible_cursor += len(piece)
            yield piece


def regia_window(seed: bytes, start_coordinate: int, span_length: int) -> str:
    """Materialize one corrected visible coordinate window."""
    return "".join(iter_regia_window(seed, start_coordinate, span_length))

def regia_middle(seed: bytes, middle_length: int) -> str:
    """Materialize exactly ``middle_length`` corrected visible glyphs.

    Phase 5 makes visible extent a hard contract: Regia repairs may consume any
    additional raw coordinates required, but they may never shorten or lengthen the
    caller-declared visible middle.
    """
    from .hashing import validate_middle_length

    width = validate_middle_length(middle_length)
    corrected = "".join(iter_regia_middle(seed, width))
    if len(corrected) != width:
        raise RuntimeError(
            f"Regia visible extent mismatch: produced {len(corrected)} glyphs; expected {width}"
        )
    return corrected


# Closure guards: trigger and deletion sets are intentionally different.
if _GENERATED_ENOCH_SET != frozenset({"𝔓", "ཪ", "☍", "⚶", "߷", "🜚", "🜛", "🜕", "🜗", "🜔", "🜖"}):
    raise RuntimeError("Regia deletion set must be all eleven generated Enochs")
if FORM_GLYPH != "🜔":
    raise RuntimeError("Regia repair scar must be the canonical Q0/Form glyph")
