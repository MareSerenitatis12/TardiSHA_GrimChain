#!/usr/bin/env python3
"""TardiSHA Living Domus self-test harness.

Runs the plan §13 acceptance checks plus explicit regression for the nine hard
failures found in external audit. Exit code 0 iff every check passes. This is a
real executable harness (plan §13 requires one shipped in the package); it does
not self-grade a weaker implementation — each check asserts the plan's requirement.

Usage:  python3 TardiSHA_selftest.py
"""
from __future__ import annotations

import dataclasses
import json
import inspect
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from TardiSHA import canon as K
from TardiSHA import court_registry as CR
from TardiSHA import qstate_glyphs as Q
from TardiSHA import trig as TG
from TardiSHA import tripartite as TP
from TardiSHA import phase_evolution as PE
from TardiSHA import verification_appendices as VA
from TardiSHA import living_alphabet as LA
from TardiSHA import hashing as H
from TardiSHA import domus as C
from TardiSHA import personality_traits as PT
from TardiSHA import route as R
from TardiSHA import source_emission as ZE
from TardiSHA import aeon_layers as AL
from TardiSHA import stream as ST
from TardiSHA.manifestation import parity_flip
from TardiSHA.hashing import file_fingerprint, file_emission, canonical_emission, RAW_FILE_SOURCE_DOMAIN
from TardiSHA.node import node_from_material, node_from_file, node_from_directory
from TardiSHA import archive as AR
from TardiSHA.seal import create, parse, verify
from TardiSHA.domus_stream import living_domus_for_source

PASS: list[str] = []
FAIL: list[str] = []


def ck(name: str, cond: bool) -> None:
    (PASS if cond else FAIL).append(name)


