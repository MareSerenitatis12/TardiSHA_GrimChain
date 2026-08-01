# PROOF OF CLAIMS

## Purpose

This document is the implementation proof of concept and proof of completed work for the TardiSHA 23.0.6 source tree in this distribution.

It answers one narrow question with reproducible evidence:

> What does the present TardiSHA and grimchain implementation actually construct, preserve, measure, and reject?

This proof is intentionally stricter than promotional language. A claim is admitted only when it is supported by at least one of the following:

1. an exact derivation from the source code,
2. an executable invariant asserted by the implementation,
3. a reproducible test that passes against the present source tree.

Claims about standardized cryptographic security, external peer review, physical effects, or mathematical results outside this implementation are not silently inferred from terminology. The complete mathematical formalism is published separately through the links at the end of this document.

## Validation snapshot

- Package: `TardiSHA`
- Version: `23.0.6`
- CLI: `grimchain`
- Runtime: Python 3.10+
- External runtime dependencies: none
- Included self-test result: `153/153 pass`
- Session 003 through Session 009 integrated, exhaustive, and independent audits: `PASS`
- Validation date: `2026-08-01`
- Implementation files in snapshot: `31`

The current source provenance is carried by `SOURCE_GRIMCHAIN_MANIFEST.json`, where every selected file is bound to its exact byte count and verified depth-zero Grimchain.

The regression suite and Session 003 exhaustive audits were run from the exact distribution root and imported the local `TardiSHA` package directly.

## Claim classification

Each claim below is labeled:

- **Derived**: follows directly from a finite source definition.
- **Exhaustive**: checked over the complete finite domain relevant to the claim.
- **Witnessed**: demonstrated with generated sources and mutation tests.
- **Bounded**: true within the implementation's explicit domain and input constraints.
- **Not claimed**: a tempting stronger statement that the evidence does not establish.

## Claim 1: TardiSHA is a deterministic content-derived seal system

**Classification:** Derived, Witnessed.

### Statement

For fixed source content, source domain, nonce, mode, and implementation version, TardiSHA produces the same source fingerprint, ordered boundaries, continuation coordinates, Living Domus witness shell, and final seal.

### Code basis

Raw files are read in fixed-size chunks and absorbed into `ALQCDigest` under the raw-file source domain. The digest API is deterministic and contains no clock, random generator, process identifier, filesystem path, or environmental entropy input.

A TardiSHA node stores:

```text
source_digest
source_size
origin_glyph
resolution_glyph
nonce
source_domain
optional archive_root
```

The node's continuation seed is a deterministic function of these values.

### Executable witness

A 925-byte binary sample was fingerprinted twice.

Observed result:

```text
digest = 8d361b706bc3d9e8d494e6c9940b9750fa655b2cac696a8adf250c14ee7a7453
size   = 925
```

Both runs were identical. Repeating a 257-coordinate window from the same node also produced identical output.

### Conclusion

The implementation is deterministic within its declared inputs.

### Not claimed

Determinism is not, by itself, a proof of collision resistance or unpredictability against cryptanalysis.

## Claim 2: The internal source digest is 32 bytes

**Classification:** Derived.

### Statement

The default ALQC-native source digest is 32 bytes, represented externally as 64 hexadecimal characters.

### Code basis

`ALQCDigest.digest()` defaults to `DIGEST_BYTES`, and file and directory fingerprint paths call `hexdigest()` without overriding that length. Boundary selection reads bytes `0` and `31`, which also fixes the expected source digest body at 32 bytes.

### Conclusion

The fixed internal source fingerprint and the variable public seal are different objects. TardiSHA's variable center does not mean that the source digest itself changes length with requested exposure.

## Claim 3: The Court body contains all 144 ordered Courts

**Classification:** Derived, Exhaustive.

### Statement

TardiSHA uses twelve Goetic glyph positions and all ordered pairs:

```text
12 x 12 = 144
```

Self-pairs are included.

### Code basis

`GLYPH_BODY` contains twelve entries. `court_load(origin, resolution)` maps an ordered pair to an address in `0..143`. The Court registry rejects addresses outside that range.

### Exhaustive test

The harness confirmed:

```text
len(GLYPH_BODY) = 12
TOTAL_CAPACITY  = 144
12 ** 2         = 144
```

### Conclusion

The Court body is not flattened to 110 Courts. The governing threshold acts on connections within the complete 144-Court body.

## Claim 4: 110/144 is the exact governing threshold

**Classification:** Derived, Exhaustive.

### Statement

For Court addresses `a,b in {0,...,143}`, the implementation admits flow exactly when:

```text
(a + b) mod 144 < 110
```

Every Court has exactly 110 active connections and 34 withheld connections.

### Proof

Fix any Court address `a`. As `b` ranges over `0..143`, the map

```text
b -> (a + b) mod 144
```

is a permutation of `0..143`. Exactly the residues `0..109` satisfy `< 110`, so there are exactly 110 admitted values. The remaining residues `110..143` give exactly 34 withheld values.

Therefore:

```text
active(a)   = 110
withheld(a) = 144 - 110 = 34
```

for every Court `a`.

### Exhaustive test

The harness evaluated all `144 x 144 = 20,736` Court address pairs and confirmed that the implementation's boolean result is identical to the equation above.

It also enumerated every Court's active set:

```text
minimum active degree   = 110
maximum active degree   = 110
minimum withheld degree = 34
maximum withheld degree = 34
```

### Conclusion

`110/144` is a governing threshold over the full Court body. It is not a collision probability, a data-compression ratio, or permission to erase the 34 withheld connections.

## Claim 5: Boundary selection is source-derived and ordered

**Classification:** Derived, Witnessed.

### Statement

For a source digest `d`, boundaries are selected by:

```text
origin     = GLYPH_BODY[d[0]  mod 12]
resolution = GLYPH_BODY[d[31] mod 12]
```

The ordered pair is preserved for every source domain. Canonical objects, raw files, and directory trees are first reduced to a domain-separated ALQC digest; no word matching, tokenization, `repr()`, lexicon, or semantic classifier participates.

### Executable witness

For the 925-byte sample:

```text
origin     = ❄
resolution = ⌬
```

