---
name: dag-causal
description: >-
  Builds and analyzes a causal DAG (Directed Acyclic Graph) to choose the minimal sufficient
  adjustment set for an exposure-outcome effect and derive testable implications; use when the
  user asks to draw a DAG, build a causal diagram, select confounders, choose an adjustment set,
  identify backdoor paths, check for colliders or mediators, run dagitty, use ggdag, diagnose
  M-bias, or assess causal structure before analysis. Operates only on the STRUCTURAL step —
  NOT the regression fit (use specify-regression) and NOT the estimand / SAP framing (use
  frame-study, which this skill complements as the target-trial structural step). Opt-in: only
  present when the causal module is enabled. Operationalizes the causal module doc and the
  target-trial / TARGET-statement workflow.
---

# /datavidence-healthanalysis:dag-causal

> Applies `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> `<<PENDING_CONFIRMATION>>` for uncertain edges, comprehension-before-code) and emits the DAG
> artifact per `../_shared/spec-artifact.md`. Pairs with the causal module doc
> (`docs/analysis/modules/causal.md`) and with `frame-study` (target-trial emulation /
> estimand). Packages: `dagitty`, `ggdag`; downstream: `WeightIt`, `MatchIt`, `marginaleffects`.

## When to use / when NOT to use
- **Use it when:** the user wants to draw a DAG, identify confounders, select an adjustment set,
  trace backdoor paths, flag colliders or mediators, encode causal structure in dagitty / ggdag,
  or check conditional independencies before specifying a model.
- **Do NOT use when:**
  - Specifying or fitting the regression model — use `specify-regression` (dag-causal feeds it
    the adjustment set; specify-regression consumes it).
  - Framing the estimand, target trial, or analysis plan — use `frame-study` (dag-causal is the
    structural/DAG step; frame-study is the estimand/SAP step; they pair sequentially).
  - Building a computable phenotype for the exposure or outcome — use `phenotype-gate` first.

## What it does (in order)

### 1. Elicit causal structure
Collect from the user (or infer from the protocol / data dictionary, flagging assumptions):
- Exposure(s), outcome(s), candidate confounders, suspected mediators, suspected colliders,
  time-varying variables, competing events.
- Mark every assumed or inferred edge `<<PENDING_CONFIRMATION>>` if not stated in the protocol.

### 2. Encode the DAG in dagitty syntax
Produce a `dagitty::dagitty()` call encoding all nodes and directed edges. Annotate the R code
block with comments for every `<<PENDING_CONFIRMATION>>` edge.

Example skeleton (fill with study variables):
```r
library(dagitty)
library(ggdag)

dag <- dagitty::dagitty('dag {
  # <<PENDING_CONFIRMATION>> — assumed from domain knowledge; confirm with PI
  age -> exposure
  age -> outcome
  exposure -> outcome
  # mediator: do NOT adjust
  exposure -> mediator -> outcome
  # collider: do NOT adjust
  collider <- exposure
  collider <- outcome
}')

# Set coordinates for ggdag layout
dagitty::coordinates(dag) <- list(
  x = c(age = 0, exposure = 1, mediator = 2, outcome = 3, collider = 2),
  y = c(age = 1, exposure = 0, mediator = 0, outcome = 0, collider = -1)
)
```

### 3. Derive the minimal sufficient adjustment set(s)
Delegate to dagitty — never compute by hand:
```r
# All minimal sufficient adjustment sets for exposure -> outcome
dagitty::adjustmentSets(dag, exposure = "exposure", outcome = "outcome",
                        type = "minimal")
```
Report every set returned. If multiple sets exist, note the practical trade-offs
(availability in data, sample size, model complexity).

### 4. Flag colliders, mediators, and M-bias
```r
# Paths that are open / blocked
dagitty::paths(dag, from = "exposure", to = "outcome")

