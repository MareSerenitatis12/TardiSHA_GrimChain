# How TardiSHA Works

This chapter explains the operating sequence without requiring the full ALQC mathematics.

## 1. The physical source is read

For an ordinary file, every physical byte is read. Filesystem timestamps, ownership, and path names do not enter the raw-file identity.

The bytes are absorbed by the twelve-lane ALQC sponge. The completed source emission preserves:

- all twelve finalized lanes;
- the public 256-bit source digest;
- the next equal-width cadence from the same finalized state;
- the source size and source domain.

The digest is part of the witness, but the digest alone is not allowed to choose the Goetics. The whole twelve-lane emission is required.

## 2. Parliament resolves the Goetics

The source emission becomes two conserved twelve-seat bodies.

The structural body records the relative amplitude carried by each Goetic lane. The operational body records the AHN-relative phase gaps across the Parliament order.

The first internal Fraktur cadence is read through the structural body with the exact Golden bearing `Phi^-1`. The second cadence is read through the operational body with `Phi^-2`.

Both bearings preserve the Parliament order. No `% 12` selector, first-byte selector, last-byte selector, fixed zodiac longitude, or reversed Parliament procession is used.

The result is one ordered pair:

```text
(governing Goetic, hyperbolic parent)
```

## 3. The Courts form after the pair exists

The forward Court is `C(i,j)`. The reciprocal Court is `C(j,i)`.

Court selection never happens first and then invents its own parents. The source path is:

```text
source emission -> Parliament -> Goetics -> Courts
```

The route closure derives source D-COMP `0` and source Truth `1` from exact conservation residuals.

## 4. The Living Domus seal appears

The visible seal contains:

- the governing Goetic;
- the forward Court glyph;
- the opening Q-state and bias witness;
- the depth-zero Supervenience center `⟠`, or a requested Synodic Magicae center;
- the return bias witness;
- the reciprocal Court glyph;
- the hyperbolic parent.

The center length changes the visible extent, not the rooted source identity.

## 5. The Aeternum Mirror return

The expanded file body occupies the `Fraktur Z1` source posture. Its returned depth-zero Grimchain occupies the `Fraktur Z0` compressed posture.

When a file ends with a possible depth-zero Grimchain, TardiSHA does not discard it. The program:

1. reads and parses the terminal body;
2. computes the source emission of the preceding bytes;
3. regenerates the expected Grimchain from those preceding bytes;
4. measures the exact UTF-8 difference between the terminal body and the regenerated body;
5. folds the return only when that residual is zero.

The two closure offices remain distinct:

```text
source D-COMP    source-route conservation residual
source Truth     whether the effective source route closes
return D-COMP    measured difference between returned and regenerated Grimchains
return Truth     whether the terminal return residual is zero
```

For an exact self-return:

```text
source D-COMP = 0
source Truth  = 1
return D-COMP = 0
return Truth  = 1
```

For a false depth-zero return:

```text
source D-COMP = 0 for the enlarged physical source
source Truth  = 1 for that enlarged source
return D-COMP > 0
return Truth  = 0
```

The false return remains source matter. Nothing is predeclared as correct.

## 6. Append-only return lineage

A file may carry more than one consecutive exact returned self. Each member of the terminal stack must recompute exactly from the effective body beneath it.

There is no configured return-count ceiling. Verification terminates because every admitted return occupies positive physical extent and each inward step strictly shortens the finite inspected prefix.

## 7. Physical bytes and effective identity

The physical byte ledger is never falsified. A folded exact return remains present in the physical file and is reported by the Mirror witness. The fold changes the effective identity posture, not the fact that the bytes exist.

Reversible archives preserve the physical-byte office and restore the exact original bytes, including any appended returned bodies.
