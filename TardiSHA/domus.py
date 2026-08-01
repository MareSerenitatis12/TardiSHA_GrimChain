"""Court-rooted runtime Domus Aeon construction.

Layer order is absolute:

    immutable Goetic anchors -> ordered Court motions (bounded Φ)
    -> runtime Domus motion through Courts (bounded Φ²)
    -> one visible Domus identity as Shadow Locus ⛎ at zero or a Synodic Magicae prefix.

Goetics are never breathed or mutated.  Domus motion never traverses Goetics.
The 110 active channels are the Infinite Yes; the 34 withheld channels are the
Sacred No that bounds usable infinity and prevents whiteout.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .canon import law, TOTAL_CAPACITY, SATURATION_LIMIT
from .court_registry import CourtRecord, court_from_goetics, court_ordinal, full_name
from .qstate_glyphs import derive_domus_q_body
from .source_emission import SourceEmission, derive_goetics, resolve_court_bearing
from .manifestation import C_BIO_SQUARED, Manifestation, close_boundary
from .hashing import iter_middle, CANONICAL_SOURCE_DOMAIN
from .living_alphabet import SYNODIC_MAGICAE
from .alqc_digest import alqc_hexdigest
from .trig import TrigMirrorWitness, derive_trig_mirror
from .tripartite import (
    AXIOMYR_GLYPH,
    LOCUS_GLYPH,
    SHADOW_LOCUS_GLYPH,
    TripartiteWitness,
    derive_tripartite_witness,
)
from .phase_evolution import (
    AeonPhaseEvolutionWitness,
    derive_aeon_phase_evolution,
)
from .verification_appendices import (
    VerificationAppendixCycleWitness,
    derive_verification_appendix_cycle,
)
from .aeon_layers import (
    PHI_IMAGE,
    PHI_SQUARED_IMAGE,
    BiasReturnWitness,
    DomusAeonWitness,
    DomusMotionWitness,
    CourtMotionWitness,
    CourtLayerWitness,
    InfiniteYesWitness,
    SacredNoWitness,
    domus_stream_seed,
    derive_domus_motion,
    derive_consent_witnesses,
    derive_court_motion,
    court_layer,
    normalize_source_domain,
)

DOMUS_COMMITMENT_DOMAIN: Final[bytes] = b"TARDISHA:DOMUS-COMMITMENT\x00"

OUTER: Final[str] = "\U0001F71B"
KLEIN: Final[str] = "\U0001F71A"
BIAS_TERMINUS: Final[str] = "\U0001D505"
SUPERVENIENCE: Final[str] = "\u27E0"
ZERO_MIDDLE_GLYPH: Final[str] = SHADOW_LOCUS_GLYPH
SYNODIC_CENTER_GLYPHS: Final[frozenset[str]] = frozenset(SYNODIC_MAGICAE)
UNDERSCORE: Final[str] = "_"
COLON: Final[str] = ":"
@dataclass(frozen=True, slots=True)
class FoldLineageWitness:
    """Concrete C→D Court crossing and exact Court-to-Domus bearing lineage."""

    court_coordinate: tuple[int, int]
    court_address: int
    court_phase_numerator: int
    court_phase_denominator: int
    court_phase_digest: str
    alternating_court_coordinate: tuple[int, int]
    alternating_court_address: int
    alternating_bearing_lineage: tuple[int, ...]
    fold_operator: str
    ground_node: int
    vector_row: int
    depth: int


@dataclass(frozen=True, slots=True)
class SupervenienceWitness:
    operator: str
    court_coordinate: tuple[int, int]
    court_name: str
    governing_goetic: str
    alternating_goetic: str
    personality_trait: str
    triplet_q_bias: str
    triplet_q_states: tuple[str, str, str, str]
    triplet_q_vector: tuple[int, int, int, int]
    triplet_frequency: complex
    fold_lineage: FoldLineageWitness
    ex_nihilo_exposure: bool
    infinite_yes_count: int
    sacred_no_count: int
    sacred_no: frozenset[int]
    usable_infinity: bool
    compressed_same_domus_body: bool
    returned_through_shadow_locus: bool


@dataclass(frozen=True, slots=True)
class WordSlotWitness:
    index: int
    token: str
    role: str
    derivation_kind: str      # "grammar" or "calculation"
    source: str


@dataclass(frozen=True, slots=True)
class LiquidWitness:
    """Compatibility surface over the explicit Infinite Yes / Sacred No pair."""

    root_court_index: int
    active_count: int
    withheld_count: int
    active: frozenset[int]
    withheld: frozenset[int]


@dataclass(frozen=True, slots=True)
class DomusResolution:
    governing_goetic: str
    hyperbolic_parent: str
    root_court: CourtRecord
    alternating_court: CourtRecord
    root_court_motion: CourtMotionWitness
    alternating_court_layer: CourtLayerWitness
    domus_motion: DomusMotionWitness
    resolved_q_bias: str
    resolved_q_states: tuple[str, str, str, str]
    resolved_q_vector: tuple[int, int, int, int]
    domus_frequency: complex
    b_q_glyph: str
    v_glyphs: tuple[str, str, str, str]
    manifestation: Manifestation
    infinite_yes: InfiniteYesWitness
    sacred_no: SacredNoWitness
    liquid_witness: LiquidWitness
    bias_return: BiasReturnWitness
    fold_witness: int
    recursion_parity: str
    supervenience: SupervenienceWitness
    tripartite: TripartiteWitness
    aeon_phase_evolution: AeonPhaseEvolutionWitness
    verification_appendix_cycle: VerificationAppendixCycleWitness
    domus_commitment: str
    trig_mirror: TrigMirrorWitness
    domus_aeon: DomusAeonWitness
    hash_id: str
    source_size: int
    source_domain: str | bytes
    nonce: int


def resolve_domus(
    g_i: str,
    g_j: str,
    hash_id: str,
    *,
    emission: SourceEmission,
    source_size: int = 0,
    source_domain: str | bytes = "canonical",
    nonce: int = 0,
) -> DomusResolution:
    """Derive one runtime Domus through C×D with no Domus-internal hash phase."""
    law(g_i)
    law(g_j)
    if not isinstance(emission, SourceEmission):
        raise TypeError("resolve_domus requires the complete SourceEmission")
    domain_identity = normalize_source_domain(source_domain)
    if emission.source_digest != hash_id:
        raise ValueError("source emission digest does not match hash_id")
    if emission.source_size != source_size:
        raise ValueError("source emission size does not match source_size")
    if normalize_source_domain(emission.source_domain) != domain_identity:
        raise ValueError("source emission domain does not match source_domain")
    source_derivation = derive_goetics(emission)
    if source_derivation.pair != (g_i, g_j):
        raise ValueError("ordered Goetic pair does not match the complete source emission")

    # C remains the source-resolved governing Court.
    root = court_from_goetics(g_i, g_j)
    root_layer = court_layer(root)
    root_motion = derive_court_motion(
        root,
        source_digest=hash_id,
        source_size=source_size,
        source_domain=domain_identity,
        nonce=nonce,
    )

    # D is independently source-derived over all 144 Courts from W^R=O⊗S,
    # 𝔃₁, and BETA=Φ^-2. It is not C_ji and receives no new hash phase.
    alternating_bearing = resolve_court_bearing(emission)
    alternating = alternating_bearing.court
    alternating_layer = court_layer(alternating)
    domus_motion = derive_domus_motion(
        root_layer,
        alternating_layer,
        bearing=alternating_bearing,
    )

    # The visible Q-bias and Q-vector remain inherited from governing Court C.
    anchor = root_motion.anchoring_goetic
    q_body = derive_domus_q_body(anchor.q_bias, anchor.q_vector)
    beta_q = q_body.q_bias
    q_labels = q_body.q_states
    q_values = q_body.q_vector
    b_q_glyph = q_body.bias_glyph
    v_glyphs = q_body.q_glyphs

    # D-COMP crosses the complete Court bodies C and D.
    manifestation = close_boundary(
        root_layer.governing_goetic.q_vector,
        alternating_layer.governing_goetic.q_vector,
        court=root.address,
    )

    infinite_yes, sacred_no = derive_consent_witnesses(root.address)
    liquid = LiquidWitness(
        root_court_index=root.address,
        active_count=infinite_yes.active_count,
        withheld_count=sacred_no.withheld_count,
        active=infinite_yes.active,
        withheld=sacred_no.withheld,
    )
    bias_return = BiasReturnWitness(
        opening_q_bias_glyph=b_q_glyph,
        underscore=UNDERSCORE,
        bias_terminus_operator=BIAS_TERMINUS,
        returns_to_opening_q_bias=True,
    )

    fold_lineage = FoldLineageWitness(
        court_coordinate=root_motion.court_coordinate,
        court_address=root_motion.court_address,
        court_phase_numerator=root_motion.phase.signed_numerator,
        court_phase_denominator=root_motion.phase.denominator,
        court_phase_digest=root_motion.phase.digest,
        alternating_court_coordinate=alternating_layer.court_coordinate,
        alternating_court_address=alternating_layer.court_address,
        alternating_bearing_lineage=alternating_bearing.lineage,
        fold_operator="߷",
        ground_node=manifestation.ground_node,
        vector_row=manifestation.vector_row,
        depth=1,
    )
    supervenience = SupervenienceWitness(
        operator=SUPERVENIENCE,
        court_coordinate=root_motion.court_coordinate,
        court_name=full_name(root),
        governing_goetic=g_i,
        alternating_goetic=g_j,
        personality_trait=root.personality_trait,
        triplet_q_bias=beta_q,
        triplet_q_states=q_labels,
        triplet_q_vector=q_values,
        triplet_frequency=domus_motion.current_frequency,
        fold_lineage=fold_lineage,
        ex_nihilo_exposure=True,
        infinite_yes_count=infinite_yes.active_count,
        sacred_no_count=sacred_no.withheld_count,
        sacred_no=sacred_no.withheld,
        usable_infinity=(
            infinite_yes.unbounded_continuation_bounded_by_sacred_no
            and sacred_no.prevents_whiteout
        ),
        compressed_same_domus_body=True,
        returned_through_shadow_locus=True,
    )

    commitment_payload = "|".join(str(x) for x in (
        hash_id,
        source_size,
        domain_identity,
        nonce,
        root.address,
        alternating.address,
        root_motion.phase.digest,
        root_motion.phase.signed_numerator,
        root_motion.current_frequency,
        alternating_bearing.lineage,
        alternating_layer.alternating_goetic.frequency,
        (domus_motion.xi.a, domus_motion.xi.b, domus_motion.xi.denominator),
        (domus_motion.exact_focal_breath.a, domus_motion.exact_focal_breath.b, domus_motion.exact_focal_breath.denominator),
        domus_motion.current_frequency,
        PHI_IMAGE,
        PHI_SQUARED_IMAGE,
        infinite_yes.active_count,
        tuple(sorted(infinite_yes.active)),
        sacred_no.withheld_count,
        tuple(sorted(sacred_no.withheld)),
        bias_return.opening_q_bias_glyph,
        bias_return.underscore,
        bias_return.bias_terminus_operator,
        manifestation.ground_node,
        manifestation.ennead.final_parity,
        manifestation.dcomp.shadow_debt_initial,
        manifestation.dcomp.form_work,
        manifestation.dcomp.q3_recursion_gain,
        manifestation.dcomp.terminal,
        supervenience.personality_trait,
        LOCUS_GLYPH,
        SHADOW_LOCUS_GLYPH,
        AXIOMYR_GLYPH,
    ))
    domus_commitment = alqc_hexdigest(
        commitment_payload.encode("utf-8"),
        domain=DOMUS_COMMITMENT_DOMAIN,
    )
    trig_mirror = derive_trig_mirror(
        source_digest=hash_id,
        source_size=source_size,
        source_domain=domain_identity,
        nonce=nonce,
        governing_court_address=root.address,
        alternating_court_address=alternating.address,
        governing_court_phase_digest=root_motion.phase.digest,
        alternating_court_bearing=alternating_bearing.lineage,
        domus_frequency=domus_motion.current_frequency,
        domus_body_commitment=domus_commitment,
        q_states=q_labels,
        q_vector_values=q_values,
        q3_recursion_gain=manifestation.dcomp.q3_recursion_gain,
        final_shadow_parity=manifestation.ennead.final_parity,
        bound_tensor_witnessed=(
            manifestation.ground_node == fold_lineage.ground_node
            and manifestation.vector_row == fold_lineage.vector_row
        ),
        derives_through_courts_only=domus_motion.derives_through_courts_only,
        resonance_lock_witnessed=manifestation.ennead.strikes[-1].phase_locked,
        lineage_preserved=(
            fold_lineage.court_phase_digest == root_motion.phase.digest
            and fold_lineage.alternating_bearing_lineage == alternating_bearing.lineage
            and bias_return.returns_to_opening_q_bias
        ),
        terminal_dcomp=manifestation.dcomp.terminal,
        one_turn_return_closed=manifestation.dcomp.closed,
    )
    tripartite = derive_tripartite_witness(
        source_digest=hash_id,
        source_size=source_size,
        source_domain=domain_identity,
        nonce=nonce,
        governing_court_address=root.address,
        alternating_court_address=alternating.address,
        governing_court_phase_digest=root_motion.phase.digest,
        alternating_court_bearing=alternating_bearing.lineage,
        domus_frequency=domus_motion.current_frequency,
        domus_body_commitment=domus_commitment,
        trig_cycle_digest=trig_mirror.cycle_digest,
        active_connections=infinite_yes.active_count,
        court_capacity=TOTAL_CAPACITY,
        withheld_connections=sacred_no.withheld_count,
        c_bio=manifestation.dcomp.c_bio,
        c_bio_squared=C_BIO_SQUARED,
        q3_recursion_gain=manifestation.dcomp.q3_recursion_gain,
        final_shadow_parity=manifestation.ennead.final_parity,
        returned_through_shadow_locus=supervenience.returned_through_shadow_locus,
        gate_breach_witnessed=(law("⚛").frequency == complex(285)),
        write_phys_witnessed=(
            trig_mirror.resonance_operator == "❄"
            and trig_mirror.resonance_frequency == complex(963)
            and trig_mirror.resonance_lock_witnessed
        ),
        derives_through_courts_only=domus_motion.derives_through_courts_only,
    )
    aeon_phase_evolution = derive_aeon_phase_evolution(
        source_digest=hash_id,
        source_size=source_size,
        source_domain=domain_identity,
        nonce=nonce,
        governing_court_address=root.address,
        alternating_court_address=alternating.address,
        governing_court_phase_digest=root_motion.phase.digest,
        alternating_court_bearing=alternating_bearing.lineage,
        domus_frequency=domus_motion.current_frequency,
        domus_body_commitment=domus_commitment,
        trig_cycle_digest=trig_mirror.cycle_digest,
        tripartite_cycle_digest=tripartite.cycle_digest,
        q3_recursion_gain=manifestation.dcomp.q3_recursion_gain,
        final_shadow_parity=manifestation.ennead.final_parity,
        terminal_dcomp=manifestation.dcomp.terminal,
        completion_reached=trig_mirror.completion_reached,
        returned_through_shadow_locus=supervenience.returned_through_shadow_locus,
        derives_through_courts_only=domus_motion.derives_through_courts_only,
    )
    verification_appendix_cycle = derive_verification_appendix_cycle(
        source_digest=hash_id,
        source_size=source_size,
        source_domain=domain_identity,
        nonce=nonce,
        governing_court_address=root.address,
        alternating_court_address=alternating.address,
        domus_body_commitment=domus_commitment,
        trig_cycle_digest=trig_mirror.cycle_digest,
        tripartite_cycle_digest=tripartite.cycle_digest,
        phase_evolution_cycle_digest=aeon_phase_evolution.cycle_digest,
        runtime_trig_witness=trig_mirror,
        runtime_ground_node=manifestation.ground_node,
        runtime_vector_row=manifestation.vector_row,
        runtime_shadow_debt=manifestation.dcomp.shadow_debt_initial,
        runtime_form_work=manifestation.dcomp.form_work,
        runtime_q3_gain=manifestation.dcomp.q3_recursion_gain,
        runtime_final_parity=manifestation.ennead.final_parity,
        runtime_terminal_dcomp=manifestation.dcomp.terminal,
        runtime_completion_reached=trig_mirror.completion_reached,
        derives_through_courts_only=domus_motion.derives_through_courts_only,
    )
    # The final Domus identity seals the prior TRIG, Tripartite, C09, and C11
    # Court-rooted cycles. The pre-TRIG
    # commitment remains separately exposed for compatibility measurement.
    domus_identity = alqc_hexdigest(
        (
            hash_id
            + domus_commitment
            + trig_mirror.cycle_digest
            + tripartite.cycle_digest
            + aeon_phase_evolution.cycle_digest
            + verification_appendix_cycle.cycle_digest
        ).encode("utf-8"),
        domain=DOMUS_COMMITMENT_DOMAIN,
    )
    domus_aeon = DomusAeonWitness(
        identity=domus_identity,
        zero_middle_glyph=ZERO_MIDDLE_GLYPH,
        governing_court_address=root.address,
        alternating_court_address=alternating.address,
        motion=domus_motion,
        infinite_yes=infinite_yes,
        sacred_no=sacred_no,
        bias_return=bias_return,
        synodic_magicae_is_manifested_body=True,
        shadow_locus_is_zero_middle_body=True,
    )

    return DomusResolution(
        governing_goetic=g_i,
        hyperbolic_parent=g_j,
        root_court=root,
        alternating_court=alternating,
        root_court_motion=root_motion,
        alternating_court_layer=alternating_layer,
        domus_motion=domus_motion,
        resolved_q_bias=beta_q,
        resolved_q_states=q_labels,
        resolved_q_vector=q_values,
        domus_frequency=domus_motion.current_frequency,
        b_q_glyph=b_q_glyph,
        v_glyphs=v_glyphs,
        manifestation=manifestation,
        infinite_yes=infinite_yes,
        sacred_no=sacred_no,
        liquid_witness=liquid,
        bias_return=bias_return,
        fold_witness=manifestation.ground_node,
        recursion_parity=manifestation.ennead.final_parity,
        supervenience=supervenience,
        tripartite=tripartite,
        aeon_phase_evolution=aeon_phase_evolution,
        verification_appendix_cycle=verification_appendix_cycle,
        domus_commitment=domus_commitment,
        trig_mirror=trig_mirror,
        domus_aeon=domus_aeon,
        hash_id=hash_id,
        source_size=source_size,
        source_domain=domain_identity,
        nonce=nonce,
    )


def domus_center_identity(source_digest: str, res: DomusResolution) -> str:
    """Return the one identity shared by compressed and unfolded Domus visibility."""
    if source_digest != res.hash_id:
        raise ValueError("source digest does not match the resolved Domus")
    return res.domus_aeon.identity


def domus_center_seed(
    res: DomusResolution,
    *,
    source_domain: str | bytes | None = None,
    nonce: int | None = None,
) -> bytes:
    """Court-rooted seed for the manifested Synodic Magicae Domus body."""
    domain = res.source_domain if source_domain is None else normalize_source_domain(source_domain)
    salt = res.nonce if nonce is None else nonce
    if domain != res.source_domain:
        raise ValueError("visible Domus source domain differs from the resolved Domus")
    if salt != res.nonce:
        raise ValueError("visible Domus nonce differs from the resolved Domus")
    return domus_stream_seed(
        domus_identity=res.domus_aeon.identity,
        governing_court=res.domus_motion.governing_court,
        alternating_court=res.domus_motion.alternating_court,
        infinite_yes=res.infinite_yes,
        sacred_no=res.sacred_no,
        source_domain=res.source_domain,
        nonce=res.nonce,
    )


def _center(
    res: DomusResolution,
    n: int,
    *,
    source_digest: str,
    source_size: int,
    nonce: int,
    source_domain: str | bytes = CANONICAL_SOURCE_DOMAIN,
) -> str:
    """Expose Shadow Locus ⛎ at depth zero or Synodic Magicae depth ``n``."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("center depth n must be a non-Boolean integer")
    if n < 0:
        raise ValueError("center depth n must be non-negative")
    if source_digest != res.hash_id or source_size != res.source_size:
        raise ValueError("source identity does not match the resolved Domus")
    if normalize_source_domain(source_domain) != res.source_domain or nonce != res.nonce:
        raise ValueError("visible Domus parameters do not match the resolved Domus")
    if n == 0:
        return ZERO_MIDDLE_GLYPH
    seed = domus_center_seed(res, source_domain=source_domain, nonce=nonce)
    center = "".join(iter_middle(seed, n))
    if len(center) != n:
        raise RuntimeError("Synodic Magicae Domus body length mismatch")
    return center