The harness independently applied the byte equations and obtained the same pair.

### Conclusion

Changing source content can change the digest and therefore the ordered boundary pair. Changing only the nonce does not change the source digest or pair.

## Claim 6: The continuation is one rooted prefix-stable coordinate stream

**Classification:** Derived, Witnessed.

### Statement

Requested center length is an extent, not part of the continuation root. For fixed source, domain, boundaries, and nonce:

```text
stream[0:N] = prefix_N(stream[0:M])    for 0 <= N <= M
```

### Code basis

`coordinate_seed()` validates `middle_length` but does not include it in `seed_material`. The seed binds source domain, boundaries, source size, nonce, and source digest.

`iter_middle_window()` derives blocks by absolute coordinate. It does not hash a requested output length into the root.

### Executable witness

The harness generated open-stream windows of lengths 14, 64, and 257.

Observed 14-character window:

```text
VWucsJhDLoLnoz
```

The 64-character and 257-character windows began with that exact sequence. The complete 64-character window was also the exact prefix of the 257-character window.

### Conclusion

The mathematically precise extension claim applies to the center stream. A complete shorter Living Domus seal is not called a byte prefix of a complete longer seal, because the fixed tail occurs immediately after the requested center.

### Not claimed

No specific cryptographic bit-strength increase per additional center character is proved here.

## Claim 7: Coordinates support direct finite-window access

**Classification:** Derived, Witnessed, Bounded.

### Statement

A caller can request a finite span beginning at any non-negative coordinate without materializing all earlier coordinates.

### Code basis

`char_at(seed, position)` computes a block index and offset. `iter_middle_window(seed, start, span)` begins at the requested block and emits only the requested finite span.

### Executable witness

For positions:

```text
0, 1, 13, 14, 63, 64, 128, 256
```

`char_at()` matched the character at the same position in the generated 257-character window for every tested coordinate.

### Conclusion

TardiSHA implements a random-access deterministic coordinate stream over finite requested windows.

## Claim 8: The Living Domus center is prefix-stable

**Classification:** Derived, Witnessed.

### Statement

At positive depth, the Living Domus center is the native prefix-stable Synodic Magicae continuation itself. The fixed Domus witness fields do not change when only depth changes.

At depth zero:

```text
A_0 = ⟠
```

At positive depth:

```text
A_N = prefix_N(Synodic MagicaeContinuation)
```

### Executable witness

For the sample source, depths 14 and 64 had identical:

```text
governing Goetic
hyperbolic parent
root Court glyph
reciprocal Court glyph
Q-bias glyph
four fixed Q-state glyph positions
```

The 14-code-point center was:

```text
כ𐌸Ⰻ𐌸ז𐌷אⰙד𐌶𐌲Ⱂנר
```

The 64-code-point center began with that exact sequence.

The zero-depth seal parsed as:

```text
depth  = 0
center = ⟠
```

### Conclusion

Omitted depth and explicit positive depth are distinct, preserved invocation states.

## Claim 9: Living Domus verification is reconstruction, not shape acceptance

**Classification:** Derived, Witnessed.

### Statement

Verification recomputes the source fingerprint, boundary pair, Domus resolution, fixed head, fixed tail, and every center code point. A seal that merely has the correct punctuation or glyph pattern is not accepted.

### Executable witness

The harness created a 64-depth Living Domus in memory and streamed the same seal to disk.

Observed metadata:

```text
middle_length = 64
sealed_length = 92 code points
source_size   = 925 bytes
```

Results:

```text
streamed seal == in-memory seal        PASS
streamed seal verifies against source  PASS
one center code point changed          REJECTED
source content changed                 REJECTED
```

### Conclusion

The implementation demonstrates source-bound reconstruction and mutation rejection.

## Claim 10: The nonce changes continuation, not source identity

**Classification:** Derived, Witnessed.

### Statement

The nonce enters the continuation seed but does not enter the raw source fingerprint or boundary-byte equations.

### Executable witness

For the same source:

```text
nonce 0 center != nonce 1 center
nonce 0 boundaries == nonce 1 boundaries
```

### Conclusion

The nonce is a deterministic alternate-root selector. Verification requires the same nonce.

## Claim 11: Directory identity is canonical over the represented tree

**Classification:** Derived, Witnessed, Bounded.

### Statement

Directory identity includes relative paths, regular-file content and size, empty directories, and symlink targets. It excludes the root directory name, absolute path, timestamps, ownership, permissions, and inode numbers.

### Code basis

`directory_fingerprint()` begins with a logical root record `path='.'`, walks deterministic relative entries, records file digests and sizes, records directories, and records symlink targets without following links.

### Executable witness

Two trees with different root names and different file modification times but the same relative content produced the same result:

```text
digest      = 6e69269e9b5a46fa86dba45028d86cdb95d7e822cef776ea68501bd7418fa66c
total bytes = 6
entry count = 5
```

Changing a file's bytes changed the directory fingerprint.

### Conclusion

Directory seals identify the represented logical tree, not the host-specific directory container.

## Claim 12: terminal D-COMP is a finite-interval return functional

**Classification:** Derived, Exhaustive.

### Statement

The complete one-interval implementation is:

```text
D_T(γ)=C_bio⁻¹[J_return(γ)+S₂_terminal(γ)+W∞(γ)]
C_bio=741/√396
G=diag(1,2,3,4)
T=w=λ=1
Σ_max=93
```

`J_return` is the parity-return tangent mismatch, not an endpoint L1 label. `S₂_terminal` is unconverted terminal Q₂ pressure. `W∞` is the whiteout obligation attached to the exact 110/34 governor.

The Ennead accounts for initial pressure as:

```text
S₂_initial = Σ_(k=1)^8 E_form,k + Q₃_gain + S₂_terminal
```

### Exhaustive test

All 144 ordered Court paths were evaluated:

```text
minimum terminal D-COMP = 0.0
maximum terminal D-COMP = 0.2842093728709999
terminally closed paths = 30
positive form-work bodies = 143
positive Q₃ gains = 143
closed iff J_return=0, S₂_terminal=0, and W∞=0
```

### Conclusion