# Implied conditional independencies (testable implications)
dagitty::impliedConditionalIndependencies(dag)
```
For each collider and mediator identified:
- **Collider** — name it and state: "Do NOT condition on [node]; conditioning opens the
  [exposure ← collider → outcome] path."
- **Mediator** — name it and state: "Do NOT adjust for [node] if estimating the total effect;
  adjust only if estimating the direct effect (requires mediation analysis)."
- **M-bias** — if a pre-exposure variable is a collider of two ancestors of exposure and
  outcome, warn explicitly and cite Pearl 2009 / Greenland 2003.

### 5. Testable implications
List each conditional independence from step 4 as a falsifiable claim the data can check
(e.g., "age ⊥ outcome | exposure, confounder_X"). Recommend a test (partial correlation,
conditional independence test via `dagitty::localTests()`).

### 6. Summarize adjustment recommendation
Produce a compact table:

| Adjustment set | Variables | Available in data? | Notes |
|---|---|---|---|
| Set 1 | … | <<PENDING_CONFIRMATION>> | … |

State which set is recommended and why. If the causal structure is uncertain, recommend
sensitivity analyses under alternative DAGs.

### 7. Emit the ggdag visualization code
```r
ggdag::ggdag(dag, layout = "nicely") +
  ggdag::theme_dag() +
  ggdag::geom_dag_point(colour = "steelblue") +
  ggdag::geom_dag_text(colour = "white", size = 3) +
  ggdag::geom_dag_edges_arc()
```
If the study has time-varying treatment or confounding, note that `ggdag` shows the static
structure and the analyst must extend to SWIG / LMTP for dynamic treatment regimes.

## Rules / invariants
- **Never compute adjustment sets mentally** — always delegate to `dagitty::adjustmentSets()`.
- **Never adjust for mediators or colliders** — warn explicitly when either is present in a
  candidate set. This is non-negotiable.
- **Mark uncertain edges** — every edge not anchored to the protocol or a cited reference gets
  `<<PENDING_CONFIRMATION>>` in both the dagitty code and the summary table.
- **No invented variables** — only include nodes confirmed in the protocol, data dictionary
  (`metadata/data_dictionary.csv`), or literature; flag others as `<<PENDING_CONFIRMATION>>`.
- **Math by tool** — apply `../_shared/health-principles.md`; do not reason through d-separation
  by hand.
- **Comprehension before code** — emit the DAG structure and verbal interpretation before
  producing runnable code; do not skip to code if structure is not yet agreed.
- This skill ends at the adjustment set. Downstream model specification goes to
  `specify-regression`; estimand and SAP go to `frame-study`.

## Pairs with (repo policy)
- `docs/analysis/modules/causal.md` — module policy (target trial, TARGET statement,
  exchangeability / positivity / consistency, ICH E9(R1) estimand).
- `frame-study` — upstream estimand / target-trial framing; dag-causal is the structural
  companion.
- `specify-regression` — downstream model specification; consumes the adjustment set this
  skill produces.
- `phenotype-gate` — define exposure and outcome operationally before drawing the DAG.
- `../_shared/health-principles.md` — cross-cutting principles (math-by-tool, claim-to-evidence).
- `../_shared/spec-artifact.md` — artifact layout.

## Output
Emit as a DAG spec artifact:
- **`dag-spec/dag.R`** — dagitty + ggdag code, self-contained, with `<<PENDING_CONFIRMATION>>`
  comments on assumed edges.
- **`dag-spec/adjustment-sets.md`** — table of minimal sufficient adjustment sets, collider /
  mediator / M-bias warnings, and the recommended set with rationale.
- **`dag-spec/testable-implications.md`** — list of conditional independencies and suggested
  local tests.
- **`dag-spec/README.md`** — one-paragraph summary: exposure, outcome, recommended adjustment
  set, key warnings, open questions.
- If the DAG changes materially after PI review, version the old dag as `dag-v0.R` before
  updating, and record the change in `dag-spec/README.md`.