def run() -> int:
    tf = tempfile.NamedTemporaryFile("wb", suffix=".t", delete=False)
    tf.write(b"the wheel carried strain, the cart advanced; gold and silver twine")
    tf.close()
    source_emission = file_emission(tf.name)
    dig, size = source_emission.source_digest, source_emission.source_size
    gi, gj, w = R.resolve_parents(source_emission)
    ck("00 Final Equation Z route closure", w.route_dcomp == 0 and w.truth == 1)
    res = C.resolve_domus(
        gi,
        gj,
        hash_id=dig,
        emission=source_emission,
        source_size=size,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
        nonce=0,
    )

    def sn(k: int) -> str:
        return C.living_domus_seal(res, k, source_digest=dig, source_size=size,
                                     source_domain=RAW_FILE_SOURCE_DOMAIN)

    # ---- §13 court / registry ------------------------------------------------
    ck("01 144 addresses once", sorted(r.address for r in CR._COURTS) == list(range(144)))
    ck("02 144 unique glyphs", len({r.glyph for r in CR._COURTS}) == 144)
    ck("03 one code point each", all(len(r.glyph) == 1 for r in CR._COURTS))
    ck("04 addr == 12i+j", all(CR.court_record(a).address == a for a in range(144)))
    ck("05 twelve diagonal courts", all(CR.court_record(13 * i).i == i for i in range(12)))
    ck("06 addr39 == ⛧", CR.court_record(39).glyph == "⛧")
    ck("07 addr72 == 🝏", CR.court_record(72).glyph == "🝏")
    f, r = CR.court_pair("⚝", "❂")
    ck("13 court_pair == (Ci,j, Cj,i)", (f, r) == (CR.court_from_goetics("⚝", "❂"),
                                                   CR.reciprocal_from_goetics("⚝", "❂")))
    ck("14 AHN/VEL -> 𝀖@40, ⴷ@51", f.glyph == "𝀖" and f.address == 40 and r.glyph == "ⴷ" and r.address == 51)
    f2, r2 = CR.court_pair("❂", "⧗")
    ck("15 VEL/DREH -> ⵃ@55, 𒄑@88", f2.glyph == "ⵃ" and f2.address == 55 and r2.glyph == "𒄑" and r2.address == 88)
    ck("16 ordinal == j+1", all(CR.court_ordinal(x) == x.j + 1 for x in CR._COURTS))
    ck("16A 144 ordered Supervenient personalities",
       len(PT.PERSONALITY_TRAIT_MAP) == 144
       and len(set(PT.PERSONALITY_TRAIT_MAP.values())) == 144
       and all(r.personality_trait == PT.personality_trait(K.GLYPH_BODY[r.i], K.GLYPH_BODY[r.j])
               for r in CR._COURTS))
    ck("16B retrieved Court examples remain exact",
       PT.personality_trait("⏣", "❈") == "The Inevitable"
       and PT.personality_trait("⧗", "❂") == "The Collapse"
       and PT.personality_trait("ꙮ", "⧗") == "The Vacuum"
       and PT.personality_trait("❄", "⚝") == "The Unified")

    # ---- §13 layered Goetic / Court / Domus math ----------------------------
    ck("17 visible Q body inherits from the anchoring Court",
       res.resolved_q_bias == res.root_court_motion.anchoring_goetic.q_bias
       and res.resolved_q_states == Q.Q_STATES
       and res.resolved_q_vector == res.root_court_motion.anchoring_goetic.q_vector)
    ck("18 Goetic roots remain immutable while Court offices stay partitioned",
       res.root_court_motion.anchor_immutable
       and res.root_court_motion.mirror_immutable
       and res.root_court_motion.anchoring_goetic.glyph == gi
       and res.root_court_motion.hyperbolic_mirror_goetic.glyph == gj
       and res.alternating_court_layer.governing_goetic.glyph == K.GLYPH_BODY[res.alternating_court.i]
       and res.alternating_court_layer.alternating_goetic.glyph == K.GLYPH_BODY[res.alternating_court.j])
    ck("19 Court motion is bounded exactly by Φ around the alternating Goetic pure frequency",
       abs(res.root_court_motion.phase.signed_numerator) <= res.root_court_motion.phase.denominator
       and res.root_court_motion.breath_radius == AL.PHI_IMAGE
       and res.root_court_motion.current_frequency == (
           res.root_court_motion.hyperbolic_mirror_goetic.frequency
           + res.root_court_motion.focal_breath
       )
       and res.root_court_motion.court_anchor_frequency
           == res.root_court_motion.hyperbolic_mirror_goetic.frequency)
    ck("19A Domus is exact Court C×D motion bounded by Φ²",
       res.domus_motion.derives_through_courts_only
       and not res.domus_motion.static_grid
       and res.domus_motion.governing_court.court_address == res.root_court.address
       and res.domus_motion.alternating_court.court_address == res.alternating_court.address
       and res.domus_motion.bearing.court == res.alternating_court
       and res.domus_motion.xi.within_unit_interval
       and res.domus_motion.exact_focal_breath.within_phi_squared
       and res.domus_motion.exact_bound_verified
       and res.domus_motion.court_crossing_cardinality == 144 * 144
       and res.domus_motion.breath_radius == AL.PHI_SQUARED_IMAGE
       and res.domus_frequency == (
           res.alternating_court_layer.alternating_goetic.frequency
           + res.domus_motion.focal_breath
       ))
    ck("19B Supervenience is compressed usable infinity of the same Domus body",
       res.supervenience is not res.liquid_witness
       and res.supervenience.operator == "⟠"
       and res.supervenience.court_coordinate == (res.root_court.i, res.root_court.j)
       and res.supervenience.personality_trait == res.root_court.personality_trait
       and res.supervenience.triplet_q_bias == res.resolved_q_bias
       and res.supervenience.triplet_q_states == res.resolved_q_states
       and res.supervenience.triplet_q_vector == res.resolved_q_vector
       and res.supervenience.triplet_frequency == res.domus_frequency
       and res.supervenience.fold_lineage.court_phase_digest == res.root_court_motion.phase.digest
       and res.supervenience.fold_lineage.alternating_court_address == res.alternating_court.address
       and res.supervenience.fold_lineage.alternating_bearing_lineage == res.domus_motion.bearing.lineage
       and res.supervenience.fold_lineage.fold_operator == "߷"
       and res.supervenience.fold_lineage.ground_node == res.fold_witness
       and res.supervenience.fold_lineage.vector_row == res.manifestation.vector_row
       and res.supervenience.fold_lineage.depth == 1
       and res.supervenience.infinite_yes_count == 110
       and res.supervenience.sacred_no_count == 34
       and res.supervenience.usable_infinity
       and res.supervenience.compressed_same_domus_body)
    ck("19C Infinite Yes and Sacred No are exact operative witnesses",
       res.infinite_yes.active_count == 110
       and res.sacred_no.withheld_count == 34
       and res.infinite_yes.active.isdisjoint(res.sacred_no.withheld)
       and res.infinite_yes.active | res.sacred_no.withheld == frozenset(range(144))
       and res.infinite_yes.unbounded_continuation_bounded_by_sacred_no
       and res.sacred_no.prevents_whiteout)
    ck("19D underscore materializes return to Q-bias",
       res.bias_return.opening_q_bias_glyph == res.b_q_glyph
       and res.bias_return.underscore == "_"
       and res.bias_return.bias_terminus_operator == "𝔅"
       and res.bias_return.returns_to_opening_q_bias)
    ck("19E Tripartite offices are exact and distinct",
       (res.tripartite.locus, res.tripartite.shadow_locus, res.tripartite.axiomyr) == ("♾", "⛎", "᳀")
       and res.tripartite.locus_non_traversable
       and res.tripartite.shadow_locus_deformable
       and res.tripartite.shadow_locus_return_path
       and res.tripartite.axiomyr_actuator
       and res.tripartite.axiomyr_constitutive_revivocus
       and res.tripartite.shared_root_frequency == TP.ROOT_FREQUENCY_BODY
       and TP.AXIOMYR_BRANCH_COMPONENT_SQUARED.numerator == 1847
       and TP.AXIOMYR_BRANCH_COMPONENT_SQUARED.denominator == 200)
    trig = res.trig_mirror
    ck("19F TRIG immutable Goetic body remains exact",
       (trig.operator_glyph, trig.structural_frequency, trig.operator_q_bias, trig.operator_q_vector)
       == ("⌬", complex(639), "Q3", (1, 1, 3, 2))
       and K.law("⌬").frequency == complex(639)
       and K.law("⌬").q_vector == (1, 1, 3, 2))
    ck("19G TRIG keeps three directional offices distinct",
       trig.global_shadow_parity == ("Q2", "Q3")
       and trig.forward_mirror_map == ("Q1", "Q3")
       and trig.return_commitment_map == ("Q3", "Q1")
       and trig.global_shadow_parity_preserved
       and parity_flip(2) == 3 and parity_flip(3) == 2
       and parity_flip(0) == 0 and parity_flip(1) == 1)
    ck("19H TRIG is source-bound and Domus-through-Court rooted",
       trig.source_digest == dig
       and trig.source_size == size
       and trig.governing_court_address == res.root_court.address
       and trig.alternating_court_address == res.alternating_court.address
       and trig.governing_court_phase_digest == res.root_court_motion.phase.digest
       and trig.alternating_court_bearing == res.domus_motion.bearing.lineage
       and trig.domus_body_commitment == res.domus_commitment
       and trig.court_rooted
       and trig.derives_through_courts_only)
    ck("19I TRIG preserves lineage and exact one-turn completion obligation",
       trig.lineage_preserved
       and trig.resonance_lock_witnessed
       and trig.mirror_materialization_typed
       and trig.commitment_return_typed
       and trig.completion_reached == (
           trig.mirror_materialization_typed
           and trig.commitment_return_typed
           and trig.global_shadow_parity_preserved
           and trig.one_turn_return_closed
           and res.manifestation.dcomp.closed
           and res.manifestation.dcomp.truth == 1
           and res.manifestation.dcomp.terminal == 0.0)
       and ("complete one-turn return closes at D-COMP zero" in trig.return_obligation))
    ck("19J TRIG does not counterfeit a classical Hodge computation",
       trig.classical_hodge_computation is False
       and "Q1 --𝔓[T_Bound,𝕂]--> Q3" in trig.derivation
       and "Q2↔Q3 remains the separate Shadow parity law" in trig.derivation)
    ck("19K TRIG cycle digest verifies and rejects mutation",
       TG.verify_trig_mirror(trig)
       and not TG.verify_trig_mirror(dataclasses.replace(trig, cycle_digest="0" * 64)))
    tri = res.tripartite
    c09 = res.aeon_phase_evolution
    c11 = res.verification_appendix_cycle
    ck("19L Domus identity commits TRIG, Tripartite, C09, and C11 cycles",
       res.domus_aeon.identity == C.alqc_hexdigest(
           (
               dig + res.domus_commitment + trig.cycle_digest
               + tri.cycle_digest + c09.cycle_digest + c11.cycle_digest
           ).encode("utf-8"),
           domain=C.DOMUS_COMMITMENT_DOMAIN))
    ck("19M Complete Tripartite witness verifies",
       TP.verify_tripartite_witness(tri)
       and tri.carrier_frequency_hz == TP.ROOT_FREQUENCY_BODY
       and tri.faraday_seed_seal == "🜛♌🜚⛎🜛🜚♾🜚🜛⛎🜚♌🜛")
    ck("19N Locus remains untouched while Shadow carries",
       tri.locus == "♾"
       and tri.locus_non_traversable
       and tri.locus_unchanged
       and not tri.direct_locus_traversal
       and tri.shadow_locus == "⛎"
       and tri.shadow_carrier_witnessed
       and tri.components[0].equation == "♾ = iω₀"
       and tri.components[1].equation == "⛎ = T_⛎(iω₀)")
    ck("19O Axiomyr keeps operator and Parliament seat distinct",
       tri.axiomyr == "᳀"
       and tri.components[2].body_glyph == "᳀"
       and tri.components[2].parliament_seat_glyph == "♌"
       and tuple(axis.operator for axis in tri.axiomyr_axes) == ("√i18.47", "⚛", "❄")
       and tuple(axis.frequency for axis in tri.axiomyr_axes[1:]) == (complex(285), complex(963))
       and all(not axis.direct_locus_traversal for axis in tri.axiomyr_axes))
    ck("19P Liquid connection governor yields EVENT at exact threshold",
       tri.liquid_threshold.governor_active_connections == 110
       and tri.liquid_threshold.governor_court_capacity == 144
       and tri.liquid_threshold.governor_withheld_connections == 34
       and tri.liquid_threshold.governor_expression == "110/144"
       and tri.liquid_threshold.energetic_body == K.LIQUID_THRESHOLD
       and tri.liquid_threshold.c_local_connection_body.numerator == 55
       and tri.liquid_threshold.c_local_connection_body.denominator == 72
       and tri.liquid_threshold.threshold_met
       and tri.liquid_threshold.manifestation_state == "EVENT"
       and tri.liquid_threshold.governing_threshold_not_ratio)
    below_threshold = TP.derive_liquid_threshold(
        active_connections=109, court_capacity=144, withheld_connections=35)
    at_threshold = TP.derive_liquid_threshold(
        active_connections=110, court_capacity=144, withheld_connections=34)
    ck("19P1 Liquid threshold preserves Potential below and EVENT at the governor",
       not below_threshold.threshold_met
       and below_threshold.manifestation_state == "Potential"
       and at_threshold.threshold_met
       and at_threshold.manifestation_state == "EVENT")
    ck("19Q nine Emissions preserve ∞ and ⛤ offices",
       len(tri.emissions) == 9
       and tuple(item.emission for item in tri.emissions)
       == ("Ponder", "Will", "Feel", "Speak", "Believe", "Act", "Know", "Ascend", "Regia")
       and all(item.vector_office == "∞" and item.nature_office == "⛤" for item in tri.emissions))
    ck("19R Parliament has twelve exact Star Seed Court mappings",
       len(tri.parliament) == 12
       and tuple(seed.index for seed in tri.parliament) == tuple(f"P13-D{i}" for i in range(1, 13))
       and tuple(seed.target_court for seed in tri.parliament)
       == ("⬡", "⧗", "❂", "⌬", "⏣", "⚝", "❈", "⊛", "⚛", "❄", "✡", "ꙮ")
       and tuple(seed.opcode for seed in tri.parliament)
       == ("WRITE_ONLY", "AUTH_CHECK", "DECRYPT", "VECTOR_TO", "ENTROPY_0", "SUPERPOS",
           "SIGNAL_IO", "SINK_STATE", "GUARD_NET", "WRITE_PHYS", "NEXT_FRAME", "BRIDGE")
       and all(seed.energy_displacement == 0.0 for seed in tri.parliament))
    ck("19S Q∞ and Q⛤ remain special offices outside Q0-Q3",
       tri.dynamic_q_states == ("Q0", "Q1", "Q2", "Q3")
       and tuple(state.symbol for state in tri.invariable_states) == ("Q∞", "Q⛤")
       and all(not state.dynamic_q_state for state in tri.invariable_states)
       and tri.invariable_states_outside_dynamic_q_domain)
    ck("19T Spirit-Soul Gold registry is complete and ordered",
       len(tri.spirit_soul_gold) == 15
       and tuple(item.number for item in tri.spirit_soul_gold) == tuple(range(1, 16))
       and tri.spirit_soul_gold[0].spirit_hz == 174.0
       and tri.spirit_soul_gold[-1].spirit_hz == 0.0)
    ck("19U Tripartite witness is source and Domus bound",
       tri.source_digest == dig
       and tri.source_size == size
       and tri.governing_court_address == res.root_court.address
       and tri.alternating_court_address == res.alternating_court.address
       and tri.domus_body_commitment == res.domus_commitment
       and tri.trig_cycle_digest == trig.cycle_digest
       and tri.court_rooted
       and tri.derives_through_courts_only)
    ck("19V Tripartite digest rejects mutation",
       not TP.verify_tripartite_witness(dataclasses.replace(tri, cycle_digest="0" * 64))
       and not TP.verify_tripartite_witness(dataclasses.replace(tri, direct_locus_traversal=True)))
    ck("19W Region C09 Aeon-phase witness verifies",
       PE.verify_aeon_phase_evolution(c09))
    ck("19X C09 carries 12 roots, 144 relational Courts, and 12 ordered phases",
       len(c09.goetic_table) == 12
       and len(c09.court_table) == 144
       and len(c09.phase_steps) == 12
       and tuple(step.phase for step in c09.phase_steps) == tuple(range(1, 13)))
    ck("19Y Goetic structural anchors remain immutable ཪ bodies",
       c09.structural_anchor_preserved
       and all(row.immutable_root for row in c09.goetic_table)
       and tuple(row.glyph for row in c09.goetic_table) == K.GLYPH_BODY
       and all(row.structural_frequency == K.law(row.glyph).frequency for row in c09.goetic_table))
    ck("19Z Court rows inherit governing Q-body and preserve alternating parent",
       c09.all_courts_relationally_typed
       and all(row.coordinate == divmod(row.address, 12) for row in c09.court_table)
       and all(row.inherited_q_bias == K.law(row.governing_goetic).q_bias for row in c09.court_table)
       and all(row.inherited_q_vector == K.law(row.governing_goetic).q_vector for row in c09.court_table)
       and all(row.alternating_structural_frequency == K.law(row.alternating_goetic).frequency
               for row in c09.court_table))
    ck("19AA structural ཪ and operational ±Φ remain separately typed",
       c09.operational_phi_preserved
       and (AL.PHI.a, AL.PHI.b, AL.PHI.denominator) == (1, 1, 2)
       and all(row.operational_phi_radius == AL.PHI for row in c09.court_table)
       and c09.court_table[39].structural_anchor_frequency == K.law("⚝").frequency
       and c09.court_table[39].hyperbolic_bifurcation_center == K.law("⚝").frequency
       and c09.court_table[39].ahn_structural_reference_hz
           == K.law("⚝").frequency.structural_hz)
    ck("19AB twelve-phase path preserves the Canon sequence and named Court witnesses",
       c09.phase_order_complete
       and c09.phase_steps[0].court_addresses == (0,)
       and c09.phase_steps[2].court_addresses == (89, 15, 28)
       and c09.phase_steps[8].court_addresses == (107,)
       and c09.phase_steps[11].court_addresses == (143,))
    ck("19AC M.A.S. is Fuel→Shape→Body in the exact 852→174→528 order",
       c09.mas_body.order_preserved
       and (c09.mas_body.manifestation_goetic,
            c09.mas_body.alignment_goetic,
            c09.mas_body.symmetry_goetic) == ("⧗", "⬡", "✡")
       and (c09.mas_body.manifestation_frequency,
            c09.mas_body.alignment_frequency,
            c09.mas_body.symmetry_frequency) == (complex(852), complex(174), complex(528)))
    ck("19AD Golden Ratio witnesses preserve the primary lock and 2^126 fold",
       c09.golden_ratio.within_tolerance
       and c09.golden_ratio.residual <= c09.golden_ratio.tolerance
       and c09.golden_ratio.harmonic_index == 76
       and c09.golden_ratio.folded_states == 2**126
       and c09.golden_ratio.manifest_positions == 81)
    ck("19AE Klein parity preserves cancellation and actual terminal completion",
       c09.poincare_parity.sphere_parity == 1
       and c09.poincare_parity.klein_parity == -1
       and c09.poincare_parity.shadow_cancellation_units == 0
       and c09.poincare_parity.q2_to_q3_return
       and c09.phase12_completion_reached == trig.completion_reached)
    ck("19AF first NULL:DEATH connection is recorded without exhausting its type",
       c09.null_death_connection.symbol == "NULL:DEATH"
       and c09.null_death_connection.first_explicit_physical_page == 102
       and c09.null_death_connection.first_occurrence_only
       and not c09.null_death_connection.exhaustive_type_claimed
       and c09.null_death_connection.loop_closure == "⏣ ↔ ❄")
    ck("19AG C09 body is source, Court, TRIG, and Tripartite bound",
       c09.source_digest == dig
       and c09.governing_court_address == res.root_court.address
       and c09.alternating_court_address == res.alternating_court.address
       and c09.domus_body_commitment == res.domus_commitment
       and c09.trig_cycle_digest == trig.cycle_digest
       and c09.tripartite_cycle_digest == tri.cycle_digest
       and c09.court_rooted
       and c09.derives_through_courts_only)
    ck("19AH C09 digest rejects mutation and false exhaustiveness",
       not PE.verify_aeon_phase_evolution(dataclasses.replace(c09, cycle_digest="0" * 64))
       and not PE.verify_aeon_phase_evolution(dataclasses.replace(
           c09,
           null_death_connection=dataclasses.replace(
               c09.null_death_connection,
               exhaustive_type_claimed=True,
           ),
       )))
    ck("19AV Region C11 verification-appendix cycle verifies independently",
       VA.verify_verification_appendix_cycle(c11))
    ck("19AW C11 is source, Domus, and prior-cycle bound",
       c11.source_digest == dig
       and c11.source_size == size
       and c11.governing_court_address == res.root_court.address
       and c11.alternating_court_address == res.alternating_court.address
       and c11.domus_body_commitment == res.domus_commitment
       and c11.trig_cycle_digest == trig.cycle_digest
       and c11.tripartite_cycle_digest == tri.cycle_digest
       and c11.phase_evolution_cycle_digest == c09.cycle_digest
       and c11.court_rooted)
    ck("19AX C11 types Millennium profiles without counterfeit recomputation",
       c11.corollaries_typed_not_recomputed
       and len(c11.millennium_profiles) == 8
       and all(profile.canon_corollary_declaration for profile in c11.millennium_profiles)
       and all(not profile.classical_object_recomputed_from_tardisha_source
               for profile in c11.millennium_profiles))
    ck("19AY C11 Bound Tensor verifies 12x12 to 9x9 runtime correspondence",
       c11.bound_tensor_runtime_correspondence
       and c11.bound_tensor.definition_side == 12
       and c11.bound_tensor.definition_nodes == 144
       and c11.bound_tensor.manifestation_side == 9
       and c11.bound_tensor.manifestation_nodes == 81
       and c11.bound_tensor.active_court_address == res.root_court.address
       and c11.bound_tensor.active_ground_node == res.manifestation.ground_node
       and c11.bound_tensor.active_vector_row == res.manifestation.vector_row
       and c11.bound_tensor.ground_node_matches_runtime
       and c11.bound_tensor.vector_row_matches_runtime
       and c11.bound_tensor.complete_ground_coverage)
    ck("19AZ C11 preserves Q2 accounting and the application boundary",
       c11.q2_resource_accounting_preserved
       and c11.shadow_runtime.source_shadow_debt == res.manifestation.dcomp.shadow_debt_initial
       and c11.shadow_runtime.source_form_work == res.manifestation.dcomp.form_work
       and c11.shadow_runtime.source_q3_gain == res.manifestation.dcomp.q3_recursion_gain
       and c11.shadow_runtime.source_final_parity == "Q3"
       and not c11.shadow_runtime.raylib_debt_factor_imported_into_tardisha
       and not c11.shadow_runtime.raylib_reflective_ring_imported_into_tardisha
       and not c11.shadow_runtime.raylib_delayed_reinjection_imported_into_tardisha
       and c11.application_boundary_preserved)
    ck("19BA C11 keeps Liquid governor, Potential, Stasis, and Whiteout offices distinct",
       c11.canonical_liquid_regime_preserved
       and c11.liquid_regime.canonical_expression == "110/144"
       and c11.liquid_regime.canonical_active == 110
       and c11.liquid_regime.canonical_withheld == 34
       and c11.liquid_regime.canonical_regime == "LIQUID"
       and c11.liquid_regime.below_cutoff_regime == "STASIS"
       and c11.liquid_regime.full_capacity_regime == "WHITEOUT"
       and c11.liquid_regime.potential_state_distinct_from_runtime_regime)
    ck("19BB C11 grammar and translation registries preserve existing Q positions",
       c11.grammar_registry_complete
       and len(c11.grammar.bnf_productions) == 10
       and len(c11.grammar.inference_rules) == 9
       and c11.quantum_translation_preserves_q_positions
       and tuple(row.state for row in c11.quantum_translation) == Q.Q_STATES
       and c11.volume_bifurcation_preserves_one_body
       and c11.volume_bifurcation.segmentation_editorial
       and not c11.volume_bifurcation.segmentation_ontological)
    ck("19BC C11 frequency and 144-Court glyph registries preserve source identity",
       c11.frequency_registry_matches_goetic_laws
       and c11.glyph_registry_identity_preserved
       and c11.glyph_registry_audit.court_entries == 144
       and c11.glyph_registry_audit.declared_codepoint_matches == 142
       and tuple(item.court_address for item in c11.glyph_registry_audit.discrepancies) == (39, 72)
       and all(item.implementation_preserves_glyph_scalar
               for item in c11.glyph_registry_audit.discrepancies))
    ck("19BD C11 digest rejects body, source, and application-boundary mutation",
       not VA.verify_verification_appendix_cycle(dataclasses.replace(c11, cycle_digest="0" * 64))
       and not VA.verify_verification_appendix_cycle(dataclasses.replace(c11, source_digest="0" * 64))
       and not VA.verify_verification_appendix_cycle(dataclasses.replace(
           c11, bound_tensor=dataclasses.replace(c11.bound_tensor, active_ground_node=(c11.bound_tensor.active_ground_node + 1) % 81)))
       and not VA.verify_verification_appendix_cycle(dataclasses.replace(
           c11, shadow_runtime=dataclasses.replace(c11.shadow_runtime, raylib_debt_factor_imported_into_tardisha=True))))
    hostile_index = 29
    hostile_seed = H.alqc_digest(
        f"ALQC Mirror emergence source {hostile_index}".encode(),
        domain=b"TARDISHA:HOSTILE-FIXTURE\x00",
        length=64,
    )
    hostile_body = (
        hostile_seed * ((hostile_index % 7) + 1)
        + hostile_index.to_bytes(4, "big")
        + bytes(range(hostile_index % 64))
        + b"\x00\xff\n"
    )
    hostile_file = tempfile.NamedTemporaryFile("wb", suffix=".hostile", delete=False)
    hostile_file.write(hostile_body)
    hostile_file.close()
    hostile_emission = file_emission(hostile_file.name)
    hostile_gi, hostile_gj, _hostile_route = R.resolve_parents(hostile_emission)
    hostile_res = C.resolve_domus(
        hostile_gi,
        hostile_gj,
        hash_id=hostile_emission.source_digest,
        emission=hostile_emission,
        source_size=hostile_emission.source_size,
        source_domain=RAW_FILE_SOURCE_DOMAIN,
        nonce=0,
    )
    ck("19BE zero-Q3 hostile body preserves owed TRIG completion through C11",
       hostile_res.trig_mirror.q_vector_values == (1, 3, 0, 0)
       and hostile_res.trig_mirror.q3_recursion_gain == 0.0
       and not hostile_res.trig_mirror.completion_reached
       and not hostile_res.verification_appendix_cycle.runtime_completion_reached
       and hostile_res.verification_appendix_cycle.trig_runtime == hostile_res.trig_mirror
       and VA.verify_verification_appendix_cycle(hostile_res.verification_appendix_cycle))
    os.unlink(hostile_file.name)
    ck("31 Q map is exactly Q0-3 -> 🜔🜕🜖🜗", [Q.psi_q(x) for x in Q.Q_STATES] == ["🜔", "🜕", "🜖", "🜗"])
    ck("31A reverse Q seam returns each glyph to its state",
       tuple(Q.q_state_of(glyph) for glyph in ("🜔", "🜕", "🜖", "🜗")) == Q.Q_STATES)
    ck("32 Q names preserve FORM/TRUTH/SHADOW/RECURSION",
       [Q.name_of(x) for x in Q.Q_STATES] == ["FORM", "TRUTH", "SHADOW", "RECURSION"])
    slots = Q.q_state_slots((3, 2, 1, 0))
    ck("32A Q-coordinate offices remain fixed while vector values remain recoverable",
       tuple(slot.state for slot in slots) == Q.Q_STATES
       and tuple(slot.glyph for slot in slots) == ("🜔", "🜕", "🜖", "🜗")
       and tuple(slot.value for slot in slots) == (3, 2, 1, 0))
    ck("32AA visible Q-body is derived from the current vector",
       Q.q_vector_glyphs((3, 2, 1, 0)) == ("🜗", "🜖", "🜕", "🜔")
       and Q.q_vector_glyphs((1, 1, 1, 3)) == ("🜕", "🜕", "🜕", "🜗"))
    q_body = Q.derive_domus_q_body(res.root_court_motion.anchoring_goetic.q_bias,
                                  res.root_court_motion.anchoring_goetic.q_vector)
    ck("32AB complete Court-derived Q-body returns through the First Seam",
       q_body.q_bias == res.resolved_q_bias
       and q_body.bias_glyph == res.b_q_glyph
       and q_body.q_vector == res.resolved_q_vector
       and q_body.q_glyphs == res.v_glyphs
       and Q.q_state_of(q_body.bias_glyph) == q_body.q_bias
       and tuple(Q.value_of_glyph(glyph) for glyph in q_body.q_glyphs) == q_body.q_vector)
    all_q_bodies = tuple(Q.derive_domus_q_body(K.law(g).q_bias, K.law(g).q_vector)
                         for g in K.GLYPH_BODY)
    ck("32AC Domus bias and Q-body vary with the resolved governing Court",
       len({body.bias_glyph for body in all_q_bodies}) == 4
       and len({body.q_glyphs for body in all_q_bodies}) == 12
       and all(body.bias_glyph == Q.psi_q(K.law(g).q_bias)
               and body.q_glyphs == Q.q_vector_glyphs(K.law(g).q_vector)
               for g, body in zip(K.GLYPH_BODY, all_q_bodies)))
    try:
        Q.q_state_slots((0, 1, 2))
    except ValueError:
        short_q_rejected = True
    else:
        short_q_rejected = False
    ck("32B Q-vector seam rejects non-fourfold bodies", short_q_rejected)
    ck("33 B_Q = psi(bias)", res.b_q_glyph == Q.psi_q(res.resolved_q_bias))

    # ---- §13 seal grammar / lengths / stability ------------------------------
    ck("36 zero-depth center is Shadow Locus ⛎", C.parse_living_domus(sn(0)).center == C.ZERO_MIDDLE_GLYPH)
    ck("37 positive depth has no Shadow Locus zero glyph", C.ZERO_MIDDLE_GLYPH not in sn(14))
    ck("44 depth0 length 31", len(sn(0)) == 31)
    ck("45 positive length 30+n", all(len(sn(k)) == 30 + k for k in (1, 14, 50)))
    ck("46 grimchain 169 -> 199", len(sn(169)) == 199)
    one_coordinate_center = C.parse_living_domus(sn(1)).center
    ck("46A exact Domus colon grammar",
       C.domus_word(res, one_coordinate_center, depth=1) == (
           ":" + res.b_q_glyph + "_::" + res.v_glyphs[0] + "::" + res.v_glyphs[1]
           + ":" + one_coordinate_center + ":" + res.v_glyphs[2]
           + "::" + res.v_glyphs[3] + "::_𝔅:"
       ))
    ck("47 shorter center prefixes longer",
       C.parse_living_domus(sn(12)).center.startswith(C.parse_living_domus(sn(5)).center))
    ck("49 nine Emission offices preserve the three-code-point Regia alignment",
       LA.DAEMONIC_TONGUE[0] == "𑁦"
       and LA.DAEMONIC_TONGUE[1:9] == ("☿", "♂", "♀", "♃", "♄", "⛢", "♆", "♇")
       and LA.DAEMONIC_TONGUE[9:12] == ("☽", "☉", "☾")
       and LA.DAEMONIC_TONGUE[24:36] == ("⏣", "⬡", "✡", "⚝", "❂", "ꙮ", "❈", "⧗", "⊛", "❄", "⚛", "⌬"))
    ck("50 Synodic Magicae and Daemonic Tongue preserve their exact bodies",
       len(LA.SYNODIC_MAGICAE) == 192
       and len(set(LA.SYNODIC_MAGICAE)) == 192
       and len(LA.DAEMONIC_TONGUE) == 192
       and len(set(LA.DAEMONIC_TONGUE)) == 192
       and len(H.ALPHABET) == 191
       and "⟠" not in H.ALPHABET
       and H.ALPHABET == LA.SYNODIC_MAGICAE.replace("⟠", "")
       and LA.SYNODIC_MAGICAE == "".join(LA.DAEMONIC_TONGUE)
       and LA.DAEMONIC_TONGUE[-12:] == ("𝔓", "ཪ", "☍", "⟠", "⚶", "߷", "🜚", "🜛", "🜕", "🜗", "🜔", "🜖"))
    ck("52 verify recomputes dynamic slots",
       C.verify_living_domus(sn(9), gi, gj, emission=source_emission, source_digest=dig, source_size=size,
                               source_domain=RAW_FILE_SOURCE_DOMAIN))
    bad = sn(0)
    bad = bad[:6] + ("🜖" if bad[6] != "🜖" else "🜔") + bad[7:]
    ck("54 one code-point mutation fails verify",
       not C.verify_living_domus(bad, gi, gj, emission=source_emission, source_digest=dig, source_size=size,
                                   source_domain=RAW_FILE_SOURCE_DOMAIN))
    ck("55 Ennead nine strikes", len(res.manifestation.ennead.strikes) == 9)
    ck("58 Domus Q-state glyphs derive componentwise from the resolved Court vector",
       res.v_glyphs == Q.q_vector_glyphs(res.resolved_q_vector)
       and res.resolved_q_states == Q.Q_STATES
       and res.resolved_q_vector == res.root_court_motion.anchoring_goetic.q_vector)
    ck("59 explicit-length KAT seal intact", parse(create("song dance", middle_length=14).value).value is not None)
    zero_seal = create("song dance", middle_length=0)
    ck("59A generic zero middle is Shadow Locus ⛎",
       zero_seal.middle == C.ZERO_MIDDLE_GLYPH
       and parse(zero_seal.value).middle_length == 0
       and verify(zero_seal.value, "song dance"))

    # ---- HF regression -------------------------------------------------------
    # HF1: node carries no hard-coded absolute import
    ck("HF1 no hardcoded __import__ in node", '__import__("TardiSHA' not in open("TardiSHA/node.py").read())
    # HF2: a self-signed false Parliament pair must fail complete-emission verification.
    lawful = R.lawful_pair(source_emission)
    forged = ("⏣", "⬡") if lawful != ("⏣", "⬡") else ("⌬", "⚛")
    forged_origin_index = K.GLYPH_BODY.index(forged[0])
    forged_resolution_index = K.GLYPH_BODY.index(forged[1])
    forged_first_seat = next(seat for seat in ZE.PARLIAMENT if seat.goetic == forged[0])
    forged_last_seat = next(seat for seat in ZE.PARLIAMENT if seat.goetic == forged[1])
    forged_source_q = tuple(float(v) for v in K.law(forged[0]).q_vector)
    forged_resolution_q = tuple(float(v) for v in K.law(forged[1]).q_vector)
    forged_first = dataclasses.replace(w.first, seat=forged_first_seat)
    forged_last = dataclasses.replace(w.last, seat=forged_last_seat)
    forged_provisional = dataclasses.replace(
        w,
        first=forged_first,
        last=forged_last,
        origin_index=forged_origin_index,
        resolution_index=forged_resolution_index,
        court_address=K.court_node(forged[0], forged[1]),
        reciprocal_address=K.court_node(forged[1], forged[0]),
        source_q_vector=forged_source_q,
        resolution_q_vector=forged_resolution_q,
        derivation_lineage=("self-signed forged Parliament derivation",),
        derivation_proof="",
    )
    forged_w = dataclasses.replace(
        forged_provisional,
        derivation_proof=R._proof_for(forged_provisional),
    )
    ck("HF2 forged pair rejected by verify_source",
       not R.verify_source(source_emission, forged_w))
    ck("HF2 genuine pair accepted", R.verify_source(source_emission, w))
    # HF3: terminal unresolved Q2 is distinct from accumulated Shadow Debt.
    parts = R.connection(K.law("❄").q_vector, K.law("⧗").q_vector, "❄", "⧗")
    ck("HF3 terminal unresolved debt == |Q2| of target",
       parts.terminal_unresolved_debt == float(abs(K.law("⧗").q_vector[2])))
    ck("HF3 accumulated debt includes native return friction",
       parts.shadow_debt_initial == parts.local_friction + parts.terminal_unresolved_debt)
    # HF4: horizon uses the actual current Court-node, not (root+h)
    hor = ST.liquid_horizon(res.root_court.address, 7)
    ck("HF4 horizon i_h is the supplied node (not root+7)", hor.current_court_index == res.root_court.address)
    ck("HF4 horizon 110/34", hor.active_count == 110 and hor.withheld_count == 34)
    # HF5: one Domus identity governs compressed and unfolded visibility.
    altered_aeon = dataclasses.replace(res.domus_aeon, identity="0" * 64)
    res_alt = dataclasses.replace(res, domus_aeon=altered_aeon)
    ck("HF5 Synodic Magicae center binds Domus identity",
       C._center(res, 14, source_digest=dig, source_size=size, nonce=0,
                 source_domain=RAW_FILE_SOURCE_DOMAIN)
       != C._center(res_alt, 14, source_digest=dig, source_size=size, nonce=0,
                    source_domain=RAW_FILE_SOURCE_DOMAIN))
    reproduced = C.resolve_domus(
        gi, gj, hash_id=dig, emission=source_emission, source_size=size,
        source_domain=RAW_FILE_SOURCE_DOMAIN, nonce=0,
    )
    ck("HF5 Domus commitment and identity reproducible",
       reproduced.domus_commitment == res.domus_commitment
       and reproduced.domus_aeon.identity == res.domus_aeon.identity)
    ck("HF5 Shadow Locus zero and Synodic Magicae are visible depths of one Domus Aeon",
       C.parse_living_domus(sn(0)).center == C.ZERO_MIDDLE_GLYPH
       and C.parse_living_domus(sn(14)).center == C._center(
           res, 14, source_digest=dig, source_size=size, nonce=0,
           source_domain=RAW_FILE_SOURCE_DOMAIN)
       and res.domus_aeon.zero_middle_glyph == C.ZERO_MIDDLE_GLYPH
       and res.domus_aeon.shadow_locus_is_zero_middle_body
       and res.domus_aeon.synodic_magicae_is_manifested_body)

    goetic_before = {g: (K.law(g).frequency, K.law(g).q_bias, K.law(g).q_vector)
                     for g in K.GLYPH_BODY}
    all_court_motions = [AL.derive_court_motion(
        record, source_digest=dig, source_size=size,
        source_domain=RAW_FILE_SOURCE_DOMAIN, nonce=0
    ) for record in CR._COURTS]
    all_court_layers = [AL.court_layer(record) for record in CR._COURTS]
    goetic_after = {g: (K.law(g).frequency, K.law(g).q_bias, K.law(g).q_vector)
                    for g in K.GLYPH_BODY}
    ck("LAYER all Goetic state/bias/vector/frequency remain immutable",
       goetic_before == goetic_after)
    ck("LAYER all 144 Courts inherit Q-body from governing and Ω_C from alternating",
       all(
           motion.anchoring_goetic.glyph == K.GLYPH_BODY[record.i]
           and motion.hyperbolic_mirror_goetic.glyph == K.GLYPH_BODY[record.j]
           and motion.court_anchor_frequency == complex(K.law(K.GLYPH_BODY[record.j]).frequency)
           and layer.alternating_goetic.frequency == motion.court_anchor_frequency
           for record, motion, layer in zip(CR._COURTS, all_court_motions, all_court_layers)
       ))
    ck("LAYER all 144 Court breaths remain within exact Φ around alternating Ω_C",
       all(
           abs(motion.phase.signed_numerator) <= motion.phase.denominator
           and motion.breath_radius == AL.PHI_IMAGE
           and motion.current_frequency == motion.court_anchor_frequency + motion.focal_breath
           for motion in all_court_motions
       ))
    crossing_indices = {144 * c.address + d.address for c in CR._COURTS for d in CR._COURTS}
    ck("LAYER C×D ordered Court crossing image is exactly 144² = 20,736",
       len(crossing_indices) == 144 * 144
       and min(crossing_indices) == 0
       and max(crossing_indices) == 144 * 144 - 1)
    ck("LAYER runtime Domus uses exact 𝔃₁/BETA Court D and Φ² bound",
       res.domus_motion.bearing == ZE.resolve_court_bearing(source_emission)
       and res.domus_motion.bearing.product_measure_verifies
       and res.domus_motion.bearing.normalized_measure_sum == 1
       and res.domus_motion.xi.within_unit_interval
       and res.domus_motion.exact_focal_breath.within_phi_squared
       and res.domus_motion.exact_bound_verified)
    domus_source = inspect.getsource(AL.derive_domus_motion)
    ck("LAYER Domus frequency derivation contains no digest/hash call",
       all(token not in domus_source for token in (
           "_phase(", "alqc_digest(", "alqc_hexdigest(", "hashlib", "DOMUS_PHASE_DOMAIN"
       )))
    ck("LAYER D is independently source-derived rather than forced to C_ji",
       res.alternating_court.address == ZE.resolve_court_bearing(source_emission).court.address
       and res.domus_motion.bearing.cadence_symbol == "𝔃₁"
       and res.domus_motion.bearing.bearing == ZE.BETA)
    # HF7: parity flip is an involution on 0..3
    ck("HF7 parity involutive", all(parity_flip(parity_flip(x)) == x for x in (0, 1, 2, 3)) and parity_flip(2) == 3)
    # HF8/V-06: a node whose stored pair contradicts its source is rejected at construction
    n = node_from_file(tf.name)
    ck("V06 genuine node source_route verifies", n.domus_witness(middle_length=0)["source_route"]["verifies"])

    invariant_node = node_from_material("authoritative invariant", mode="INVARIANT")
    ck("NODE INVARIANT materializes exactly Shadow Locus",
       invariant_node.materialized_middle() == C.ZERO_MIDDLE_GLYPH
       and invariant_node.supervenient_window()
       == f"{invariant_node.origin_glyph}{C.ZERO_MIDDLE_GLYPH}{invariant_node.resolution_glyph}")
    try:
        invariant_node.middle_window(0, 0)
    except H.TardiSHAError:
        ck("NODE INVARIANT rejects every window derivation", True)
    else:
        ck("NODE INVARIANT rejects every window derivation", False)

    try:
        node_from_material("finite without extent", mode="MANIFEST_FINITE")
    except H.TardiSHAError:
        ck("NODE MANIFEST_FINITE rejects missing explicit extent", True)
    else:
        ck("NODE MANIFEST_FINITE rejects missing explicit extent", False)
    finite_node = node_from_material(
        "finite exact extent", mode="MANIFEST_FINITE", finite_extent=14
    )
    ck("NODE MANIFEST_FINITE materializes only declared extent",
       len(finite_node.materialized_middle()) == 14)
    try:
        finite_node.middle_window(0, 13)
    except H.TardiSHAError:
        ck("NODE MANIFEST_FINITE rejects substituted extent", True)
    else:
        ck("NODE MANIFEST_FINITE rejects substituted extent", False)

    open_node = node_from_material("open without terminal", mode="MANIFEST_OPEN")
    ck("NODE MANIFEST_OPEN derives arbitrary finite windows without terminal claim",
       len(open_node.middle_window(169, 14)) == 14
       and open_node.mode_witness()["open_stream_has_no_terminal_claim"]
       and open_node.mode_witness()["declared_finite_extent"] is None)
    try:
        node_from_material("open cannot close", mode="MANIFEST_OPEN", finite_extent=14)
    except H.TardiSHAError:
        ck("NODE MANIFEST_OPEN rejects terminal extent", True)
    else:
        ck("NODE MANIFEST_OPEN rejects terminal extent", False)
    try:
        dataclasses.replace(n, origin_glyph=("⏣" if n.origin_glyph != "⏣" else "⌬"))
        ck("V06 tampered node rejected at construction", False)
    except Exception:
        ck("V06 tampered node rejected at construction", True)

    # V-01: terminal finite-interval D-COMP varies across the 144 ordered Courts.
    from TardiSHA.manifestation import close_boundary, ennead_saturate, parity_vector
    dvals = [close_boundary(K.law(a).q_vector, K.law(b).q_vector,
                            court=K.court_node(a, b)).dcomp.terminal
             for a in K.GLYPH_BODY for b in K.GLYPH_BODY]
    ck("V01 terminal D-COMP is exact zero with Truth unity on all 144 Courts",
       dvals == [0.0] * 144
       and all(
           close_boundary(K.law(a).q_vector, K.law(b).q_vector,
                          court=K.court_node(a, b)).dcomp.truth == 1
           for a in K.GLYPH_BODY for b in K.GLYPH_BODY
       ))
    closure_law = []
    for a in K.GLYPH_BODY:
        for b in K.GLYPH_BODY:
            witness = close_boundary(
                K.law(a).q_vector,
                K.law(b).q_vector,
                court=K.court_node(a, b),
            ).dcomp
            closure_law.append(
                witness.closed
                and witness.exact_commutator_pressure == (0, 1)
                and witness.exact_velocity_mismatch_square == (0, 1)
                and witness.exact_shadow_debt_terminal == (0, 0, 1)
            )
    ck("V01 finite return closes exact commutator, Mirror path, and Shadow Debt on all 144 Courts",
       all(closure_law))
    # V-02: strike 9 is a conversion — nonzero debt leaves a positive pre-lock ghost, Q2 emptied
    e = ennead_saturate(0, 3.0)
    ck("V02 pre-lock Q2 ghost > 0 (finite Φ-siphon)", e.pre_lock_q2_residual > 0.0)
    ck("V02 Q2 emptied by k=9 conversion", e.residual_debt == 0.0 and e.q3_recursion_residue == e.pre_lock_q2_residual)
    ck("V02 strike 9 typed Q3 phase-lock", e.strikes[8].q_parity == "Q3" and e.strikes[8].phase_locked)
    # GRIM: package entry point must resolve through cli.main.
    def run_mod(*argv: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", *argv],
            cwd=Path(__file__).resolve().parent,
            text=True,
            capture_output=True,
        )

    top_help = run_mod("TardiSHA", "--help")
    ck("CLI python -m TardiSHA resolves cli.main", top_help.returncode == 0)

    # GRIM: absence is an invocation state. It is not default 14 and not collapsed to numeric 0.
    grim_src = Path("TardiSHA/grimchain.py").read_text(encoding="utf-8")
    ck("GRIM omitted middle preserved as invocation state",
       "middle_was_supplied" in grim_src and "_do_file_shadow_locus" in grim_src and
       "DEFAULT_MIDDLE_LENGTH" not in grim_src and "if middle is None:\n            middle = 0" not in grim_src)

    def grim(*argv: str) -> str:
        cp = run_mod("TardiSHA.grimchain", *argv)
        ck(f"grimchain {' '.join(argv) or '<stdin>'} exits 0", cp.returncode == 0)
        return cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else ""

    g_absent = grim(tf.name)
    g_explicit0 = grim("0", tf.name)
    g_explicit14 = grim("14", tf.name)
    ck("GRIM omitted middle emits Shadow Locus center ⛎", C.parse_living_domus(g_absent).center == C.ZERO_MIDDLE_GLYPH)
    ck("GRIM explicit 0 emits Shadow Locus center ⛎", C.parse_living_domus(g_explicit0).center == C.ZERO_MIDDLE_GLYPH)
    p14 = C.parse_living_domus(g_explicit14)
    ck("GRIM explicit 14 emits native Synodic Magicae center", p14.depth == 14 and C.ZERO_MIDDLE_GLYPH not in p14.center)

    with tempfile.TemporaryDirectory() as d:
        dp = Path(d)
        (dp / "a.txt").write_text("alpha", encoding="utf-8")
        (dp / "sub").mkdir()
        (dp / "sub" / "b.txt").write_text("beta", encoding="utf-8")
        gd_absent = grim(str(dp))
        gd_14 = grim("14", str(dp))
        ck("GRIM directory omitted middle emits Shadow Locus center ⛎", C.parse_living_domus(gd_absent).center == C.ZERO_MIDDLE_GLYPH)
        pd14 = C.parse_living_domus(gd_14)
        ck("GRIM directory explicit 14 emits native Synodic Magicae center", pd14.depth == 14 and C.ZERO_MIDDLE_GLYPH not in pd14.center)

    # V-07: visible_window is a coordinate witness, not a Living Domus depth seal.
    starts = (0, 1, 10, 169)
    wins = {s: n.visible_window(s, 14) for s in starts}
    ck("V07 visible_window accepts arbitrary coordinates", all(isinstance(wins[s], str) and wins[s] for s in starts))
    ck("V07 visible_window is boundary + middle_window + boundary",
       all(wins[s] == f"{n.origin_glyph}{n.middle_window(s, 14)}{n.resolution_glyph}" for s in starts))
    ck("V07 nonzero coordinate windows are not refused", wins[10] != "")
    ck("V07 coordinate window is distinct from Living Domus seal", wins[0] != living_domus_for_source(tf.name, 14, kind="file"))

    # V-01(new): canonical material has the same digest-derived parent law as files.
    from TardiSHA.node import TardiSHANode
    canonical_source_emission, _cdom = canonical_emission("a wheel that carries strain and returns")
    cdig, csize = canonical_source_emission.source_digest, canonical_source_emission.source_size
    canonical_witness = R.source_route_witness_from_emission(canonical_source_emission)
    cw = R.parents_t(canonical_witness)
    cstored = ("⏣", "⏣") if cw != ("⏣", "⏣") else ("⬡", "⬡")
    try:
        TardiSHANode(mode="MANIFEST_FINITE", source_digest=cdig, source_size=csize,
                     origin_glyph=cstored[0], resolution_glyph=cstored[1], source_domain="canonical",
                     route_witness=canonical_witness, finite_extent=14)
    except H.TardiSHAError:
        ck("V01 canonical forged parent rejected at construction", True)
    else:
        ck("V01 canonical forged parent rejected at construction", False)

    # WITNESS: serialized layer bodies must remain exact and independently typed.
    witness = n.domus_witness(middle_length=14)

    def _as_complex(value: object) -> complex:
        if isinstance(value, (int, float, complex)):
            return complex(value)
        return complex(str(value).replace(" ", ""))

    def _court_motion_complete(side: str, record: CR.CourtRecord) -> bool:
        body = witness[side]["motion"]
        anchor = body["anchoring_goetic"]
        mirror = body["hyperbolic_mirror_goetic"]
        phase = body["phase"]
        expected_anchor = CR.gov_glyph(record)
        expected_mirror = CR.alt_glyph(record)
        if tuple(body["court_coordinate"]) != (record.i, record.j):
            return False
        if body["court_address"] != record.address or body["court_glyph"] != record.glyph:
            return False
        if anchor["glyph"] != expected_anchor or mirror["glyph"] != expected_mirror:
            return False
        if _as_complex(anchor["frequency"]) != complex(K.law(expected_anchor).frequency):
            return False
        if _as_complex(mirror["frequency"]) != complex(K.law(expected_mirror).frequency):
            return False
        if anchor["q_bias"] != K.law(expected_anchor).q_bias:
            return False
        if tuple(anchor["q_vector"]) != K.law(expected_anchor).q_vector:
            return False
        if abs(phase["signed_numerator"]) > phase["denominator"]:
            return False
        if body["breath_radius"] != AL.PHI_IMAGE:
            return False
        if (_as_complex(body["current_frequency"])
                != _as_complex(mirror["frequency"]) + _as_complex(body["focal_breath"])):
            return False
        return bool(body["anchor_immutable"] and body["mirror_immutable"] and body["derivation"])

    def _court_layer_complete(side: str, record: CR.CourtRecord) -> bool:
        body = witness[side]["layer"]
        governing = body["governing_goetic"]
        alternating = body["alternating_goetic"]
        return (
            tuple(body["court_coordinate"]) == (record.i, record.j)
            and body["court_address"] == record.address
            and body["court_glyph"] == record.glyph
            and governing["glyph"] == CR.gov_glyph(record)
            and alternating["glyph"] == CR.alt_glyph(record)
            and _as_complex(body["alternating_goetic_frequency"])
                == complex(K.law(CR.alt_glyph(record)).frequency)
        )

    ck("WITNESS governing Court C motion is complete",
       _court_motion_complete("governing_court", res.root_court))
    ck("WITNESS alternating Court D layer is complete",
       _court_layer_complete("alternating_court", res.alternating_court))
    cm = witness["domus_motion"]
    ck("WITNESS Domus motion is exact Court-derived Φ²",
       cm["derives_through_courts_only"]
       and not cm["static_grid"]
       and cm["exact_bound_verified"]
       and cm["court_crossing_cardinality"] == 144 * 144
       and cm["bearing"]["cadence_symbol"] == "𝔃₁"
       and cm["bearing"]["bearing"]["name"] == "Phi^-2"
       and cm["breath_radius"] == AL.PHI_SQUARED_IMAGE)
    ck("WITNESS Infinite Yes / Sacred No / Q-bias return exposed",
       witness["infinite_yes"]["active_count"] == 110
       and witness["sacred_no"]["withheld_count"] == 34
       and witness["bias_return"]["returns_to_opening_q_bias"])
    ck("WITNESS visible Domus Aeon is the serialized Synodic Magicae body",
       witness["domus_aeon"]["visible_body"] == witness["visible_domus_aeon"]
       and witness["domus_aeon"]["identity"] == res.domus_aeon.identity)
    ck("WITNESS TRIG cycle is serialized and JSON-safe",
       witness["trig_mirror_witness"]["cycle_digest"] == res.trig_mirror.cycle_digest
       and witness["trig_mirror_witness"]["forward_mirror_map"] == ["Q1", "Q3"]
       and isinstance(json.dumps(witness, ensure_ascii=False, sort_keys=True), str))

    # FINAL EQUATION Z: the ordered Goetic body spans the complete Court address body.
    court_addresses = {
        K.court_load(origin, resolution)
        for origin in K.GLYPH_BODY
        for resolution in K.GLYPH_BODY
    }
    ck("HASH twelve ordered Goetics span all 144 Court addresses",
       court_addresses == set(range(K.TOTAL_CAPACITY)))

    nontext = {"raw": bytes((0, 255, 128, 1)), "integer": 47, "body": [None, True]}
    nontext_emission, _ = H.canonical_emission(nontext)
    nontext_route = R.calculate_route(nontext_emission)
    nontext_seal = create(nontext, middle_length=14)
    nontext_node = node_from_material(nontext, mode="MANIFEST_FINITE", finite_extent=14)
    ck("HASH non-text canonical objects use the same digest parent law",
       (nontext_route.origin_glyph, nontext_route.resolution_glyph)
       == (nontext_seal.origin_glyph, nontext_seal.resolution_glyph)
       == (nontext_node.origin_glyph, nontext_node.resolution_glyph))
    ck("HASH no lexical route modules remain",
       not Path("TardiSHA/vectorizer.py").exists()
       and not Path("TardiSHA/lexicon.py").exists()
       and "semantic_text" not in Path("TardiSHA/seal.py").read_text(encoding="utf-8")
       and "semantic_text" not in Path("TardiSHA/node.py").read_text(encoding="utf-8"))

    label_res = C.resolve_domus(
        gi, gj, hash_id=dig, emission=source_emission, source_size=size, source_domain="raw-file", nonce=0)
    byte_res = C.resolve_domus(
        gi, gj, hash_id=dig, emission=source_emission, source_size=size,
        source_domain=RAW_FILE_SOURCE_DOMAIN, nonce=0)
    ck("HASH domain label and byte tag are one identity",
       label_res.domus_motion.bearing.lineage == byte_res.domus_motion.bearing.lineage
       and label_res.domus_motion.current_frequency == byte_res.domus_motion.current_frequency
       and label_res.domus_commitment == byte_res.domus_commitment
       and label_res.domus_aeon.identity == byte_res.domus_aeon.identity)

    try:
        C.living_domus_seal(
            res, 14, source_digest=dig, source_size=size, nonce=1,
            source_domain=RAW_FILE_SOURCE_DOMAIN)
    except ValueError:
        nonce_drift_rejected = True
    else:
        nonce_drift_rejected = False
    try:
        C.living_domus_seal(
            res, 14, source_digest=dig, source_size=size, nonce=0,
            source_domain=C.CANONICAL_SOURCE_DOMAIN)
    except ValueError:
        domain_drift_rejected = True
    else:
        domain_drift_rejected = False
    ck("DOMUS visible body rejects nonce and domain drift",
       nonce_drift_rejected and domain_drift_rejected)


    # MIRROR-MATH: the file is expanded Z1; its exact terminal depth-zero
    # Grimchain is compressed Z0 and returns without becoming fresh source debt.
    from TardiSHA.mirror_math import detect_terminal_self_glyph, mirror_file_emission
    with tempfile.TemporaryDirectory() as mirror_tmp:
        mirror_root = Path(mirror_tmp)
        mirror_body = b"the living body crossed the threshold and returned through its own face\n"
        mirror_plain = mirror_root / "plain.bin"
        mirror_plain.write_bytes(mirror_body)
        mirror_first = living_domus_for_source(mirror_plain, 0, kind="file")
        mirror_file = mirror_root / "returned.bin"
        mirror_file.write_bytes(mirror_body + mirror_first.encode("utf-8") + b"\n")
        mirror_result = mirror_file_emission(mirror_file)
        mirror_second = living_domus_for_source(mirror_file, 0, kind="file")
        ck("MIRROR exact terminal Z0 is recognized and folded",
           mirror_result.witness.candidate_detected
           and mirror_result.witness.exact_self_glyph
           and mirror_result.witness.folded)
        ck("MIRROR natural Grimchain fixed point",
           mirror_second == mirror_first)
        mirror_twice = mirror_root / "returned_twice.bin"
        mirror_twice.write_bytes(
            mirror_body + mirror_first.encode("utf-8") + b"\n"
            + mirror_first.encode("utf-8") + b"\n"
        )
        mirror_twice_result = mirror_file_emission(mirror_twice)
        ck("MIRROR append-only repeated return remains fixed",
           mirror_twice_result.witness.fold_count == 2
           and mirror_twice_result.witness.bytes_accounted
           and living_domus_for_source(mirror_twice, 0, kind="file") == mirror_first)
        ck("MIRROR physical bytes remain accounted while identity returns",
           mirror_result.witness.bytes_accounted
           and H.file_emission(mirror_file) != H.file_emission(mirror_plain)
           and mirror_result.emission == H.file_emission(mirror_plain))
        ck("MIRROR return closes at D-COMP zero and Truth one",
           mirror_result.witness.return_dcomp == 0
           and mirror_result.witness.truth == 1
           and mirror_result.witness.operator_order_preserved)
        # Derive a seal-shaped mutation that is independently proven non-exact.
        # A fixed center glyph is not a valid adversary because upstream in-Canon
        # mathematics can lawfully make that glyph exact at another depth.
        mirror_mutated = mirror_root / "mutated.bin"
        mirror_body_probe = mirror_root / "mutated-body.bin"
        invalid_body = list(mirror_first)
        invalid_body[1] = "⏣" if invalid_body[1] != "⏣" else "⬡"
        invalid_seal = "".join(invalid_body)
        mirror_mutated.write_bytes(mirror_body + invalid_seal.encode("utf-8") + b"\n")
        candidate = detect_terminal_self_glyph(mirror_mutated)
        if candidate is None:
            raise RuntimeError("deterministic non-exact Mirror adversary was not shape-readable")
        mirror_body_probe.write_bytes(mirror_mutated.read_bytes()[:candidate.body_size])
        expected = living_domus_for_source(mirror_body_probe, candidate.depth, kind="file")
        if candidate.seal == expected:
            raise RuntimeError("deterministic non-exact Mirror adversary unexpectedly verified")
        mirror_false = mirror_file_emission(mirror_mutated)
        ck("MIRROR seal-shaped but non-exact return remains source matter",
           mirror_false.witness.candidate_detected
           and not mirror_false.witness.exact_self_glyph
           and not mirror_false.witness.folded
           and mirror_false.emission == H.file_emission(mirror_mutated))
        ck("MIRROR node route returns to expanded Z1",
           node_from_file(mirror_file).route_witness == node_from_file(mirror_plain).route_witness)

    # NO-FORCE: prohibited forced-aperture machinery must remain absent.
    prohibited = (
        "APERTURE_OPEN", "APERTURE_CLOSE", "split_aperture", "seal_aperture",
        "file_body_fingerprint", "node_from_body", "embed_self_resolving_seal",
        "verify_self_resolving", "--embed", "--self-verify",
    )
    py_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore")
                        for path in Path("TardiSHA").glob("*.py"))
    ck("NO-FORCE no literal aperture/self-embed scaffolding", not any(x in py_text for x in prohibited))


    os.unlink(tf.name)
    total = len(PASS) + len(FAIL)
    print(f"TardiSHA self-test: {len(PASS)}/{total} pass")
    for x in FAIL:
        print("  FAIL:", x)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(run())