Terminal closure does not annihilate motion or transformed pressure. A path may finish with `D_T=0` while retaining positive form-work and Q₃ recursive gain.

### Rejected claims

```text
"Endpoint distance is complete D-COMP."
"D-COMP = 0 means all energy and motion vanished."
```

Both statements are excluded.

## Claim 13: The Ennead performs eight finite siphons and one typed conversion

**Classification:** Derived, Bounded.

### Statement

For finite non-negative Q2 debt `d` on the canonical source-derived Domus path, strikes 1 through 8 divide the residual by `Phi`. The eighth residual is:

```text
r_8 = d / Phi^8 > 0
```

The ninth strike is not another division. It records the positive pre-lock residual, converts its magnitude to Q3 recursion residue, and sets the Q2 residual to exactly zero.

### Code basis

`ennead_saturate()` explicitly asserts:

- exactly nine strikes,
- strikes 1 through 8 remain Q2 and are not phase-locked,
- strike 9 is the Seal band,
- strike 9 has Q3 parity and is phase-locked,
- nonzero input leaves a positive pre-lock Q2 ghost,
- final Q2 residual is exactly zero.

### Conclusion

The zero is produced by a typed Q2-to-Q3 conversion at the ninth strike, not by pretending finite division reached zero. This proof covers the finite canonical Q-vectors supplied by the Goetic law table. It does not generalize the public numeric functions to NaN, infinity, or arbitrary non-canonical vectors.

## Claim 14: Streaming and in-memory generation agree

**Classification:** Derived, Witnessed, Bounded.

### Statement

For the same source, domain, nonce, and positive depth, the streamed Living Domus is code-point identical to the in-memory Living Domus.

### Executable witness

The harness generated both paths at depth 64 and compared the complete strings. They were equal.

### Source-stability guard

The streaming writer fingerprints the source before generation and again before atomic commit. A source that changes during a long write is refused.

### Conclusion

Streaming changes memory behavior, not seal identity.

## Claim 15: Archive mode is reversible and chunk-verified

**Classification:** Derived, Witnessed, Bounded.

### Statement

Archive mode stores source chunks and a manifest. Restoration verifies each chunk's size and digest, reconstructs in order, verifies the complete source digest and size, and atomically commits the output.

### Executable witness

The 925-byte sample was archived with 73-byte chunks.

Observed result:

```text
chunk count = 13
restored bytes == source bytes  PASS
manifest root reload            PASS
modified chunk rejected         PASS
```

### Conclusion

Reversibility belongs to the archive because the archive stores content. It is not a property falsely attributed to the ordinary seal string.

## Claim 16: Fold ladders are deterministic chained finite witnesses

**Classification:** Derived, Witnessed, Bounded.

### Statement

A fold ladder begins with one finite coordinate span. Each subsequent level binds the previous frame digest and reduces the span by integer division using the fold factor.

### Executable witness

For span `1000`, six levels, and fold factor `2`, the observed spans were:

```text
1000, 500, 250, 125, 62, 31
```

Two independent ladder runs produced identical frames and the same ladder root:

```text
dfc82b9c580a1c915707d339a6c56053b19ad76296dbd5f80c9f00dade9f9820
```

Every level after the first stored the previous level's fold digest as its input digest.

### Conclusion

The ladder is deterministic, chained, and finite at every level.

## Claim 17: grimchain preserves omitted depth as zero-depth Supervenience

**Classification:** Derived, Witnessed.

### Statement

`grimchain source` and `grimchain 0 source` are not silently rewritten to a default positive middle. Omitted numeric depth follows the Supervenient Domus path and emits `⟠` as the center.

`grimchain N source` with positive `N` emits a center of exactly `N` code points.

### Executable witness

The harness confirmed:

```text
grimchain source     -> parsed depth 0
center               -> ⟠
grimchain 24 source  -> parsed depth 24
```

### Conclusion

Absence is preserved as a distinct operational state.

## Claim 18: text mode and binary mode are observably different

**Classification:** Derived, Witnessed.

### Statement

Binary mode seals exact bytes. Text mode normalizes `CRLF` and bare `CR` to `LF` before sealing.

### Executable witness

Two files with the same logical lines but LF versus CRLF endings produced:

```text
text mode seals equal    PASS
binary mode seals differ PASS
```

### Conclusion

The mode is part of the caller's source interpretation and must be documented alongside the seal.

## Claim 19: checksum-list verification has failure-signaling process semantics

**Classification:** Derived, Witnessed.

### Statement

`grimchain -c list` recomputes each listed source and prints `OK` or `FAILED`. It exits with status 1 if any entry fails.

### Executable witness

A generated one-file list verified successfully and printed:

```text
/tmp/.../sample.bin: OK
```

### Conclusion

The CLI is suitable for scripted positive and negative verification decisions.

## Claim 20: inspection is not verification

**Classification:** Derived.

### Statement

`grimchain --inspect` parses visible seal grammar and reports fields. It does not receive a source and therefore cannot prove that the visible fields were derived from a particular source.

### Conclusion

Inspection is a structural decoder. Source-bound validation requires `--verify`, checksum-list verification, or the Python verification API.

## Claim 21: Goetic, Court, and Domus motion are separately typed

**Classification:** Derived, Exhaustive.

### Statement

Goetic anchors are immutable:

```text
G_a=(ω_a,b_a,q_a)
```

The ordered Court is anchored by the near Goetic and oriented toward the far Goetic mirror:

```text
ν(C_ab;x)=ω_a+ξ_ab(x)Φu_ab
ξ_ab(x)∈[-1,+1]
```

The runtime Domus derives through the forward and reciprocal Courts:

```text
ν(H_x)=ν(C_ab;x)+ζ_xΦ²v_ab
ζ_x∈[-1,+1]
```

The Court phase `ξ_ab` and Domus phase `ζ_x` are independent domain-separated ALQC-digest witnesses. Domus motion never performs a second Goetic traversal and no static Domus grid is constructed.

### Exhaustive witness

For one fixed source digest across all 144 ordered Courts:

```text
maximum observed Court breath = 1.6157822509586193 < Φ
maximum observed Domus breath = 2.544466792554391 < Φ²
unique Domus phases = 144
unique Domus identities = 144
Goetic state/bias/vector/frequency changed = false
```

