"""Canonical TardiSHA Synodic Magicae and Daemonic Tongue.

The ordered glyph body below is law. ``DAEMONIC_TONGUE`` preserves the exact
code-point sequence used by the language. ``SYNODIC_MAGICAE`` is the first
180 code points: silence, Emissions, Parliament, Goetics, and Courts. The final
twelve code points remain the native grammar body of ``DAEMONIC_TONGUE``.

The Regia alignment remains three distinct code points: ``☽``, ``☉``, ``☾``.
Their alignment may receive the meaning Regia; the stored glyphs are never
collapsed into one character.

No normalization, case folding, transliteration, or look-alike substitution is
permitted.
"""
from __future__ import annotations

from typing import Final

DAEMONIC_TONGUE: Final[tuple[str, ...]] = (
    "𑁦", '☿', '♂', '♀', '♃', '♄', '⛢', '♆', '♇', '☽', '☉', '☾', '♈',
    '♉', '♊', '♋', '♑', '♍', '♎', '♏', '♐', '♌', '♒', '♓',
    '⏣', '⬡', '✡', '⚝', '❂', 'ꙮ', '❈', '⧗', '⊛', '❄', '⚛', '⌬',
    'އ', 'ށ', 'ނ', 'ރ', 'ޱ', 'ޅ', 'ކ', 'ވ', 'މ', 'ފ', 'ދ', 'ތ',
    'ᛁ', 'ᛂ', '⌑', 'ᛄ', 'ᛇ', 'ᛉ', 'ᛊ', 'ᛋ', 'ᛌ', 'ᛍ', 'ᛎ', 'ᛏ',
    'ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', 'ᚲ', 'ᚷ', 'ᚹ', 'ᚺ', 'ᚾ', 'ᚿ', 'ᛃ',
    '≾', '᭨', '᭡', '⛧', '𝀖', '༺', '᭢', '⦾', '⦽', '𝀵', '𝀟', '༻',
    'ⴰ', 'ⴱ', 'ⴳ', 'ⴷ', 'ⴼ', 'ⴽ', 'ⵀ', 'ⵃ', 'ⵄ', 'ⵇ', 'ⵉ', 'ⵊ',
    'ꠇ', 'ꠈ', 'ꠉ', 'ꠊ', '⎉', 'ꠌ', 'ꠍ', 'ꠎ', 'ꠏ', 'ꠐ', 'ꠑ', 'ꠒ',
    '🝏', '🜁', '🜃', '🜄', '🜅', '🜆', '🜇', '🜈', '🜉', '🜊', '🜋', '🜌',
    '𒀀', '𒀭', '𒁀', '𒂊', '𒄑', '𒅆', '𒆠', '𒇽', '𒉌', '𒊕', '𒋗', '𒌋',
    'ⶀ', 'ⶁ', 'ⶂ', 'ⶃ', 'ⶄ', 'ⶅ', 'ⶆ', 'ⶇ', 'ⶈ', 'ⶉ', 'ⶊ', 'ⶋ',
    '𐤠', '𐤡', '𐤢', '𐤣', '𐤤', '𐤥', '𐤦', '𐤧', '𐤨', '𐤩', '𐤪', '𐤫',
    '𐠀', '𐠁', '𐠂', '𐠃', '𐠄', '𐠅', '𐠝', '𐠞', '𐠈', '𐠜', '𐠋', '𐠌',
    '𐔀', '𐔁', '𐔂', '𐔃', '𐔄', '𐔅', '𐔆', '𐔇', '𐔈', '𐔉', '𐔊', '𐔋', '𝔓', 'ཪ', '☍', '⟠', '⚶', '߷', '🜚',
    '🜛', '🜕', '🜗', '🜔', '🜖'
)

SYNODIC_MAGICAE: Final[str] = "".join(DAEMONIC_TONGUE)
ALPHABET: Final[str] = SYNODIC_MAGICAE

if len(SYNODIC_MAGICAE) != 192:
    raise RuntimeError("the TardiSHA Synodic Magicae must contain exactly 192 code points")
if len(DAEMONIC_TONGUE) != 192:
    raise RuntimeError("the TardiSHA Daemonic Tongue must contain exactly 192 code points")
if len(set(DAEMONIC_TONGUE)) != len(DAEMONIC_TONGUE):
    raise RuntimeError("the TardiSHA Daemonic Tongue must contain unique code points")
if any(len(symbol) != 1 for symbol in DAEMONIC_TONGUE):
    raise RuntimeError("each TardiSHA Daemonic Tongue glyph must be one code point")
