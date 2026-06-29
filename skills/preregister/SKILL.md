---
name: preregister
description: >-
  Consolidates the upstream design artifacts (estimand/SAP from frame-study, the sensitivity
  plan, the phenotype case/exposure definitions, the variable catalog, the indicator/population
  frame) into ONE canonical, lockable pre-registration artifact with PENDING markers, then LOCKS
  it (status: locked + validation/logs/sap_lock.json) on explicit human sign-off so the sap-lock
  hook permits analysis. Builds the population_cascade (target -> accessible -> sampled -> study)
  and records every post-lock change in a deviations log -- never a silent edit. Use when the user
  asks to pre-register the study, lock the SAP or analysis plan, freeze the protocol, create the
  pre-registration, set status: locked, or record a deviation from the locked plan. NOT for
  drafting the estimand or SAP itself (use frame-study); NOT for adding sensitivity analyses (use
  specify-sensitivity-plan) -- this skill consolidates and locks what those produce.
---

# /datavidence-healthanalysis:preregister

> Operationalizes the tsukuba "mandatory pre-registration" paradigm (one lockable artifact;
> the file-existence lock is the most reliable gate). Apply `../_shared/health-principles.md`
> (claim-to-evidence, PENDING_LOCAL_DECISION, comprehension-before-code, math-by-tool) and emit
> per `../_shared/spec-artifact.md`. The lock is enforced at write-time by the `sap-lock` hook;
> the variable catalog by `variable-catalog-gate`; attrition logging by `attrition-log`.

## When to use / when NOT to use

- **Use it when:** the design artifacts exist and the analyst wants to FREEZE them into one
  canonical pre-registration and lock it before any cleaning/modeling code runs; or to record a
  deviation after the lock.
- **Do NOT use it when:**
  - The estimand / SAP has not been drafted yet -- use `frame-study` first.
  - The user wants to add or change sensitivity analyses -- use `specify-sensitivity-plan`.
  - The user wants to (re)define a phenotype or indicator -- use `phenotype-gate` /
    `design-indicator`. This skill CONSOLIDATES those artifacts; it does not author them.

## What it does (in order)

### 1. Gather the upstream artifacts
Collect (or locate) and reference, never re-derive:
- estimand + SAP skeleton (`frame-study` output),
- pre-specified sensitivity plan (`specify-sensitivity-plan`),
- case / exposure definitions (`phenotype-gate`),
- denominator / population frame + windows (`design-indicator`),
- variable spec catalog (`metadata/variable_spec_catalog.yaml`, or the hyphen alias
  `metadata/variable-catalog.yaml`; the `variable-catalog-gate` hook accepts either).
Any artifact not yet produced is recorded as `PENDING_LOCAL_DECISION: <artifact>` -- not invented.

### 2. Assemble the canonical pre-registration
Write `analysis/prereg/pre-registration.yaml` with this schema (fill from step 1; every unfilled
field is an explicit `PENDING`):
```yaml
status: draft            # draft | locked  (locked is the gate)
locked_at:               # ISO datetime, set at lock
locked_by:               # initials, set at lock
content_sha256:          # hash of this file at lock
population:
  target: PENDING        # target population (estimand denominator)
  estimand: PENDING      # PICO/PECOT, ICH E9(R1) attributes
index_date: PENDING
exposures: [PENDING]
outcomes: [PENDING]
objectives: [PENDING]
model:
  primary: PENDING       # primary analysis spec (ties to specify-regression)
adjustments:
  prespecified: [PENDING]
sensitivity_analyses: PENDING   # reference the locked sensitivity-plan artifact
references:              # provenance: path to each upstream artifact
  sap: PENDING
  sensitivity_plan: PENDING
  phenotype: PENDING
  indicator: PENDING
  variable_catalog: PENDING
deviations: []           # appended AFTER lock only (see step 6)
```

### 3. Build the population cascade
Write `analysis/prereg/population_cascade.yaml` -- counts per level, each from code output
(math-by-tool), `PENDING` until the count exists:
```yaml
levels:
  - level: target       # the population the estimand is about
    n: PENDING
  - level: accessible   # in the data source / catchment
    n: PENDING
  - level: sampled      # met eligibility / sampling
    n: PENDING
  - level: study        # final analytic set
    n: PENDING
```
Each downstream filter must call `log_attrition(step, n_in, n_out, excludes_target_population, reason)`
(the `attrition-log` hook flags filters that omit it). `excludes_target_population: true` marks a
filter that narrows AWAY from the target population (the target/accessible split), giving the
two-branch STROBE flow that accumulates from the start.

### 4. Resolve PENDING before lock
The artifact cannot be locked while any field is `PENDING`. List every open `PENDING_LOCAL_DECISION`
and ask the analyst to resolve or explicitly defer it. A deferred field stays `PENDING` and the
artifact stays `draft` (unlocked) -- never lock over a PENDING.

### 5. Human sign-off + LOCK
Present the assembled pre-registration for explicit confirmation. Silence is not consent. On
sign-off:
- set `status: locked`, `locked_at`, `locked_by`;
- compute the SHA-256 of the locked file content and record it in `content_sha256`;
- write `validation/logs/sap_lock.json` = the object {locked_at, locked_by, prereg_path, content_sha256}.
The EXISTENCE of `validation/logs/sap_lock.json` is the gate the `sap-lock` hook checks -- once it
exists, analysis/model writes proceed.

### 6. Post-lock changes = deviations, never silent edits
After lock, any change is appended to `deviations:` (date, field, from, to, reason, approved_by)
and the file re-locked (new hash). Editing a locked pre-registration without logging the deviation
defeats the paradigm. The locked artifact becomes the methods-appendix record.

## Rules / invariants
- **The lock is the gate.** No cleaning/analysis/model code before `validation/logs/sap_lock.json`
  exists (enforced by the `sap-lock` hook; this skill produces the lock).
- **No lock over PENDING.** Every field is a real value or an explicit deferred `PENDING`; locking
  requires zero unresolved PENDING.
- **Consolidate, do not author.** Reference the upstream artifacts; do not re-derive the estimand,
  phenotype, or sensitivity plan here.
- **Deviations are logged, never silent.** Post-lock edits append to `deviations:` and re-hash.
- **Math by tool.** Cascade counts and attrition come from code output, not prose.
- **Sign-off is explicit.** Silence is not consent; mark `locked` only on confirmation.

## Pairs with (repo policy)
- `frame-study` -- upstream estimand / SAP (prerequisite).
- `specify-sensitivity-plan` -- the locked sensitivity plan referenced here.
- `phenotype-gate` / `design-indicator` / `map-clinical-codes` -- definitions consolidated here.
- Hooks `sap-lock` (gates analysis on the lock), `attrition-log` (each filter logs counts),
  `variable-catalog-gate` (blocks `status: unknown` variables).
- `../_shared/health-principles.md`, `../_shared/spec-artifact.md`.

## Output
- `analysis/prereg/pre-registration.yaml` -- the canonical, lockable artifact.
- `analysis/prereg/population_cascade.yaml` -- counts per level.
- `validation/logs/sap_lock.json` -- the lock sidecar (existence = locked).
- Inline summary: lock status, unresolved PENDING count, and (post-lock) any deviations.