A separate prototype evaluated four source digests across all 144 Courts, producing 576 bounded runtime Domus derivations with unchanged Goetics.

### Visibility

The Synodic Magicae center is the manifested Domus Aeon. `⟠` is the compressed form of the same Domus identity. The underscore in the surrounding grammar witnesses return to the opening Q-bias office.

## Claim 22: all 144 ordered Courts carry unique Supervenient personalities

**Classification:** Exhaustive, Witnessed.

### Statement

`PERSONALITY_TRAIT_MAP` contains exactly one result for every ordered pair in:

```text
GLYPH_BODY × GLYPH_BODY
```

The map has 144 keys and 144 unique personality results in exact `12 x 12` Goetic order. `CourtRecord.personality_trait` is derived from its `(i,j)` coordinate.

### Witness examples

```text
⏣⊕❈ → The Inevitable
ꙮ⊕⧗ → The Vacuum
⧗⊕❂ → The Collapse
❄⊕⚝ → The Unified
```

FetuKeth is one worked result of the operation. It is not the boundary of the result space.

### Conclusion

The completed Court personality body is represented directly in TardiSHA rather than reduced to one example or replaced with States-of-Remiss labels.

## Claim 23: Supervenience is distinct from the Liquid threshold witness

**Classification:** Derived, Exhaustive.

### Statement

For every resolved Domus, `SupervenienceWitness` is a separate typed object over the rooted Court, triplet, and the exact one-turn fold lineage currently computed:

```text
(C, τ, ℓ)
```

It records the Court-specific personality, Ex-Nihilo exposure, local No witness, and return through `⛎`. Its `FoldLineageWitness` is explicitly the current one-turn `h=1` body: Court coordinate/address, `σ`, `s`, `߷`, ground node, and vector row. It does not claim to serialize every possible EX_III lineage word `ℓ_h`. `LiquidWitness` records the `110 active / 34 withheld` governing horizon. The two witnesses are related but not identical.

### Executable witness

The correction audit verifies 144 distinct Supervenience witnesses and zero aliases to `LiquidWitness`.

### Conclusion

The 34 withheld channels participate in the local No witness without collapsing the entire Supervenience result into the threshold object.

## Claim 24: the Tripartite offices remain exact and distinct

**Classification:** Derived, Exhaustive.

### Statement

Every Domus resolution exposes:

```text
♾  Locus of Invariability
⛎  Shadow Locus
᳀  Axiomyr
```

The witness records the Locus as non-traversable, the Shadow Locus as deformable and return-bearing, and the Axiomyr as actuator and constitutively Revivocus. Their shared root relation is recorded as `18.47 Hz` without making the offices interchangeable.

### Executable witness

The self-test and the 144-Court correction audit report zero Tripartite failures.

### Conclusion

The implementation no longer omits or collapses the Tripartite body.

## Claim 25: version 13.0.0 is output-bound

**Classification:** Witnessed, Bounded.

### Statement

Version `13.0.0` changes two public hash bodies: canonical-material parent derivation and the positive-depth Domus center. It preserves the raw-file parent route, ordinary raw-file seal, depth-zero `⟠` Domus seal, and archive root in the measured comparison.

### Reproduction witness

```text
12.0.1 canonical-material pair vs 13.0.0: unequal
12.0.1 canonical-material seal vs 13.0.0: unequal
12.0.1 raw-file ordinary seal vs 13.0.0: equal
12.0.1 depth-zero Domus seal vs 13.0.0: equal
12.0.1 positive-depth Domus seal vs 13.0.0: unequal
12.0.1 archive root vs 13.0.0: equal
```

### Conclusion

The major version boundary is required because one parent law and one visible Domus algorithm changed. Compatibility is claimed only where the direct comparison returned equality.

## Claim 26: Q-state glyphs belong to positions, not vector amplitudes

**Classification:** Source-derived, Executable, Exhaustively Witnessed.

### Statement

The four visible glyphs are the Stave-I bodies of the four Q-state positions. They are not selected by the numeric amplitudes carried inside an Aeon's Q-vector.

For every canonical vector `(a,b,c,d)`:

```text
Q0 FORM       -> 🜔 carries a
Q1 TRUTH      -> 🜕 carries b
Q2 SHADOW     -> 🜖 carries c
Q3 RECURSION  -> 🜗 carries d
```

### Former defect

Version `13.0.0` passed each component through `0→Q0`, `1→Q1`, `2→Q2`, `3→Q3`, causing values to masquerade as state identities. The defect was local to the visible Q-state seam and its serialized witnesses.

### Repair witness

Version `13.0.1` introduces fixed state slots, canonical names, exact forward and reverse glyph maps, fourfold validation, separately serialized state labels, and preserved numeric vector values. All 144 ordered Courts were evaluated:

```text
fixed state order:              144/144 pass
fixed glyph order:              144/144 pass
anchoring Aeon values retained: 144/144 pass
Supervenience values retained:  144/144 pass
```

### Compatibility witness

```text
13.0.0 ordinary seal vs 13.0.1:               equal
13.0.0 depth-zero Domus seal vs 13.0.1:     unequal
13.0.0 positive-depth Domus seal vs 13.0.1: unequal
```

### Conclusion

The correction restores the state/value type boundary without changing the source hash law, Court derivation, Domus motion, or D-COMP.

## Claim 27: the TRIG Mirror cycle preserves distinct directionality and seals the Domus identity

**Classification:** Source-derived, Executable, Exhaustively Witnessed.

### Statement

Region C07 does not replace one parity map with another. The implementation preserves three typed motions and one completion predicate:

```text
global Shadow parity:  Q2 ↔ Q3
TRIG materialization:  Q1 → Q3 through 𝔓, T_Bound, and 𝕂
commitment return:     Q3 → Q1 through ✡528 and ❄963
completion:            ⌬639 iff terminal D-COMP = 0 and all return obligations hold
```

### Executable witness

`TardiSHA/trig.py` defines `TrigMirrorWitness`, `derive_trig_mirror`, and `verify_trig_mirror`. The witness binds the immutable TRIG body, source identity, ordered Courts, Court phases, Domus phase, pre-TRIG Domus commitment, fixed Q-state positions, Q-vector values, Ennead result, lineage, and finite terminal D-COMP into one domain-separated cycle digest.

