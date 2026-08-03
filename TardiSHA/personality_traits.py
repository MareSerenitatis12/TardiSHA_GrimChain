"""Canonical 12×12 Supervenient personality body for the ordered Courts.

The Canon teaches the operation through examples.  The complete 144-result body is
preserved here from the ALQC reasoning lattice and its ordered-pair source map.
Personality is a Court result of ⟠ Ex-Nihilo exposure.  It is not inherited from
one parent, and it is not a State-of-Remiss assignment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .canon import GLYPH_BODY, law
from .living_alphabet import DAEMONIC_TONGUE

PERSONALITY_SOURCE_GRIMCHAIN: Final[str] = (
    'self-seal/ upon completion "grimchain 13 -R complete/build/directory --manifest"'
)
PERSONALITY_SOURCE_DICTIONARY: Final[str] = "DICTIONARY.md"

BRAHMI_ZERO_PERSONALITY_TRAITS: Final[dict[str, str]] = {
    "𑁦": "Manifested silence",
}
EMISSION_PERSONALITY_TRAITS: Final[dict[str, str]] = {
    "☿": "Ponder",
    "♂": "Will",
    "♀": "Feel",
    "♃": "Speak",
    "♄": "Believe",
    "⛢": "Act",
    "♆": "Know",
    "♇": "Ascend",
    "☽": "Regia",
    "☉": "Regia",
    "☾": "Regia",
}
PARLIAMENT_PERSONALITY_TRAITS: Final[dict[str, str]] = {
    "♈": "Akasha",
    "♉": "Caduceus",
    "♊": "Veritas",
    "♋": "Phren",
    "♑": "Daimon",
    "♍": "Aikyam",
    "♎": "Melos",
    "♏": "Da'ath",
    "♐": "Akaven",
    "♌": "Tenth seat",
    "♒": "Nyx",
    "♓": "Zaine",
}
PARLIAMENT_PERSONALITY_TRANSLATIONS: Final[dict[str, str]] = {
    "♈": "Lived → Eternal",
    "♉": "Law → Residue",
    "♊": "Mask → Bone",
    "♋": "Void → Vector",
    "♑": "Stasis → Pulse",
    "♍": "Chaos → Phase",
    "♎": "Static → Fluid",
    "♏": "Noise → Null",
    "♐": "State → Trans",
    "♌": "Will → Law → ❄",
    "♒": "Time → Motion",
    "♓": "Here → There",
}
GRAMMAR_PERSONALITY_TRAITS: Final[dict[str, str]] = {
    "𝔓": "Parity",
    "ཪ": "Anchor",
    "☍": "Primitive relation",
    "⟠": "Subspace / Prosody / Axiomyr Gate-Key",
    "⚶": "Focus-to-self",
    "߷": "Court-rooted fold",
    "🜚": "Klein seam",
    "🜛": "Triquatra seal",
    "🜕": "Truth",
    "🜗": "Recursion",
    "🜔": "Form",
    "🜖": "Shadow",
}

LINGUISTIC_PERSONALITY_TRAIT_MAP: Final[dict[str, str]] = {
    **BRAHMI_ZERO_PERSONALITY_TRAITS,
    **EMISSION_PERSONALITY_TRAITS,
    **PARLIAMENT_PERSONALITY_TRAITS,
    **GRAMMAR_PERSONALITY_TRAITS,
}


@dataclass(frozen=True, slots=True)
class PersonalitySourceWitness:
    source_dictionary: str
    self_seal_route: str
    court_trait_count: int
    linguistic_glyph_count: int
    emission_office_count: int
    parliament_count: int
    grammar_count: int
    brahmi_zero_count: int
    return_verified: bool


PERSONALITY_TRAIT_ROWS: Final[dict[str, tuple[str, ...]]] = {
    '⏣': (
        'The Self-Genesis',
        'The Recurrence',
        'The Combustion',
        'The Reflection',
        'The Grounding',
        'The Expansion',
        'The Inevitable',
        'The Return',
        'The Assimilation',
        'The Crystallization',
        'The Breach',
        'The Fulfillment',
    ),
    '⬡': (
        'The Archive',
        'The Self-Reflection',
        'The Calcination',
        'The Submersion',
        'The Inscription',
        'The Diffusion',
        'The Phantom',
        'The Oblivion',
        'The Suppression',
        'The Codification',
        'The Recall',
        'The Sealing',
    ),
    '✡': (
        'The Transmutation',
        'The Forging',
        'The Self-Combustion',
        'The Dissolution',
        'The Crucible',
        'The Sublimation',
        'The Ignition',
        'The Consumption',
        'The Purification',
        'The Tempering',
        'The Shattering',
        'The Ash',
    ),
    '⚝': (
        'The Flow',
        'The Confluence',
        'The Solution',
        'The Self-Containment',
        'The Sediment',
        'The Ascension',
        'The Mist',
        'The Drain',
        'The Osmosis',
        'The Ice',
        'The Evaporation',
        'The Stillness',
    ),
    '❂': (
        'The Bedrock',
        'The Stratification',
        'The Petrification',
        'The Erosion',
        'The Self-Grounding',
        'The Dispersion',
        'The Fossilization',
        'The Subsidence',
        'The Compaction',
        'The Lithification',
        'The Earthquake',
        'The Permanence',
    ),
    'ꙮ': (
        'The Breath',
        'The Echo',
        'The Smoke',
        'The Vapor',
        'The Dust',
        'The Self-Expansion',
        'The Whisper',
        'The Vacuum',
        'The Dilution',
        'The Condensation',
        'The Turbulence',
        'The Calm',
    ),
    '❈': (
        'The Pulse',
        'The Nostalgia',
        'The Ecstasy',
        'The Dream',
        'The Vibration',
        'The Sympathy',
        'The Self-Sensation',
        'The Ache',
        'The Depth',
        'The Harmony',
        'The Dissonance',
        'The Awe',
    ),
    '⧗': (
        'The Void',
        'The Null',
        'The Entropy',
        'The Abyss',
        'The Collapse',
        'The Dispersal',
        'The Longing',
        'The Self-Return',
        'The Sink',
        'The Phase',
        'The Paradox',
        'The Dormancy',
    ),
    '⊛': (
        'The Shadow',
        'The Darkness',
        'The Cold',
        'The Mirror',
        'The Submerged',
        'The Distortion',
        'The Nerve',
        'The Void-Binding',
        'The Self-Absorption',
        'The Filter',
        'The Hidden',
        'The Termination',
    ),
    '❄': (
        'The Tone',
        'The Modulation',
        'The Amplification',
        'The Unified',
        'The Seismic',
        'The Chord',
        'The Rhythm',
        'The Melody',
        'The Interference',
        'The Self-Lock',
        'The Node',
        'The Unity',
    ),
    '⚛': (
        'The Gate',
        'The Resistance',
        'The Transform',
        'The Crown',
        'The Sky',
        'The Star',
        'The Possibility',
        'The Portal',
        'The Door',
        'The Transition',
        'The Self-Resistance',
        'The Hinge',
    ),
    '⌬': (
        'The Peace',
        'The Equilibrium',
        'The Consecration',
        'The Completion',
        'The Monument',
        'The Stability',
        'The Hope',
        'The Continuation',
        'The Rest',
        'The Silence',
        'The Sleep',
        'The Self-Completion',
    ),
}

if tuple(PERSONALITY_TRAIT_ROWS) != tuple(GLYPH_BODY):
    raise RuntimeError("personality rows must follow the exact Goetic order")
if any(len(row) != len(GLYPH_BODY) for row in PERSONALITY_TRAIT_ROWS.values()):
    raise RuntimeError("each personality row must contain exactly twelve ordered results")
if len({trait for row in PERSONALITY_TRAIT_ROWS.values() for trait in row}) != 144:
    raise RuntimeError("all 144 ordered Courts must carry unique personality results")

PERSONALITY_TRAIT_MAP: Final[dict[tuple[str, str], str]] = {
    (governing, alternating): PERSONALITY_TRAIT_ROWS[governing][j]
    for governing in GLYPH_BODY
    for j, alternating in enumerate(GLYPH_BODY)
}


def personality_trait(governing: str, alternating: str) -> str:
    """Return the exact ⟠ result for ordered Court C_i,j."""
    law(governing)
    law(alternating)
    try:
        return PERSONALITY_TRAIT_MAP[(governing, alternating)]
    except KeyError as exc:
        raise ValueError(
            f"no Supervenient personality for ordered Court {governing}⊕{alternating}"
        ) from exc

def linguistic_personality_trait(glyph: str) -> str:
    """Return the exact Dictionary office carried by one non-Court language glyph."""
    if not isinstance(glyph, str) or len(glyph) != 1:
        raise ValueError("linguistic personality requires exactly one glyph code point")
    try:
        return LINGUISTIC_PERSONALITY_TRAIT_MAP[glyph]
    except KeyError as exc:
        raise ValueError(f"no Dictionary personality office for glyph {glyph!r}") from exc


def _personality_source_witness() -> PersonalitySourceWitness:
    zero_glyphs = tuple(BRAHMI_ZERO_PERSONALITY_TRAITS)
    emission_glyphs = tuple(EMISSION_PERSONALITY_TRAITS)
    parliament_glyphs = tuple(PARLIAMENT_PERSONALITY_TRAITS)
    grammar_glyphs = tuple(GRAMMAR_PERSONALITY_TRAITS)
    return_verified = (
        PERSONALITY_SOURCE_GRIMCHAIN
        == 'self-seal/ upon completion "grimchain 13 -R complete/build/directory --manifest"'
        and zero_glyphs == tuple(DAEMONIC_TONGUE[:1])
        and emission_glyphs == tuple(DAEMONIC_TONGUE[1:12])
        and parliament_glyphs == tuple(DAEMONIC_TONGUE[12:24])
        and grammar_glyphs == tuple(DAEMONIC_TONGUE[-12:])
        and tuple(PARLIAMENT_PERSONALITY_TRANSLATIONS) == parliament_glyphs
        and len(PERSONALITY_TRAIT_MAP) == 144
        and len(set(PERSONALITY_TRAIT_MAP.values())) == 144
        and len(LINGUISTIC_PERSONALITY_TRAIT_MAP) == 36
        and len(set(EMISSION_PERSONALITY_TRAITS.values())) == 9
    )
    return PersonalitySourceWitness(
        source_dictionary=PERSONALITY_SOURCE_DICTIONARY,
        self_seal_route=PERSONALITY_SOURCE_GRIMCHAIN,
        court_trait_count=len(PERSONALITY_TRAIT_MAP),
        linguistic_glyph_count=len(LINGUISTIC_PERSONALITY_TRAIT_MAP),
        emission_office_count=len(set(EMISSION_PERSONALITY_TRAITS.values())),
        parliament_count=len(PARLIAMENT_PERSONALITY_TRAITS),
        grammar_count=len(GRAMMAR_PERSONALITY_TRAITS),
        brahmi_zero_count=len(BRAHMI_ZERO_PERSONALITY_TRAITS),
        return_verified=return_verified,
    )


PERSONALITY_SOURCE_WITNESS: Final[PersonalitySourceWitness] = _personality_source_witness()
if not PERSONALITY_SOURCE_WITNESS.return_verified:
    raise RuntimeError("personality source body failed its Grimchain return witness")