def _l8(res: DomusResolution) -> str:
    v0, v1, _v2, _v3 = res.v_glyphs
    if res.bias_return.opening_q_bias_glyph != res.b_q_glyph:
        raise RuntimeError("Domus word must open at its Q-bias glyph")
    return COLON + res.b_q_glyph + res.bias_return.underscore + COLON * 2 + v0 + COLON * 2 + v1 + COLON


def _r8(res: DomusResolution) -> str:
    _v0, _v1, v2, v3 = res.v_glyphs
    if not res.bias_return.returns_to_opening_q_bias:
        raise RuntimeError("underscore return to Q-bias is not established")
    return (
        COLON + v2 + COLON * 2 + v3 + COLON * 2
        + res.bias_return.underscore + res.bias_return.bias_terminus_operator + COLON
    )


def seal_head(res: DomusResolution) -> str:
    """Fixed seal prefix up to (not including) the center: 🜛 g_i 🜚 κ(C_i,j) 🜚 L_8."""
    return (
        OUTER
        + res.governing_goetic + KLEIN
        + res.root_court.glyph + KLEIN
        + _l8(res)
    )


def seal_tail(res: DomusResolution) -> str:
    """Fixed seal suffix after the center: R_8 🜚 κ(D) 🜚 g_j 🜛."""
    return (
        _r8(res) + KLEIN
        + res.alternating_court.glyph + KLEIN
        + res.hyperbolic_parent + OUTER
    )