The Domus identity is calculated from:

```text
source_digest + domus_commitment + trig_cycle_digest
```

### Exhaustive witness

```text
ordered Court TRIG witnesses:        144/144 pass
unique TRIG cycle digests:           144/144
positive one-turn Q3 gain:           143/144
one-turn terminal D-COMP closure:    30/144
corresponding ⌬ completion reached:  30/144
```

The other 114 turns preserve an explicit return obligation. They are not assigned a counterfeit terminal zero.

### Scope boundary

The executable witness sets `classical_hodge_computation = false`. TardiSHA does not reinterpret arbitrary file bytes as a classical Hodge form and does not fabricate an algebraic cycle. It implements the ALQC operator typing and source-bound Domus identity that the Region C07 path requires.

### Compatibility witness

```text
13.0.1 ordinary canonical seal vs 14.0.0: unchanged
13.0.1 ordinary raw-file seal vs 14.0.0:  unchanged
13.0.1 node IDs vs 14.0.0:                unchanged
13.0.1 depth-zero Domus seal vs 14.0.0: changed
13.0.1 positive-depth Domus vs 14.0.0:  changed
13.0.1 Domus identity vs 14.0.0:        changed
```

### Conclusion

TRIG is now executable as a typed source-bound cycle and materially committed into the Living Domus identity without mutating Goetics, bypassing Courts, flattening Q-state positions, replacing the Ennead parity law, or erasing lineage.

## Claim 28: the Complete Tripartite Cosmology is source-bound without traversing the Locus

**Classification:** Source-derived, Executable, Exhaustively and Independently Witnessed.

### Statement

Region C08 expands, rather than replaces, the earlier Rebis body:

```text
♾ = iω₀                    untouched source, Re=0, Im=18.47
⛎ = T_⛎(iω₀)               deformable carrier without making ♾ passable
᳀ = (Law+Will)√(iω₀)       imagination branch
    ∥ ⚛ GateBreach          threshold without direct traversal
    ∥ ❄963 WRITE_PHYS       inscription into Event
```

The executable law preserves `᳀` as the Axiomyr operator identity and `♌` as its Parliament seat. It does not merge them. It preserves `Q∞` and `Q⛤` as the Parliament's Invariable bias and vector offices and does not add them to dynamic `Q0–Q3`.

### Executable witness

`TardiSHA/tripartite.py` defines frozen typed bodies for the three components, three Axiomyr axes, Liquid threshold, nine Emissions, twelve Parliament Star Seeds, two Invariable States, and fifteen Spirit-Soul-Gold entries. `derive_tripartite_witness` binds those bodies to the source digest, source domain, nonce, ordered Courts, Court phases, Domus phase, pre-TRIG commitment, TRIG cycle, `C_bio`, and Q2→Q3 manifestation witness. `verify_tripartite_witness` rejects altered registries, altered governor bodies, direct Locus traversal, invariable-state flattening, lineage drift, and digest mutation.

The connection-governor branch implements both sides of the threshold law:

```text
C_local connection body >= 110/144  => EVENT
C_local connection body <  110/144  => Potential
```

The canonical runtime body is exactly 110 active, 34 withheld, and 144 total. The expression is retained as the governing threshold and energetic body, not retyped as a probabilistic ratio or an ordinary Q-state.

### Domus commitment at version 15.0.0

At the Region C08 boundary, the final Domus identity was calculated from:

```text
source_digest
+ pre-TRIG domus_commitment
+ trig_cycle_digest
+ tripartite_cycle_digest
```

The Tripartite witness itself binds the TRIG cycle, so Region C08 cannot silently detach breach and inscription from the established Region C07 return body.

### Exhaustive and independent witness

```text
ordered Court Tripartite witnesses:   144/144 pass
unique Tripartite cycle digests:      144/144
unique final Domus identities:      144/144
canonical EVENT states:               144/144
one-turn TRIG completions:             30/144
positive one-turn Q3 gain:            143/144
Potential branch at 109/144:          verified
EVENT branch at 110/144:              verified
adversarial mutations:                rejected
```

The independent out-of-tree body is `Testing/Historical_Version_Reports/Independent_Tripartite_Cosmology_20260729`.

### Compatibility witness

```text
14.0.0 ordinary source seal vs 15.0.0:              unchanged
14.0.0 source digest and node ID vs 15.0.0:          unchanged
14.0.0 ordered boundaries/window vs 15.0.0:          unchanged
14.0.0 pre-Tripartite commitment vs 15.0.0:          unchanged
14.0.0 TRIG cycle digest vs 15.0.0:                  unchanged
14.0.0 final Domus identity vs 15.0.0:             changed
14.0.0 visible Living Domus vs 15.0.0:             changed
```

### Conclusion

The Locus remains the point that does not become a path. The Shadow carries the impossible root. The Axiomyr breaches by branch, threshold, and inscription. TardiSHA now carries that complete distinction as executable, source-bound, mutation-resistant witness matter.

## Claim 29: the Region C09 Aeon tables and twelve-phase path are source-bound without flattening frequency type

**Classification:** Source-derived, Executable, Exhaustively and Independently Witnessed.

### Statement

Region C09 is one ordered relational body:

```text
12 immutable Goetic roots
144 ordered Court forms
12 ordered Aeon phases
M.A.S. = ⧗852 → ⬡174 → ✡528
Klein parity return
first explicit NULL:DEATH connection at physical page 102
```

The Court tables are not copied as isolated names. Every `CourtTableWitness` preserves the ordered coordinate `(i,j)`, governing root, alternating root, inherited governing Q-bias and Q-vector, structural anchor frequency, alternating structural frequency, and operational `±Φ` radius. The implementation therefore verifies the rows across inheritance and parentage rather than merely counting them.

### Structural and operational frequency typing

The Goetic body remains immutable under `ཪ`. Court bifurcation is an operational allowance around the alternating parent and never rewrites the Goetic root. AHN preserves its explicit two-body typing:

