---
name: scaffold-reporting
description: >-
  Produces an EQUATOR-aligned reporting artifact by type for health-data studies: a RECORD
  data-source table for secondary/routinely-collected data, a Table 1 or comparison table built
  with gtsummary (no p-values, SMD for balance, missingness shown, labels-first), or a
  CONSORT/STROBE/PRISMA participant-flow diagram built with the flowchart R package.
  Use when the user asks for a Table 1, baseline characteristics table, participant flow,
  CONSORT diagram, STROBE flow, PRISMA diagram, RECORD data-source table, flow diagram,
  or descriptive table.
  Operationalizes health/secondary-data.md, health/clinical-tables.md, health/study-flow.md,
  and analysis/diagrams.md (sketch-first gate).
  NOT for the analysis itself (numeric results, estimates, regression); NOT for numeric
  verification (use numeric-check); NOT for phenotype or indicator definitions (use
  phenotype-gate or design-indicator).
---

# /datavidence-healthanalysis:scaffold-reporting

> Operationalizes `.claude/policies/health/secondary-data.md`,
> `health/clinical-tables.md`, `health/study-flow.md`, and `analysis/diagrams.md`.
> Apply `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, comprehension-before-code) and emit the artifact per
> `../_shared/spec-artifact.md`. The sketch-first approval gate from `analysis/diagrams.md`
> runs for EVERY output type before any code is written.

## When to use / when NOT to use

- Use it when: the user asks for a Table 1, baseline characteristics table, participant
  flow, CONSORT/STROBE/PRISMA diagram, RECORD data-source table, flow diagram, or
  descriptive table — i.e., a reporting scaffold aligned with an EQUATOR guideline.
- Do NOT use it when: the user needs numeric results, effect estimates, or regression
  output — use the appropriate analysis skill. Do NOT use it for numeric verification
  — use numeric-check. Do NOT use it for phenotype or indicator definitions — use
  phenotype-gate or design-indicator. Reporting scaffolds consume those outputs;
  stay in lane.

## Step 0 — Sketch-first approval gate (ALL types, no skipping)

**Prerequisite:** this skill assumes the dataset(s) have passed `validate-data-contract`
(all `error`-severity rules PASS). If no contract run report exists under
`outputs/validation/`, emit `PENDING_LOCAL_DECISION: data-contract-not-validated` and
pause — do not produce a reporting scaffold over uncontracted data.

Before any R code or numeric lookup, produce a **plain-text mock** of the artifact:
boxes and labels for flow diagrams; row/column headers for tables; source rows for
data-source tables. **No numbers.** Present the mock and **get explicit human
approval**. Silence is not consent. Iterate until the structure is agreed. Only
after sign-off proceed to the type-specific steps below.

If a reporting choice is not recorded in the SAP or protocol, return
`PENDING_LOCAL_DECISION` and name the choice — do not invent a default.

---

## Type A — RECORD data-source table (secondary / routinely-collected data)

**Policy:** `.claude/policies/health/secondary-data.md`

Produce a `metadata/data-source-table.md` (+ `.csv`) documenting every database or
source used in the study. Each row covers one source:

| Column | Content |
|---|---|
| Source name | Database / registry / extract name |
| Version / release | Exact version or extract date |
| Coverage | Population, geography, date range |
| Linkage | How sources are joined; linkage quality / QC |
| Code lists used | Phenotype algorithms or code sets defining key variables |
| Validation status | Whether the extract was validated against a data contract |
| Missingness mechanism | Declared mechanism per source: missing encounter ≠ MAR — a record absent from the DB may mean the event never occurred, was not coded, or was not linked. State the assumed mechanism (MCAR / MAR / MNAR) and the implication for analysis. |

Rules:
- Every entry traces to `metadata/data_dictionary.csv` or `contracts/*.yml`; a source
  that cannot be anchored gets `status: unknown` and `<<PENDING_CONFIRMATION_Qn>>`.
- Missingness mechanism for each source must be declared (missing encounter ≠ MAR).
- If target-trial emulation applies, note that TARGET reporting is also required
  (see `.claude/policies/health/reporting-standards.md`).
- After sign-off: emit `metadata/data-source-table.md` (human-readable) and
  `metadata/data-source-table.csv` (machine-readable).

---

## Type B — Table 1 / comparison table (gtsummary)

**Policy:** `.claude/policies/health/clinical-tables.md`

After the sketch-first gate produces an agreed row/column layout:

1. **Labels first**: map every variable to its label from `metadata/data_dictionary.csv`
   before rendering; never expose raw column names.
2. **No p-values** in descriptive or group-comparison tables unless explicitly requested
   and recorded in the SAP.
3. **Missingness**: show `n missing` or `% missing` per variable; report denominators.
4. **Balance (comparative tables)**: use standardized mean differences (SMD), not
   p-values.
5. **Confidence intervals**: all estimates carry CIs; rounding consistent across rows.
6. **Dual output**: emit one machine-readable `.csv` and one human-readable `.html` or
   `.docx` per table (per `outputs/OUTPUT_LAYOUT.md`).

R scaffolding pattern (language-agnostic pseudocode):
```
READ data_dictionary -> build label_list
CALL tbl_summary(data, by = group, label = label_list,
                 missing = "ifany", statistic = ...)
IF comparative: ADD_SMD via add_difference(test = list(all_continuous() ~ "smd"))
NEVER add_p() unless SAP explicitly permits
EXPORT as_gt() -> gtsave(.html) + as_tibble() -> write_csv()
```

Mark any variable whose label or missingness mechanism cannot be confirmed from
`metadata/data_dictionary.csv` as `PENDING_LOCAL_DECISION`.

---

## Type C — Participant-flow diagram (CONSORT / STROBE / PRISMA)

**Policy:** `.claude/policies/health/study-flow.md`; gate from `analysis/diagrams.md`

After the sketch-first gate (plain-text box mock, no numbers, approved):

- **RCT / CONSORT**: build with the `flowchart` R package from a dataframe of
  per-step counts; follow CONSORT 2025 box structure.
- **Cohort / observational (STROBE)**: participant flow built from the dataframe with
  `flowchart`; each exclusion box traceable to its data step.
- **Secondary data (RECORD-style selection flow)**: records in DB → after each
  inclusion/exclusion criterion → analytic cohort; each box traceable to its
  source/step (see Type A).
- **Systematic review (PRISMA 2020)**: use the `PRISMA2020` R package.
  *(Only when the `synthesis` module is active.)*

Invariants:
- Every box has a data source; counts must reconcile at each step
  (in = out + excluded).
- The plain-text mock (Step 0) is the design; the `flowchart` R code produces the
  final figure from real counts only after approval.
- Emit the figure to `outputs/figures/` and the underlying counts to
  `outputs/tables/flow-counts.csv`.

---

## Output

Emit a reporting spec per `../_shared/spec-artifact.md`:
- **Small artifact** (single table or short flow): one file
  `analysis/reporting/<name>-spec.md` with the mock, approved layout, and
  R pseudocode.
- **Large artifact** (multi-type or full manuscript scaffold): split into an indexed
  `analysis/reporting/<name>/` directory with a `README.md` router and one section
  file per type (A, B, C).
- After sign-off and real counts available: emit the runnable R code to
  `code/reporting/<name>.R` (or `.qmd`) + the dual outputs (csv + html/docx/png).

---

## Pairs with (repo policy)

- `.claude/policies/health/secondary-data.md` (RECORD essentials)
- `.claude/policies/health/clinical-tables.md` (gtsummary rules)
- `.claude/policies/health/study-flow.md` (flow by design)
- `.claude/policies/analysis/diagrams.md` (sketch-first gate)
- **Prior-if:** `validate-data-contract` (data must have passed its contract before
  a reporting scaffold is produced — see Step 0).
- Prerequisite inputs: `phenotype-gate` (case definitions), `design-indicator`
  (denominators / person-time), `map-clinical-codes` (code sets).
- Next-if: manuscript assembly → `.claude/policies/health/reporting-standards.md`
  (EQUATOR checklist).
