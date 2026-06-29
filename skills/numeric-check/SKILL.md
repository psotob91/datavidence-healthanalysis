---
name: numeric-check
description: >-
  Verifies a specific numeric claim by re-deriving it from source data in code — not by
  recalling or reasoning. Triggers on: "verify this number", "recompute", "double-check the
  percentage / total / CI / p-value", "is this figure right", "check the math". Runs the
  executor subagent with R code (or WolframAlpha MCP / sympy / caracas for symbolic/algebraic
  work) and anchors every output to the script and its printed result (file:line). Reports
  match or mismatch; flags any value that was asserted from memory rather than computed.
  NOT for assembling a results table (use scaffold-reporting); NOT for a full analysis pass.
---

# /datavidence-healthanalysis:numeric-check

> Operationalizes `../_shared/health-principles.md` §1 (math by tool, never by model) and the
> child policy `analysis/numeric-computation.md`. The skill re-derives a claimed number via
> code; it does not reason a number into existence.

## When to use / when NOT to use

- **Use it when**: a specific number in prose, a table cell, a figure annotation, or a script
  comment needs independent verification — the user supplies (or the conversation contains) the
  claimed value and enough context to locate the source data or formula.
- **Do NOT use it when**: the goal is to author or scaffold a results table from scratch —
  that is scaffold-reporting. Do not use it for a full analysis run or a data-quality sweep;
  those are broader tasks. This skill verifies one claim (or a short, named list of claims)
  at a time.

## What it does (in order, no skipping)

1. **Identify the claim.** Restate the numeric claim exactly as given: the value, its units,
   the surface it appears on (prose / table / figure), and the script or object it allegedly
   comes from. If the claim cannot be located or is ambiguous, stop and ask.

2. **Locate the source.** Identify the source data path and the code that produced the value
   (script file + line, or inline chunk label). If no source can be found, mark the value
   `unverified` per `analysis/numeric-computation.md` and report — do not proceed to recompute.

3. **Choose the re-derivation tool.**
   - Counts, percentages, rates, CIs, p-values from data → **R** via the executor subagent.
   - Symbolic / algebraic re-derivation (formula expansion, exact fraction, closed-form CI) →
     **WolframAlpha MCP** first; fall back to `sympy` or `caracas` in R if WolframAlpha is
     unavailable or the expression is domain-specific.
   - Never compute mentally. Subagents reason about *what* to compute, then delegate to the
     tool and cite the result.

4. **Re-derive.** Write the minimal R snippet (or symbolic expression) that re-derives the
   value from source data. For stochastic values (bootstrap, MCMC, imputation): confirm a seed
   is set (`set.seed()` + `RNGkind()`; parallel → L'Ecuyer-CMRG). Run via the executor
   subagent. Capture the printed output verbatim.

5. **Compare.** Check recomputed value against the claimed value:
   - Deterministic → exact match (or relative tolerance ≤ 1e-8 when bit-for-bit equality
     cannot hold; document why and use `all.equal` with the explicit tolerance).
   - Stochastic → agreement within a few Monte-Carlo standard errors; report the MCSE.
   - Cross-surface → verify the same number in prose equals the number in the table or figure.

6. **Emit the recomputation note** (see Output below).

## Rules / invariants

- A number you cannot anchor to code output is `unverified` — mark it, do not assert it.
- Mental arithmetic is never a substitute for tool output, even for "obvious" rounding.
- If the original code is absent or the source data is unavailable, the verdict is
  `UNVERIFIABLE` (not a guess). Surface this clearly.
- Stochastic results without a recorded seed are treated as unverified until the seed is set.
- A loosened tolerance is a last resort that can mask bugs -- never a routine default;
  document the reason and the tolerance value explicitly.
- Apply `analysis/numeric-computation.md` for tolerance and seed rules; defer to it on
  conflicts with this file.

## Output

A short **recomputation note** (not a spec artifact; not a full report):

```
## Numeric check — <brief claim description>

**Claimed value:** <value + units + source surface>
**Source:** <file:line or chunk label>
**Re-derivation tool:** R / WolframAlpha / sympy / caracas
**Recomputed value:** <value from tool output> (paste printed output verbatim below)

```
<tool output verbatim>
```

**Verdict:** MATCH | MISMATCH | UNVERIFIABLE | UNVERIFIED
  - MATCH: values agree within stated tolerance (state tolerance if not exact).
  - MISMATCH: <difference, likely cause, corrective action>.
  - UNVERIFIABLE: source data or code absent — cannot recompute.
  - UNVERIFIED: value was asserted from memory, not anchored to code output.

**Cross-surface check:** <same number in prose vs table/figure — pass or discrepancy>
```

If multiple values are checked, emit one block per value then a one-line summary tally.

## Pairs with (child policy)

- `analysis/numeric-computation.md` — the authoritative rule (tolerance, seed, reconcile-
  across-surfaces). This skill operationalizes it.
- `../_shared/health-principles.md` §1 and §2 — math by tool; claim to evidence.
- `analysis/verification-effort.md` — scale auditor depth (light = 1 pass; deeper for
  published numbers or key conclusions).