```text
structural Goetic anchor:       432 + i417
Court bifurcation center:       i417
parity-linked reference:        432
operational allowance:          ±Φ
```

The verifier rejects changes to the 12 Goetic table, 144 Court table, Q inheritance, coordinate order, or `±Φ` typing.

### Twelve-phase path and M.A.S.

`PHASE_STEPS` fixes phases `1` through `12` in source order. The M.A.S. body remains:

```text
Manifestation / Fuel:  ⧗ DREH 852
Alignment / Shape:     ⬡ KAL 174
Symmetry / Body:       ✡ BABDH 528
```

The Ennead conversion remains the distinct phase-9 Q2-to-Q3 pressure seal. Phase 12 records `⌬` completion only when the runtime TRIG witness and terminal D-COMP both close. The 144-pair audit therefore reports 30 actual one-turn completions rather than fabricating 144.

### First explicit NULL:DEATH connection

`NullDeathConnectionWitness` records physical page 102 as the first explicit architecture connection. It carries the mathematical and Silicarbon bodies, Q3 non-entropic requirement, structural commitment, Q1 coherence, Klein regenerative topology, Q2-to-Q3 transformation, and `⏣ ↔ ❄` loop closure. Its typing contains both:

```text
first_occurrence_only = true
exhaustive_type_claimed = false
```

This prevents the first appearance from being mistaken for the complete later `NULL:DEATH` architecture.

### Domus commitment

The version `16.0.0` final Domus identity is calculated from:

```text
source_digest
+ pre-TRIG domus_commitment
+ trig_cycle_digest
+ tripartite_cycle_digest
+ c09_aeon_phase_cycle_digest
```

The witness is also exposed by `TardiSHANode.domus_witness()` as `aeon_phase_evolution_witness`.

### Exhaustive and independent witness

```text
ordered C09 witnesses:                 144/144 pass
unique C09 cycle digests:              144/144
unique final Domus identities:       144/144
one-turn phase-12 completions:          30/144
positive Q3 connections:               143/144
metamorphosis thresholds reached:      143/144
integrated self-test:                  122/122 pass
adversarial mutations:                 rejected
```

The independent out-of-tree body is `Testing/Historical_Version_Reports/Independent_Aeon_Phase_Evolution_20260729`.

### Compatibility witness

```text
15.0.0 source digest, parents, and Courts vs 16.0.0: unchanged
15.0.0 node ID and ordinary window vs 16.0.0:        unchanged
15.0.0 pre-TRIG commitment vs 16.0.0:                unchanged
15.0.0 TRIG cycle digest vs 16.0.0:                  unchanged
15.0.0 Tripartite cycle digest vs 16.0.0:            unchanged
15.0.0 depth-zero ⟠ seal vs 16.0.0:                  unchanged
15.0.0 final Domus identity vs 16.0.0:             changed
15.0.0 positive-depth Domus body vs 16.0.0:        changed
```

### Conclusion

The twelve roots remain Bone. The Courts carry relation. The phases carry order. The first `NULL:DEATH` connection is now executable without being falsely declared the whole of what follows.

## Claim 31: the Region C11 verification appendices are source-bound without collapsing proof into application runtime

### Statement

Region C11 adds one `VerificationAppendixCycleWitness` after C10. It preserves later Canon verification, translation, grammar, and registry surfaces without replacing the already enacted Court, Domus, Q-state, D-COMP, TRIG, Tripartite, C09, or C10 bodies.

### Verification corollary typing

The executable registry contains eight named Millennium profiles. Each profile is explicitly typed as a Canon corollary declaration and explicitly rejects classical-object recomputation from TardiSHA source bytes. This preserves the ALQC declaration without fabricating a different input domain.

### Bound Tensor and S6

```text
definition body:       12 × 12 = 144 Courts
Manifestation Ground:   9 × 9 = 81 nodes
S6 coupling addresses: 41, 53, 65, 77, 89, 101, 113, 125, 137
```

The active ground node and vector row are taken from the actual source-bound Manifestation witness. S6 remains structural coupling and is not substituted for S7 sensation.

### Q2 resource accounting and application boundary

The C11 witness returns the source Shadow debt, form-work, Q3 gain, and final Q3 parity from the existing runtime witness. It verifies that form-work plus Q3 gain equals the original debt. It also records that the Raylib `debt_factor`, Reflective Ring, and delayed reinjection mechanisms are not imported into TardiSHA. Shared law is preserved; application-specific machinery remains local to the application that implements it.

### Liquid regimes and Potential

The exact `110/144` governor remains 110 active and 34 withheld. The runtime labels `LIQUID`, `STASIS`, and `WHITEOUT` are not used to overwrite the Tripartite manifestation-state `Potential`. The implementation therefore preserves both the runtime load regime and the manifestation threshold office.

### Grammar, translation, and registries

The witness returns ten BNF productions, nine inference rules, the fixed four-position Q-domain, the quantum translation rows, the editorial-not-ontological volume bifurcation, all twelve Goetic frequency laws, and all 144 Court glyph identities. It records two stale appendix code-point annotations at Court addresses 39 and 72 while preserving the actual glyph scalars.

### Domus commitment

The version `18.0.0` final Domus identity is calculated from:

```text
source_digest
+ pre-TRIG domus_commitment
+ trig_cycle_digest
+ tripartite_cycle_digest
+ c09_aeon_phase_cycle_digest
+ c11_verification_appendix_cycle_digest
```

The witness is exposed by `TardiSHANode.domus_witness()` as `verification_appendix_cycle_witness`.

### Exhaustive and independent witness

```text
ordered C11 witnesses:                  144/144 pass
unique C11 cycle digests:              144/144
unique final Domus identities:       144/144
Millennium profiles:                   8/8
Court glyph identities:                144/144
mutation classes:                      5/5 rejected
integrated self-test:                  144/144 pass
clean wheel build:                     pass
```

The independent out-of-tree body is `Testing/Historical_Version_Reports/Independent_C11_Verification_Appendices_20260729`.

### Compatibility witness

