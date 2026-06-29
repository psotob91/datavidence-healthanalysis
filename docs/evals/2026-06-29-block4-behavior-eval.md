# Block 4 behavior-eval + trigger-description optimization

**Date:** 2026-06-29
**Branch:** feat/healthanalysis-block0-artifact-format
**Scope:** the 5 Block-4 skills whose behavior-eval was deferred at v0.1.0 build time:
`dag-causal`, `specify-sensitivity-plan`, `review-outliers`, `big-data-triage`, `draft-diagram`.

## 1. Behavior-eval (with-skill vs baseline)

**Method.** Each skill was given one representative task in two arms:

- **baseline** -- a Sonnet agent receives only the task (no skill).
- **with-skill** -- the same Sonnet agent receives the same task plus the SKILL.md body injected.

The task text is identical across arms; the only difference is the skill. Each produced
artifact is scored against a binary rubric transcribed from the skill's own mandated
procedure and "Rules / invariants". Producers (Sonnet) are distinct from the scorer
(generator != auditor), mirroring the r-package-skills-style validation used for Blocks 1-3.

| Skill | Baseline | With-skill | Delta |
|---|---|---|---|
| dag-causal | 19% (1.5/8) | 100% (8/8) | +0.81 |
| specify-sensitivity-plan | 40% (4/10) | 100% (10/10) | +0.60 |
| review-outliers | 67% (6/9) | 100% (9/9) | +0.33 |
| big-data-triage | 55% (5.5/10) | 100% (10/10) | +0.45 |
| draft-diagram | 0% (0/7) | 100% (7/7) | +1.00 |
| **mean** | **36%** | **100%** | **+0.64** |

Consistent with the Block-4 representative figure reported at build time (100% / 38%, +0.62).
The two higher baselines (review-outliers 67%, big-data-triage 55%) are expected: a strong
generic answer already covers much of those domains, so the skill's marginal lift is smaller.
draft-diagram's 0% baseline reflects that the skill is almost entirely convention-discipline
(sketch-gate, ISO 5807, Okabe-Ito) that a generic answer skips.

**What baseline misses (the skill's value-add):**

- **dag-causal** -- no dagitty encoding, hand-picks confounders instead of `adjustmentSets()`,
  no PENDING marking of assumed edges, no testable implications, and crosses into the
  regression FIT (the skill keeps to the structural step). Baseline DID correctly flag
  adherence as a mediator.
- **specify-sensitivity-plan** -- E-value not anchored at both point and CI-limit; no named
  unmeasured confounders (abstract "residual confounding"); no probabilistic QBA; no reuse
  gate; no PENDING register. Baseline was strong on substance (negative/positive controls,
  active comparator).
- **review-outliers** -- high baseline; misses MAD-specific detection + the explicit
  anti-(mean +/- SD) rule, pre-specification-before-seeing discipline, PENDING-hold, and the
  decisions.yml record. Baseline correctly refused blanket deletion and flagged SBP=0 vs >250.
- **big-data-triage** -- does not probe RAM/size first, no profile-before-optimize, no PENDING
  register, no explicit "no row loops". Baseline correctly led with DuckDB + Parquet.
- **draft-diagram** -- baseline emits Mermaid immediately (no sketch-gate), all-rectangles
  (no ISO 5807 shapes), non-colorblind palette (no Okabe-Ito), no legend, no PENDING. The
  with-skill arm correctly STOPPED at the sketch approval gate (silence is not consent).

## 2. Trigger-description optimization

Two decorrelated Sonnet routers read all 21 skill `description` fields and routed 15 boundary
prompts (positive + sibling-boundary). Three consensus collisions were found and fixed
(description-only -- no behavior change):

| Collision | Wrong attractor | Fix |
|---|---|---|
| "target-trial framing": frame-study vs dag-causal | dag-causal | reframed the trailing "target-trial workflow" phrase as the *structural* step; added target-trial/estimand triggers to frame-study |
| "Cook's distance / influential points": validate-assumptions vs review-outliers | validate-assumptions (lacked the trigger) | added post-fit influence triggers (Cook's distance, leverage, DFBETA) to validate-assumptions |
| "phenotype temporal timeline": phenotype-gate vs draft-diagram | draft-diagram | narrowed draft-diagram's timeline trigger to project/enrollment; added a decision/temporal ASCII-timeline trigger to phenotype-gate |

Post-fix, both routers agree all 15 prompts route as a CLEAN_WIN. Router A additionally flagged
two marginal close-races (assess-missingness vs run-ida; scaffold-reporting vs draft-diagram for
CONSORT) that Router B judged already-clean because the exclusions exist; left as watch-items
(outside Block-4 scope).

## 3. Pre-existing finding (NOT introduced here)

Three descriptions exceed the project's documented <=1024-char limit and should be trimmed
separately: **run-ida (~1214)**, **design-indicator (~1031)**, **prediction-validation (~1028)**.
None were edited in this change; design-indicator was already 1031 at HEAD. The 5 edited skills
remain well under the limit (791-919).
