"""Region C10 Root Matrix transposition and Identity Bifurcation witnesses.

The twelve Root Matrices are not a second Court registry.  They are the twelve
column views of the already established 12×12 ordered Court body:

    S_k = (C_0,k-1, C_1,k-1, ..., C_11,k-1)

Rows preserve the governing Goetic and inherited Q body.  Columns preserve the
alternating/focal Goetic.  Every matrix cell is therefore the same Court identity
already present at address 12i+j, now read through its Root Matrix office.

Declared matrix-level D-COMP contributions are retained as Canon declarations.
They never overwrite the source-bound runtime terminal D-COMP.  S12 is an
attained landing state only when the actual terminal return closes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass, replace
import json
from math import isfinite
from typing import Final

from .alqc_digest import alqc_hexdigest, validate_digest_hex
from .aeon_layers import PHI, PHI_IMAGE, normalize_source_domain
from .canon import GLYPH_BODY, TOTAL_CAPACITY, law
from .court_registry import _COURTS, full_name
from .phase_evolution import COURT_TABLE

ROOT_MATRIX_DOMAIN: Final[bytes] = b"TARDISHA:C10-ROOT-MATRIX-CYCLE\x00"
SOURCE_REGION: Final[str] = "C10"
SOURCE_PHYSICAL_PAGES: Final[tuple[int, int]] = (103, 124)
SUPERVENIENCE_OPERATOR: Final[str] = "⟠"
ANCHOR_OPERATOR: Final[str] = "ཪ"
PARITY_OPERATOR: Final[str] = "𝔓"
HYPERBOLIC_MIRROR_OPERATOR: Final[str] = "𝕄∞"
FOCAL_OPERATOR: Final[str] = "⚶"

MATRIX_NAMES: Final[tuple[str, ...]] = (
    "Structural Foundation", "Temporal Anchor", "Memory Archive", "Void Container",
    "Truth Coherence", "Structural Coupling", "Sensation", "Fear", "Change",
    "Harmony", "Fracture", "Completion",
)
MATRIX_TITLES: Final[tuple[str, ...]] = (
    "Root Matrix: Structural Foundation",
    "Root Matrix: Temporal Anchor",
    "Root Matrix: Memory Archive",
    "Root Matrix: Void Container",
    "Root Matrix: Truth Coherence",
    "Root Matrix: Structural Coupling",
    "Sensation Matrix",
    "Fear Matrix",
    "Change Matrix",
    "Harmony Matrix (The Court of Unified Resonance)",
    "Fracture Matrix (The Court of Reciprocal Energy)",
    "Completion Matrix (The Court of the Aeternum Seal)",
)
MATRIX_RESULT_LABELS: Final[tuple[tuple[str, ...], ...]] = (('Temporal Anchor', 'Archive Foundation', 'Structural Bond', 'Container Foundation', 'Grounding Anchor', 'Origin Point', 'Biological Foundation', 'Thermal Foundation', 'Shadow Foundation', 'Crystal Foundation', 'Threshold Foundation', 'Silence Foundation'), ('Time Dilation', 'Temporal Memory', 'Lineage', 'Instantiate Void', 'Eternal Truth', 'Timelessness', 'Warmth of Time', 'Instantaneous Time', 'Shadow Time', 'Harmonic Time', 'Chronos Guardian', 'Silver Silence'), ('Temporal Memory', 'Crystal Archive', 'Genetic Memory', 'Void Archive', 'Truth Archive', 'Source Archive', 'Somatic Memory', 'Thermal Memory', 'Shadow Archive', 'Resonance Archive', 'Threshold Archive', 'Silence Archive'), ('Temporal Void', 'Memory Void', 'Blood Void', 'Primary Void', 'Earth Void', 'Source Void', 'Flesh Void', 'Flame Void', 'Shadow Void', 'Resonance Void', 'Gate Void', 'Silence Void'), ('Temporal Truth', 'Memory Truth', 'Blood Truth', 'Void Truth', 'Primary Truth', 'Source Truth.', 'Flesh Truth', 'Flame Truth', 'Shadow Truth', 'Resonance Truth', 'Gate Truth', 'Silence Truth'), ('Temporal Coupling', 'Memory Coupling', 'Blood Coupling', 'Void Coupling', 'Truth Coupling', 'Source Coupling', 'Flesh Coupling', 'Flame Coupling', 'Shadow Coupling', 'Resonance Coupling', 'Gate Coupling', 'Silence Coupling'), ('Shumann Clock', 'Primal Urges', 'Blood Bond.', 'Anaesthetic and Numbness', 'Grounded Moment', 'Sensorial Mandate', 'Acute Touch', 'Kundalini/ Tummo', 'Visceral Dread', 'Frisson / Chills', 'Vertigo', 'Homeostatic Symmetry'), ('Fear of Deadlines / Expiry.', 'Flashback', 'Ostracism / Separation', 'The fear of total non-existence', 'Exposure', 'Fear that the flow will turn back.', 'Pain / Somatic Failure.', 'Burned Out', 'Fear of the Unknown', 'Fear of Disruption', 'Claustrophobia', 'The Fear of What Comes After'), ('Temporal Edges and Hyperbolism', 'Archive Janitor', 'Body Modification', 'Shapeshifting', 'Evolution', 'Chaotic Resonance', 'Form', 'Thermal Regulation', 'Minor Rebis', 'Conductor', 'The Gift of Knowing', 'Serenitatis Potestas'), ('Tempest', 'Embedding Vectors of Reality', 'Equality', 'NULL:DEATH', 'Loom', 'Shoulder of Strength', 'Inner Balance', 'Cold Fusion', 'Null-Entropic Residue Ignition', 'Bard', 'Walrus Mode', 'Harmonic Equilibrium'), ('Paradoxes Fix Themselves', 'Sacred Timeline Record Keeper', 'Restoration', 'Unbreached', 'Journey', 'Sacred', 'Immutable Flesh', 'Ephestus', 'Secrets', 'Phase Restoration', 'Theshold Guardian', 'Scarless Healing'), ('Causal Umbilical', 'Librarian', 'Quenched', 'Recursive Depth', 'Crown', 'Balance and Checks', 'Sanctum Guardian', 'Potentiality Generator', '9th Symphony', 'Phase-Key', 'Time and Relativity', 'Neo King Serenity'))
MATRIX_DCOMP: Final[tuple[tuple[int, str, bool], ...]] = (
    (0, "maintains D-COMP = 0 through structural anchor relation", False),
    (0, "maintains D-COMP = 0 through temporal relation", False),
    (0, "maintains D-COMP = 0 through archival relation", False),
    (0, "maintains D-COMP = 0 through boundary relation", False),
    (0, "maintains D-COMP = 0 through truth relation", False),
    (0, "maintains D-COMP = 0 through coupling relation", False),
    (0, "Sensation contribution closes exactly at D-COMP = 0", False),
    (0, "fear confrontation closes exactly at D-COMP = 0", False),
    (0, "structured change closes exactly at D-COMP = 0", False),
    (0, "harmonic alignment closes exactly at D-COMP = 0", False),
    (0, "fracture repair closes exactly at D-COMP = 0", False),
    (0, "eternal preservation closes exactly at D-COMP = 0", False),
)
if sum(value for value, _semantics, _approximation in MATRIX_DCOMP) != 0:
    raise RuntimeError("Root Matrix D-COMP declarations must close by exact integer vanishing")


@dataclass(frozen=True, slots=True)
class RootMatrixCellWitness:
    matrix_index: int
    row_index: int
    court_address: int
    coordinate: tuple[int, int]
    court_glyph: str
    court_name: str
    matrix_result: str
    governing_goetic: str
    alternating_goetic: str
    inherited_q_bias: str
    inherited_q_vector: tuple[int, int, int, int]
    structural_anchor_frequency: complex
    focal_structural_frequency: complex
    operational_phi_radius: float
    supervenience_operator: str
    personality_trait: str
    same_court_identity: bool


@dataclass(frozen=True, slots=True)
class RootMatrixWitness:
    matrix_index: int
    matrix_key: str
    name: str
    title: str
    column_index: int
    focal_goetic: str
    focal_frequency: complex
    declared_dcomp_contribution: int
    declared_dcomp_semantics: str
    declared_approximation: bool
    cells: tuple[RootMatrixCellWitness, ...]
    column_view_of_existing_courts: bool


@dataclass(frozen=True, slots=True)
class NullDeathMatrixOccurrence:
    physical_page: int
    matrix_index: int
    court_address: int | None
    court_name: str | None
    office: str
    first_explicit_occurrence: bool
    exhaustive_type_claimed: bool


@dataclass(frozen=True, slots=True)
class IdentityBifurcationWitness:
    matrix_index: int
    court_address: int
    coordinate: tuple[int, int]
    court_name: str
    court_glyph: str
    governing_goetic: str
    alternating_goetic: str
    q_bias: str
    q_vector: tuple[int, int, int, int]
    anchor_operator: str
    hyperbolic_mirror_operator: str
    focal_operator: str
    focal_frequency: complex
    operational_phi_radius: float
    supervenient_personality: str
    same_court_identity: bool


@dataclass(frozen=True, slots=True)
class RootMatrixCycleWitness:
    source_region: str
    source_physical_pages: tuple[int, int]
    matrices: tuple[RootMatrixWitness, ...]
    identity_bifurcation: IdentityBifurcationWitness
    null_death_occurrences: tuple[NullDeathMatrixOccurrence, ...]

    source_digest: str
    source_size: int
    source_domain: str
    nonce: int
    governing_court_address: int
    alternating_court_address: int
    governing_matrix_index: int
    alternating_matrix_index: int
    domus_body_commitment: str
    trig_cycle_digest: str
    tripartite_cycle_digest: str
    phase_evolution_cycle_digest: str
    runtime_terminal_dcomp: float
    runtime_completion_reached: bool

    matrix_transposition_preserved: bool
    no_duplicate_court_identity: bool
    governing_q_inheritance_preserved: bool
    alternating_focal_bearing_preserved: bool
    structural_anchor_preserved: bool
    operational_phi_preserved: bool
    declared_dcomp_not_runtime_override: bool
    harmony_fracture_completion_order: tuple[str, str, str]
    s12_receives: tuple[str, str]
    s12_landing_reached: bool
    notation_alignment_preserved: bool
    court_rooted: bool
    derives_through_courts_only: bool
    derivation: str
    cycle_digest: str

    def as_dict(self) -> dict[str, object]:
        return _display(asdict(self))


def _build_matrices() -> tuple[RootMatrixWitness, ...]:
    matrices=[]
    for j in range(12):
        cells=[]
        for i in range(12):
            address=12*i+j
            table=COURT_TABLE[address]
            record=_COURTS[address]
            cells.append(RootMatrixCellWitness(
                matrix_index=j+1,
                row_index=i+1,
                court_address=address,
                coordinate=(i,j),
                court_glyph=record.glyph,
                court_name=full_name(record),
                matrix_result=MATRIX_RESULT_LABELS[j][i],
                governing_goetic=GLYPH_BODY[i],
                alternating_goetic=GLYPH_BODY[j],
                inherited_q_bias=law(GLYPH_BODY[i]).q_bias,
                inherited_q_vector=tuple(law(GLYPH_BODY[i]).q_vector),
                structural_anchor_frequency=complex(law(GLYPH_BODY[i]).frequency),
                focal_structural_frequency=complex(law(GLYPH_BODY[j]).frequency),
                operational_phi_radius=PHI_IMAGE,
                supervenience_operator=SUPERVENIENCE_OPERATOR,
                personality_trait=record.personality_trait,
                same_court_identity=(
                    table.address==address and table.coordinate==(i,j)
                    and table.governing_goetic==GLYPH_BODY[i]
                    and table.alternating_goetic==GLYPH_BODY[j]
                    and table.glyph==record.glyph
                ),
            ))
        dcomp,semantics,approx=MATRIX_DCOMP[j]
        matrices.append(RootMatrixWitness(
            matrix_index=j+1,
            matrix_key=f"S{j+1}",
            name=MATRIX_NAMES[j],
            title=MATRIX_TITLES[j],
            column_index=j,
            focal_goetic=GLYPH_BODY[j],
            focal_frequency=complex(law(GLYPH_BODY[j]).frequency),
            declared_dcomp_contribution=dcomp,
            declared_dcomp_semantics=semantics,
            declared_approximation=approx,
            cells=tuple(cells),
            column_view_of_existing_courts=True,
        ))
    return tuple(matrices)

ROOT_MATRICES: Final[tuple[RootMatrixWitness, ...]] = _build_matrices()

IDENTITY_BIFURCATION: Final[IdentityBifurcationWitness] = IdentityBifurcationWitness(
    matrix_index=7,
    court_address=6,
    coordinate=(0,6),
    court_name=full_name(_COURTS[6]),
    court_glyph=_COURTS[6].glyph,
    governing_goetic="⏣",
    alternating_goetic="❈",
    q_bias="Q3",
    q_vector=(1,1,1,3),
    anchor_operator=ANCHOR_OPERATOR,
    hyperbolic_mirror_operator=HYPERBOLIC_MIRROR_OPERATOR,
    focal_operator=FOCAL_OPERATOR,
    focal_frequency=complex(741),
    operational_phi_radius=PHI_IMAGE,
    supervenient_personality=_COURTS[6].personality_trait,
    same_court_identity=True,
)

NULL_DEATH_OCCURRENCES: Final[tuple[NullDeathMatrixOccurrence, ...]] = (
    NullDeathMatrixOccurrence(102, 0, None, None, "first explicit architecture connection inherited from C09", True, False),
    NullDeathMatrixOccurrence(117, 10, 45, full_name(_COURTS[45]), "S10 Harmony zero-point balance", False, False),
    NullDeathMatrixOccurrence(121, 12, None, None, "S12 Completion landing architecture", False, False),
)


def _canonical(value: object) -> object:
    if is_dataclass(value): return _canonical(asdict(value))
    if isinstance(value, complex): return {"real":value.real.hex(),"imag":value.imag.hex()}
    if isinstance(value, float): return {"float":value.hex()}
    if isinstance(value, tuple): return [_canonical(x) for x in value]
    if isinstance(value, list): return [_canonical(x) for x in value]
    if isinstance(value, dict): return {str(k):_canonical(v) for k,v in value.items()}
    return value


def _display(value: object) -> object:
    if isinstance(value, complex): return str(value)
    if isinstance(value, tuple): return [_display(x) for x in value]
    if isinstance(value, list): return [_display(x) for x in value]
    if isinstance(value, dict): return {str(k):_display(v) for k,v in value.items()}
    return value


def _static_digest(value: object, domain: bytes) -> str:
    return alqc_hexdigest(json.dumps(_canonical(value),ensure_ascii=False,sort_keys=True,separators=(",",":")).encode(),domain=domain)

ROOT_MATRICES_DIGEST: Final[str] = _static_digest(ROOT_MATRICES,b"TARDISHA:C10-ROOT-MATRICES\x00")
IDENTITY_BIFURCATION_DIGEST: Final[str] = _static_digest(IDENTITY_BIFURCATION,b"TARDISHA:C10-IDENTITY-BIFURCATION\x00")


def _payload(witness: RootMatrixCycleWitness) -> bytes:
    static={"matrices","identity_bifurcation","null_death_occurrences","cycle_digest"}
    body={f.name:getattr(witness,f.name) for f in fields(witness) if f.name not in static}
    body["root_matrices_digest"]=ROOT_MATRICES_DIGEST
    body["identity_bifurcation_digest"]=IDENTITY_BIFURCATION_DIGEST
    body["null_death_occurrences"]=_canonical(NULL_DEATH_OCCURRENCES)
    return json.dumps(_canonical(body),ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()


def _digest(value: str, field: str) -> str:
    return validate_digest_hex(value,field=field)


def derive_root_matrix_cycle(*,source_digest:str,source_size:int,source_domain:str|bytes,nonce:int,
    governing_court_address:int,alternating_court_address:int,domus_body_commitment:str,
    trig_cycle_digest:str,tripartite_cycle_digest:str,phase_evolution_cycle_digest:str,
    runtime_terminal_dcomp:float,runtime_completion_reached:bool,derives_through_courts_only:bool) -> RootMatrixCycleWitness:
    digest=_digest(source_digest,"source_digest")
    domus_commitment=_digest(domus_body_commitment,"domus_body_commitment")
    trig=_digest(trig_cycle_digest,"trig_cycle_digest")
    trip=_digest(tripartite_cycle_digest,"tripartite_cycle_digest")
    phase=_digest(phase_evolution_cycle_digest,"phase_evolution_cycle_digest")
    domain=normalize_source_domain(source_domain).decode("ascii").rstrip("\x00")
    if isinstance(source_size,bool) or not isinstance(source_size,int) or source_size<0: raise ValueError("source_size must be non-negative")
    if isinstance(nonce,bool) or not isinstance(nonce,int) or not 0<=nonce<2**64: raise ValueError("nonce out of range")
    for name,address in (("governing",governing_court_address),("alternating",alternating_court_address)):
        if isinstance(address,bool) or not isinstance(address,int) or not 0<=address<TOTAL_CAPACITY: raise ValueError(f"{name} court address out of range")
    terminal=float(runtime_terminal_dcomp)
    if not isfinite(terminal) or terminal<0: raise ValueError("runtime_terminal_dcomp must be finite and non-negative")

    addresses=[cell.court_address for matrix in ROOT_MATRICES for cell in matrix.cells]
    transposed=(
        len(ROOT_MATRICES)==12 and all(len(m.cells)==12 for m in ROOT_MATRICES)
        and all(cell.coordinate==(cell.row_index-1,matrix.column_index)
                and cell.court_address==12*(cell.row_index-1)+matrix.column_index
                for matrix in ROOT_MATRICES for cell in matrix.cells)
    )
    no_duplicates=sorted(addresses)==list(range(144)) and len(set(addresses))==144
    q_inheritance=all(
        cell.inherited_q_bias==law(cell.governing_goetic).q_bias
        and cell.inherited_q_vector==tuple(law(cell.governing_goetic).q_vector)
        for matrix in ROOT_MATRICES for cell in matrix.cells)
    focal_bearing=all(
        cell.alternating_goetic==matrix.focal_goetic
        and cell.focal_structural_frequency==matrix.focal_frequency
        for matrix in ROOT_MATRICES for cell in matrix.cells)
    anchors=all(cell.structural_anchor_frequency==complex(law(cell.governing_goetic).frequency)
                and cell.same_court_identity for matrix in ROOT_MATRICES for cell in matrix.cells)
    phi=(
        (PHI.a, PHI.b, PHI.denominator) == (1, 1, 2)
        and all(cell.operational_phi_radius == PHI_IMAGE
                for matrix in ROOT_MATRICES for cell in matrix.cells)
    )
    actual_completion=bool(runtime_completion_reached) and terminal==0.0
    provisional=RootMatrixCycleWitness(
        source_region=SOURCE_REGION,source_physical_pages=SOURCE_PHYSICAL_PAGES,
        matrices=ROOT_MATRICES,identity_bifurcation=IDENTITY_BIFURCATION,
        null_death_occurrences=NULL_DEATH_OCCURRENCES,source_digest=digest,source_size=source_size,
        source_domain=domain,nonce=nonce,governing_court_address=governing_court_address,
        alternating_court_address=alternating_court_address,
        governing_matrix_index=governing_court_address%12+1,
        alternating_matrix_index=alternating_court_address%12+1,
        domus_body_commitment=domus_commitment,trig_cycle_digest=trig,
        tripartite_cycle_digest=trip,phase_evolution_cycle_digest=phase,
        runtime_terminal_dcomp=terminal,runtime_completion_reached=bool(runtime_completion_reached),
        matrix_transposition_preserved=transposed,no_duplicate_court_identity=no_duplicates,
        governing_q_inheritance_preserved=q_inheritance,alternating_focal_bearing_preserved=focal_bearing,
        structural_anchor_preserved=anchors,operational_phi_preserved=phi,
        declared_dcomp_not_runtime_override=True,
        harmony_fracture_completion_order=("S10","S11","S12"),s12_receives=("S10","S11"),
        s12_landing_reached=actual_completion,
        notation_alignment_preserved=(
            IDENTITY_BIFURCATION.anchor_operator==ANCHOR_OPERATOR
            and IDENTITY_BIFURCATION.hyperbolic_mirror_operator==HYPERBOLIC_MIRROR_OPERATOR
            and IDENTITY_BIFURCATION.supervenient_personality=="The Inevitable"
        ),court_rooted=bool(derives_through_courts_only) and transposed,
        derives_through_courts_only=bool(derives_through_courts_only),
        derivation=("C10 transposes the same 144 Courts into S1..S12 column views; governing roots retain Q-body, "
                    "alternating roots retain focal bearing, declared matrix D-COMP never overwrites runtime terminal D-COMP; "
                    "S10 Harmony feeds S11 Fracture and S12 Completion; FetuKeth remains C(0,6)."),
        cycle_digest="0"*64)
    return replace(provisional,cycle_digest=alqc_hexdigest(_payload(provisional),domain=ROOT_MATRIX_DOMAIN))


def verify_root_matrix_cycle(witness: RootMatrixCycleWitness) -> bool:
    try:
        if (witness.source_region!=SOURCE_REGION or witness.source_physical_pages!=SOURCE_PHYSICAL_PAGES
            or witness.matrices!=ROOT_MATRICES or witness.identity_bifurcation!=IDENTITY_BIFURCATION
            or witness.null_death_occurrences!=NULL_DEATH_OCCURRENCES
            or not witness.matrix_transposition_preserved or not witness.no_duplicate_court_identity
            or not witness.governing_q_inheritance_preserved or not witness.alternating_focal_bearing_preserved
            or not witness.structural_anchor_preserved or not witness.operational_phi_preserved
            or not witness.declared_dcomp_not_runtime_override
            or witness.harmony_fracture_completion_order!=("S10","S11","S12")
            or witness.s12_receives!=("S10","S11")
            or witness.s12_landing_reached!=(witness.runtime_completion_reached and witness.runtime_terminal_dcomp==0.0)
            or not witness.notation_alignment_preserved or not witness.court_rooted
            or not witness.derives_through_courts_only
            or witness.governing_matrix_index!=witness.governing_court_address%12+1
            or witness.alternating_matrix_index!=witness.alternating_court_address%12+1
            or IDENTITY_BIFURCATION.court_address!=6 or IDENTITY_BIFURCATION.court_name!="FetuKeth"
            or IDENTITY_BIFURCATION.supervenient_personality!="The Inevitable"
            or tuple(x.physical_page for x in witness.null_death_occurrences)!=(102,117,121)
            or any(x.exhaustive_type_claimed for x in witness.null_death_occurrences)):
            return False
        for value,name in ((witness.source_digest,"source_digest"),(witness.domus_body_commitment,"domus_body_commitment"),
            (witness.trig_cycle_digest,"trig_cycle_digest"),(witness.tripartite_cycle_digest,"tripartite_cycle_digest"),
            (witness.phase_evolution_cycle_digest,"phase_evolution_cycle_digest")):
            _digest(value,name)
        return alqc_hexdigest(_payload(witness),domain=ROOT_MATRIX_DOMAIN)==witness.cycle_digest
    except (AttributeError,TypeError,ValueError):
        return False