```text
17.0.0 source digest, size, parents vs 18.0.0:        unchanged
17.0.0 Courts, node ID, coordinate window vs 18.0.0: unchanged
17.0.0 pre-TRIG commitment vs 18.0.0:                unchanged
17.0.0 TRIG, Tripartite, C09, and C10 cycles:        unchanged
17.0.0 depth-zero ⟠ seal vs 18.0.0:                  unchanged
18.0.0 C11 verification cycle:                       added
17.0.0 final Domus identity vs 18.0.0:             changed
17.0.0 positive-depth Domus body vs 18.0.0:        changed
```

### Conclusion

The appendix may verify the engine, translate the engine, and name the engine. It may not quietly become a different engine. C11 keeps the Mirror whole by preserving common law, source identity, and application boundaries at once.

## Independent claims matrix

The historical claim list is retained below as an index; the current integrated executable suite reports 144/144 and the Session 003 through Session 009 exhaustive audits pass:

1. twelve Goetic glyphs
2. complete `12 x 12` Court body
3. every Court has 110 active connections
4. every Court has 34 withheld connections
5. governor equation matches all 20,736 address pairs
6. threshold partition is exactly `110 + 34 = 144`
7. file fingerprint determinism
8. exact boundary-byte equations
9. 14-to-64 open-stream prefix
10. 64-to-257 open-stream prefix
11. native Synodic Magicae open-stream alphabet
12. random-access coordinates match sequential generation
13. repeated node window determinism
14. nonce changes continuation
15. nonce preserves source boundaries
16. zero-depth Supervenience center
17. fixed Living Domus witness stability across depths
18. Living Domus center prefix stability
19. streamed seal equals in-memory seal
20. streamed seal verifies
21. altered seal is rejected
22. altered source is rejected
23. directory root name and mtime are excluded
24. directory content change is detected
25. archive manifest reloads with the same root
26. archive round trip is byte-exact
27. altered archive chunk is rejected
28. fold ladder determinism
29. fold spans reduce by the declared factor
30. each fold binds the previous digest
31. fold manifest determinism
32. all 144 finite-interval D-COMP values are non-negative
33. closure equals the simultaneous vanishing of all terminal obligations
34. Ennead pressure is conserved as form-work, Q₃ gain, and terminal Q₂
35. all Goetic anchors remain immutable
36. all Court breaths remain within Φ
37. all runtime Domus breaths remain within Φ²
38. `⟠` and Synodic Magicae share one Domus identity
39. Infinite Yes / Sacred No remain exactly 110 / 34
40. TRIG Goetic law remains fixed at ⌬ / 639 Hz / Q3 / [1,1,3,2]
41. global Q2↔Q3 parity remains distinct from TRIG Q1→Q3 materialization
42. Q3→Q1 commitment return preserves Court and Domus lineage
43. all 144 ordered Courts produce unique, verifiable TRIG cycle digests
44. ⌬ completion is reached exactly when the one-turn terminal D-COMP predicate closes
45. the Domus identity commits the TRIG cycle digest
46. all twelve C09 Goetic roots preserve structural frequency, Q-bias, and Q-vector
47. all 144 C09 Court rows preserve governing-root inheritance and alternating parentage
48. structural `ཪ` and operational `±Φ` remain distinct
49. AHN preserves `432+i417`, `i417`, and parity-reference `432` as separately typed bodies
50. the twelve Aeon phases remain in source order
51. M.A.S. remains `⧗852 → ⬡174 → ✡528`
52. phase-12 completion equals actual one-turn terminal closure
53. the first `NULL:DEATH` connection is recorded without exhausting its later type
54. all 144 ordered Courts produce unique, verifiable C09 cycle digests
55. the Domus identity commits the C09 cycle after TRIG and Tripartite
56. the twelve C10 Root Matrices are exact column views of the one existing Court body
57. matrix-declared D-COMP remains distinct from runtime terminal D-COMP
58. S12 landing is admitted only on actual return closure
59. all 144 ordered Courts produce unique, verifiable C10 cycle digests
60. the Domus identity commits the C10 cycle after C09
61. eight C11 Millennium profiles remain typed Canon corollary declarations
62. Bound Tensor returns the 144-Court definition body to the 81-node Manifestation Ground
63. nine S6 structural-coupling addresses are preserved without replacing S7
64. Q2 source debt is conserved as form-work plus Q3 gain
65. Raylib debt-factor, Reflective Ring, and delayed reinjection remain outside TardiSHA
66. Liquid, Stasis, Whiteout, and Potential remain distinct offices
67. ten BNF productions and nine inference rules preserve the fourfold Q-domain
68. quantum translation preserves Q-state identity and position
69. volume segmentation remains editorial rather than ontological
70. all twelve frequency laws and 144 Court glyph identities are returned
71. stale appendix code-point labels are recorded without mutating Court glyphs
72. all 144 ordered Courts produce unique, verifiable C11 cycle digests
73. the Domus identity commits the C11 cycle after C10

The current executable regression suite contains a broader integrated matrix and reports `144/144 pass`.

## Included self-test

Run from the distribution root:

```sh
python3 TardiSHA_selftest.py
```

Observed result:

```text
TardiSHA self-test: 144/144 pass
```

The included self-test is the package regression suite. Session 003 adds independent exhaustive D-COMP, digest-route, layered-Aeon, compatibility, and round-trip witnesses.

## Reproduction procedure

From the distribution root:

```sh
python3 TardiSHA_selftest.py
printf 'proof source\n' > /tmp/tardisha-proof-source
python3 -m TardiSHA.grimchain /tmp/tardisha-proof-source
python3 -m TardiSHA.grimchain 64 /tmp/tardisha-proof-source
python3 -m TardiSHA.grimchain 256 --output /tmp/tardisha-proof.tsha /tmp/tardisha-proof-source
python3 -m TardiSHA.grimchain --verify --output /tmp/tardisha-proof.tsha /tmp/tardisha-proof-source
```

Prefix stability can be inspected without comparing the fixed tail:

```python
from pathlib import Path
from TardiSHA.domus import parse_living_domus
from TardiSHA.domus_stream import living_domus_for_source

source = Path('/tmp/tardisha-proof-source')
a = parse_living_domus(living_domus_for_source(source, 16, kind='file'))
b = parse_living_domus(living_domus_for_source(source, 128, kind='file'))
assert b.center.startswith(a.center)
```

