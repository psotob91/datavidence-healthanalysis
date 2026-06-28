---
name: validate-data-contract
description: >-
  Gates raw and analysis-ready data at the contract boundary: checks column
  existence and types, allowed values and numeric ranges, required-non-missing
  fields, primary-key uniqueness, expected join cardinality (1:1 / 1:m), and
  temporal plausibility (no events before birth / after death; start <= end).
  Writes a pointblank contract file (contracts/raw_<dataset>.yml or
  contracts/analysis_<dataset>.yml) and a run report to outputs/validation/.
  Records each rule as PASS / WARN / FAIL; BLOCKS the pipeline on any FAIL;
  raw data stays immutable. Use when the user asks to validate the data, run a
  data contract, check schema, run a data quality gate, check column types or
  ranges, verify the join, or confirm the data is clean before modeling.
  NOT for missingness-mechanism reasoning (use assess-missingness); NOT for
  connecting to or onboarding a new data source (use onboard-data).
  Operationalizes analysis/data-contracts.md and analysis/data-integrity.md.
---

# /datavidence-healthanalysis:validate-data-contract

> Operationalizes `.claude/policies/analysis/data-contracts.md` and
> `.claude/policies/analysis/data-integrity.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION) and emit the contract file + run report per
> `../_shared/spec-artifact.md` (simple focused artifact).

## Boundary vs sibling skills

- **assess-missingness:** this skill asks "do these columns exist and have the
  right type / value?" (schema + referential integrity). assess-missingness asks
  "are values missing and why?" (mechanism + imputation strategy). Run this skill
  first; a clean contract is a precondition for a meaningful missingness profile.
- **onboard-data:** onboard-data connects to a new source and registers it.
  This skill assumes onboarding is complete and raw data is in `data/raw/`.

## When to use / when NOT to use

- **Use it when:** data is about to enter the pipeline (raw gate) or leave
  cleaning and enter analysis (analysis-ready gate); any time a join cardinality,
  a column type, a date range, or a primary-key uniqueness check is needed; or
  when a CI step must block on a quality failure.
- **Do NOT use it when:** the question is about missingness mechanism, imputation
  strategy, or MICE configuration -- that is assess-missingness. Do NOT use it to
  connect a new source -- that is onboard-data.

## What it does: inspect -> draft -> run -> report (in order, no skipping)

### 1. Inspect existing contracts and data dictionary

Read `contracts/*.yml` (existing rules) and `metadata/data_dictionary.csv`
(variable / label / type / derivation / source). Do not invent rules not grounded
in one of these anchors or the user-stated protocol. Unresolved thresholds or
allowed-value sets receive `PENDING_LOCAL_DECISION` -- never a silent default.

### 2. Draft the pointblank contract file

Write `contracts/raw_<dataset>.yml` or `contracts/analysis_<dataset>.yml`.
The contract encodes -- for each relevant column:

- **Column existence** -- the column must be present in the dataset.
- **Type conformance** -- declared type matches (integer, double, character, date, ...).
- **Allowed values / levels** -- for categorical columns, the set of valid codes.
- **Numeric range** -- lower and upper plausible bounds (source: data dictionary or
  protocol; mark PENDING_LOCAL_DECISION where unset).
- **Required-non-missing** -- columns that must not contain NA for the row to be
  analytically valid.
- **Primary-key uniqueness** -- unique identifier column(s) must not duplicate.
- **Join cardinality** -- expected relationship (1:1 or 1:m) with a named table;
  assert row counts before and after the join.
- **Temporal plausibility** -- no event date before birth_date; no event date after
  death_date; start_date <= end_date for any interval; dates within the declared
  study window.
- **Cross-field logic** -- constraints that span two or more columns within the same
  row: e.g. a value that is only valid for one sex (pregnancy_flag == TRUE requires
  sex == 'F'), dose-route consistency (IV route requires a non-oral dose form),
  age-at-event within biologically plausible bounds. Assign `severity` per protocol
  (usually `warn` unless the protocol mandates `error`).
- **Referential integrity** -- a foreign-key value in one table must exist as a
  primary key in the referenced table (e.g. every `encounter.patient_id` must
  appear in `patients.patient_id`). This is distinct from join cardinality: cardinality
  asserts the row-count ratio; referential integrity asserts that dangling keys are
  absent. Default severity: `error` (an orphaned foreign key is a data-linkage defect).

Each rule carries a `severity`: `error` (pipeline FAIL) or `warn` (flag, no block).
Default critical rules (key, type, existence, temporal) to `error`; flag
plausibility ranges as `warn` unless the protocol specifies otherwise.

### 3. Run the contract

Delegate all execution to R code (math-by-tool). The run produces:

- A pointblank agent interrogation (or equivalent validation pass).
- Row-level counts: N total, N passing each rule, N failing each rule.
- For join rules: row counts before and after with explicit reconciliation.

Never compute counts, pass/fail tallies, or percentages in model output.

### 4. Write the run report

Write to `outputs/validation/<dataset>-contract-report.md` (or `.html` if the
child stack supports a quarto render). Each rule appears as one row:

| Rule | Column(s) | Severity | Result | N failing | Note |
|---|---|---|---|---|---|
| column_exists | patient_id | error | PASS | 0 | |
| no_missing | patient_id | error | PASS | 0 | |
| is_unique | patient_id | error | PASS | 0 | |
| col_type | dob | error | FAIL | 3 | parsed as character |
| value_range | age_years | warn | WARN | 12 | > 120; review |

Append a PENDING_LOCAL_DECISION register listing every rule whose threshold or
allowed-value set has not been fixed by the local protocol or data dictionary.

### 5. Block or pass

- Any rule at `severity: error` that returns FAIL **blocks the pipeline**. The
  report must be reviewed and the failure resolved or explicitly accepted in
  `docs/adr/` before the pipeline proceeds.
- WARN rules are surfaced and logged but do not block.
- A dataset that clears all `error` rules is declared **PASS** and may proceed to
  the next pipeline step (IDA, cleaning, or modeling as appropriate).

## Rules / invariants

- **Raw is immutable.** This skill reads `data/raw/`; it never modifies it.
  Every fix is a pipeline transform in `data/derived/` or `src/`.
- **Block on FAIL.** A failed error-severity rule stops the analysis; exceptions
  require an ADR in `docs/adr/`.
- **Declare join cardinality explicitly.** State 1:1 or 1:m and assert before and
  after every join. Silent row multiplication is a top source of invisible error.
- **PENDING_LOCAL_DECISION, never a silent default.** Any threshold, allowed-value
  set, or cardinality rule not grounded in the data dictionary or protocol is named
  PENDING_LOCAL_DECISION.
- **Math by tool.** All row counts, failure tallies, and percentages come from R
  code; no arithmetic in model output.

## Output

Emit two focused artifacts per `../_shared/spec-artifact.md` (simple artifact form):

1. **Contract file:** `contracts/raw_<dataset>.yml` or
   `contracts/analysis_<dataset>.yml` -- the machine-readable rule set, checkable
   by pointblank or an equivalent validation library.
2. **Run report:** `outputs/validation/<dataset>-contract-report.md` -- one-row-per-
   rule table (columns: Rule / Column(s) / Severity / Result / N failing / Note),
   a pass/fail summary, and the PENDING_LOCAL_DECISION register.

If the report grows beyond ~300 lines (many columns, many rules), split into
`outputs/validation/<dataset>/01-existence-types.md`, `02-values-ranges.md`,
`03-keys-joins.md`, `04-temporal.md` with a README router.

Runnable contract code (the pointblank interrogation call) may be shown as a
skeleton before results are available; final pass/fail numbers come from the
executed R code, not from model reasoning.

## Pairs with (repo policy)

- `.claude/policies/analysis/data-contracts.md` (validate at the gates; block on failure).
- `.claude/policies/analysis/data-integrity.md` (raw immutable; declare join cardinality; type control).
- **Prior-if:** `onboard-data` (data must be registered before it can be contracted).
- **Next-if:** data passes -> `analysis/initial-data-analysis.md` (IDA before modeling).
- **Parallel:** `assess-missingness` runs after this skill; a clean contract is a
  precondition for a meaningful missingness profile.