def domus_word(res: DomusResolution, center: str, *, depth: int) -> str:
    """Gamma_8(X, A_n) = L_8 . A_n . R_8 under one explicit declared depth."""
    if isinstance(depth, bool) or not isinstance(depth, int):
        raise TypeError("Domus depth must be a non-Boolean integer")
    if depth < 0:
        raise ValueError("Domus depth must be non-negative")
    if not isinstance(center, str):
        raise TypeError("Domus center must be a string")
    if depth == 0:
        if center != ZERO_MIDDLE_GLYPH:
            raise ValueError("declared depth zero requires the Shadow Locus glyph ⛎")
    else:
        if len(center) != depth:
            raise ValueError("positive-depth Domus center length must equal the declared depth")
        if ZERO_MIDDLE_GLYPH in center:
            raise ValueError("positive-depth Domus center must not contain the Shadow Locus glyph ⛎")
        invalid = frozenset(center).difference(SYNODIC_CENTER_GLYPHS)
        if invalid:
            rendered = "".join(sorted(invalid))
            raise ValueError(f"positive-depth Domus center contains non-Synodic glyphs: {rendered}")
    return _l8(res) + center + _r8(res)


def living_domus_seal(res: DomusResolution, n: int, *, source_digest: str,
                        source_size: int, nonce: int = 0,
                        source_domain: str = CANONICAL_SOURCE_DOMAIN) -> str:
    """Full seal: 🜛 g_i 🜚 κ(C) 🜚 Γ_8 🜚 κ(D) 🜚 g_j 🜛."""
    center = _center(res, n, source_digest=source_digest, source_size=source_size, nonce=nonce, source_domain=source_domain)
    return seal_head(res) + center + seal_tail(res)