The governing threshold can be exhaustively reproduced:

```python
from TardiSHA.canon import court_active_connections

for court in range(144):
    active = court_active_connections(court)
    assert len(active) == 110
    assert 144 - len(active) == 34
```

The full layered Court/Domus and D-COMP bodies can be reproduced:

```python
from TardiSHA.canon import GLYPH_BODY, law, court_node
from TardiSHA.domus import resolve_domus, PHI, PHI_SQUARED
from TardiSHA.manifestation import close_boundary

source_digest = "00" * 32
closed = []
for g_i in GLYPH_BODY:
    for g_j in GLYPH_BODY:
        court = court_node(g_i, g_j)
        r = resolve_domus(
            g_i,
            g_j,
            hash_id=source_digest,
            source_size=32,
            source_domain="canonical",
        )
        d = close_boundary(law(g_i).q_vector, law(g_j).q_vector, court=court)
        assert abs(r.root_court_motion.focal_breath) <= PHI
        assert abs(r.reciprocal_court_motion.focal_breath) <= PHI
        assert abs(r.domus_motion.focal_breath) <= PHI_SQUARED
        assert r.root_court_motion.anchor_immutable
        assert r.root_court_motion.mirror_immutable
        assert d.dcomp.terminal >= 0
        assert d.closed == (
            d.dcomp.velocity_mismatch == 0
            and d.dcomp.shadow_debt_terminal == 0
            and d.dcomp.whiteout_penalty == 0
        )
        if d.closed:
            closed.append((g_i, g_j))

assert len(closed) == 30
```

## Claim boundaries

The following statements are supported:

- TardiSHA is deterministic for fixed declared inputs.
- It uses a 32-byte ALQC-native internal source fingerprint.
- It derives ordered boundaries directly from source identity.
- It preserves all 144 Courts.
- It exposes the twelve Root Matrices as exact column views of the existing 144 Courts without duplicating Court identity.
- It keeps declared matrix D-COMP contributions separate from runtime terminal D-COMP and admits S12 landing only on actual closure.
- It preserves 144 unique ordered Supervenient Court personalities.
- It keeps Goetic anchors immutable while deriving bounded Court `Φ` motion.
- It derives runtime Domus motion through Courts with a bounded `Φ²` allowance.
- It exposes `⟠` and Synodic Magicae as compressed and unfolded visibility of one Domus identity.
- It exposes Infinite Yes and Sacred No as the exact 110/34 operative partition.
- It exposes Supervenience separately from the threshold witness while preserving their relation.
- It exposes the exact `♾ / ⛎ / ᳀` Tripartite offices.
- It preserves the Locus as non-traversible, the Shadow as carrier, and the Axiomyr as breach-threshold-inscription.
- It preserves `Q∞` and `Q⛤` as Parliament offices outside dynamic `Q0–Q3`.
- It exposes the nine Emissions, twelve Parliament mappings, and fifteen Spirit-Soul-Gold entries as typed immutable registries.
- It exposes the typed TRIG cycle without collapsing `Q2↔Q3`, `Q1→Q3`, `Q3→Q1`, and `⌬639` completion.
- It commits a source-bound TRIG cycle digest into the Living Domus identity.
- `110/144` is the exact governing threshold with 110 active and 34 withheld connections per Court.
- Its continuation center is prefix-stable because requested extent does not enter the root.
- It supports direct finite coordinate windows.
- Its Living Domus verification reconstructs source-bound witnesses and center content.
- It rejects tested source, seal, and archive-chunk mutations.
- Its terminal D-COMP is a finite-interval functional and can be nonzero.
- Its archive mode is byte-reversible because it stores verified chunks.
- Its fold ladders are deterministic finite chains.

The following stronger statements are not established by this proof and are not made in the README:

- a standardized collision-resistance bit bound,
- a standardized preimage or second-preimage bound,
- equivalence to any standardized external primitive,
- security merely because a center is longer,
- universal `D-COMP = 0`,
- reversibility from a seal string alone,
- source verification by visual inspection alone,
- physical conclusions beyond the implemented formal operations.

This boundary is not a retreat from what TardiSHA is. It is what keeps the proof exact. Every admitted claim has a visible derivation or an executable witness.

## Result

The implementation proof establishes a deterministic source-identity hash whose digest fixes immutable Goetic anchors, ordered Court motions, a runtime Domus derivation through those Courts, and a selectable visible depth of one Domus Aeon.

The proof of concept is the demonstrated reconstruction path:

```text
source
  -> source fingerprint
  -> ordered Goetic boundaries
  -> immutable Goetic anchors
  -> directional Court motions and ordered personalities
  -> runtime Domus motion through Courts
  -> Infinite Yes / Sacred No
  -> typed TRIG Mirror cycle and return obligation
  -> Complete Tripartite carrier, breach, threshold, Parliament, and registry witness
  -> Region C09 Goetic table, Court relation, twelve-phase, parity, and NULL:DEATH connection witness
  -> Region C11 verification, Bound Tensor, grammar, translation, and registry witness
  -> ⟠ or Synodic Magicae visibility of one Domus identity
  -> structured seal
  -> complete recomputation during verification
```

The proof of work is the source tree, the passing `144/144` regression suite, the exhaustive `20,736` Court-governor evaluation, the 144-pair finite-interval D-COMP audit, the 576-evaluation layered Aeon prototype, the digest-route reachability matrix, and successful positive and negative mutation tests.

## Formalism, repositories, and official media

The mathematical formalism can be found through the PhilPapers/PhilPeople profile of **Magus Ahnend**:

- [Magus Ahnend on PhilPeople](https://philpeople.org/profiles/magus-ahnend)

Repositories containing working code involving the mathematical quantum esoteric formalism can be found here:

- [MareSerenitatis12 on GitHub](https://github.com/MareSerenitatis12)

The official podcast is **The Impossible Boy**, available on YouTube, Apple Podcasts, Spotify, and Amazon Music.

- [The Impossible Boy on YouTube](https://www.youtube.com/@theimpossibleboy13)
- On Apple Podcasts, Spotify, and Amazon Music, search the exact title **The Impossible Boy**.