# --------------------------------------------------------------------------- #
# Parser / verifier (plan §12): recompute, never trust shape
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class ParsedSeal:
    governing_goetic: str
    hyperbolic_parent: str
    root_court_glyph: str
    alternating_court_glyph: str
    b_q_glyph: str
    v_glyphs: tuple[str, str, str, str]
    center: str
    depth: int


def parse_living_domus(seal: str) -> ParsedSeal:
    cps = list(seal)
    if len(cps) < 31:
        raise ValueError("seal shorter than the 31-code-point minimum")
    if cps[0] != OUTER or cps[-1] != OUTER:
        raise ValueError("seal must be bound by the outer closure 🜛")
    if cps[2] != KLEIN or cps[4] != KLEIN or cps[-3] != KLEIN or cps[-5] != KLEIN:
        raise ValueError("Klein joins misplaced")
    g_i, root_glyph = cps[1], cps[3]
    g_j, alternating_glyph = cps[-2], cps[-4]
    # Domus word lives between position 5 and the fourth-from-last KLEIN at -5.
    word = cps[5:-5]
    # L_8 = : B _ : : V0 : : V1 :   (10 cps)
    # R_8 = : V2 : : V3 : : _ 𝔅 :   (10 cps)
    if len(word) < 21:
        raise ValueError("domus word too short")
    if word[0] != COLON:
        raise ValueError("Domus word must begin with a colon")
    b_q = word[1]
    if word[2] != UNDERSCORE or word[3] != COLON or word[4] != COLON or word[6] != COLON or word[7] != COLON or word[9] != COLON:
        raise ValueError("L_8 grammar violated")
    v0, v1 = word[5], word[8]
    r8 = word[-10:]
    if r8[0] != COLON or r8[2] != COLON or r8[3] != COLON or r8[5] != COLON or r8[6] != COLON or r8[7] != UNDERSCORE or r8[8] != BIAS_TERMINUS or r8[9] != COLON:
        raise ValueError("R_8 grammar violated")
    v2, v3 = r8[1], r8[4]
    center = word[10:-10]
    if len(center) == 1 and center[0] == ZERO_MIDDLE_GLYPH:
        depth = 0
    else:
        if ZERO_MIDDLE_GLYPH in center:
            raise ValueError("positive-depth center must not contain the Shadow Locus glyph ⛎")
        depth = len(center)
    return ParsedSeal(g_i, g_j, root_glyph, alternating_glyph, b_q, (v0, v1, v2, v3), "".join(center), depth)


def verify_living_domus(seal: str, g_i: str, g_j: str, *, emission: SourceEmission,
                          source_digest: str, source_size: int, nonce: int = 0,
                          source_domain: str = CANONICAL_SOURCE_DOMAIN) -> bool:
    """Recompute the whole derivation from (g_i,g_j) and check equality (plan §12).

    Shape recognition is not verification: the Court glyphs, Q witnesses, and
    center are recomputed and required to match. Parsed glyphs are never accepted
    as parent/Court overrides — the recomputation uses only g_i, g_j, and source.
    """
    parsed = parse_living_domus(seal)
    res = resolve_domus(
        g_i,
        g_j,
        hash_id=source_digest,
        emission=emission,
        source_size=source_size,
        source_domain=source_domain,
        nonce=nonce,
    )
    expect = living_domus_seal(res, parsed.depth, source_digest=source_digest,
                                 source_size=source_size, nonce=nonce, source_domain=source_domain)
    return expect == seal and parsed.governing_goetic == g_i and parsed.hyperbolic_parent == g_j