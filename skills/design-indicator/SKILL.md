---
name: design-indicator
description: >-
  Designs or reviews an incidence or prevalence indicator built from routinely-collected data
  (EHR, claims, registry): defines the denominator BEFORE the numerator, declares the population
  frame, computes person-time by interval overlap, types every window (lookback, washout, clean,
  confirmation, outcome, risk, grace-gap), fixes the index date, builds episodes, declares a
  recurrence model, states the prevalence type or incidence form (cumulative incidence vs rate),
  and reports per RECORD / RECORD-PE. Use when the user asks about incidence, prevalence,
  denominator, person-time, episode, the washout/lookback window of an incidence or prevalence
  measure, rate, or surveillance indicator. NOT for assigning the case label itself (that is
  phenotype-gate); NOT for assembling the code set (that is map-clinical-codes).
---

# /datavidence-healthanalysis:design-indicator

> Operationalizes `.claude/policies/health/routinely-collected-data.md`. Apply
> `../_shared/health-principles.md` (math-by-tool, claim-to-evidence,
> PENDING_LOCAL_DECISION, no invention) and emit the artifact per
> `../_shared/spec-artifact.md` (chaptered split-indexed dir, variable catalog,
> implementable pseudocode, academic + executive qmd render). This gate runs
> BEFORE any pseudocode or code; runnable code is withheld until human sign-off.

## When to use / when NOT to use

- **Use** when the user needs to define or review a denominator, compute person-time,
  classify a window type, build episodes, choose a recurrence model, declare a prevalence
  type, or specify an incidence form from routinely-collected data (EHR / claims /
  registry / surveillance).
- **Do NOT use** when assigning a case label to a record (use `phenotype-gate`) or when
  assembling / validating the underlying code set (use `map-clinical-codes`). The three
  skills form a chain: code set -> case label -> indicator. Stay in lane.

## What it does: the indicator design gate (in order, no skipping)

Produce the indicator-design sections (see Output) then STOP for sign-off:

1. **Denominator declared first.** State the population frame (resident / registered /
   enrolled / observed person-time / contact / point / period), the source system, the
   time scale (e.g. calendar year, cohort entry), entry and exit rules, geography, and
   whether persons with no records remain in the frame. Run the **Denominator integrity**
   gate in `docs/health/checklists.md`; any "no" or "unknown" is a stop.

2. **Observable time boundary.** Confirm the source system observable window (enrollment
   spells, registration periods, active coverage). Flag any lookback or washout that
   extends outside it -- flag it as **insufficient lookback** (Suissa) and do not silently classify a case as incident. Phrase findings as
   observed-record statements; never read "no record" as "no disease" outside observable
   time.

3. **Windows typed and drawn.** For every window in scope, assign one type from the
   controlled vocabulary: lookback (baseline) . washout (exclude prevalent) . clean
   (require no prior event) . confirmation (future classification) . outcome (follow-up) .
   risk (time-at-risk) . grace-gap (merge records into episodes) . eligibility (cohort
   membership). State inclusivity `[ ]` vs `( )` for each boundary. Draw one ASCII
   timeline per window using `docs/health/ascii-timelines.md` forms 1-4 BEFORE any
   pseudocode. A rule you cannot draw is a rule you do not understand.

4. **Index date fixed; no immortal time.** Record the time-zero definition. If a
   confirmation window exists, confirm it classifies without shifting time-zero (form 2
   of the ascii-timelines notation). If the estimand explicitly targets confirmed
   survivors, state that and document the immortal-time consequence.

5. **Numerator defined.** Tie the numerator to a code list / phenotype (output of
   `map-clinical-codes` / `phenotype-gate`) -- not biological onset unless locally
   validated. Run the **Numerator / window / episode alignment** gate in
   `docs/health/checklists.md`; any "no" or "unknown" is a stop.

6. **Person-time by interval overlap.** Specify the algorithm for accumulating person-time:
   sort enrollment/coverage spells, intersect with at-risk periods, sum overlapping
   intervals. Never use naive max-minus-min across full history.

7. **Episode construction.** Sort + dedup events at the declared grain. Specify allowed
   gaps, minimum duration / minimum records, modality hierarchy (when multiple sources are
   present), and explicit rules for records arriving after death, transfer, or exit.

8. **Recurrence model declared.** Choose one: **chronic-irreversible** (one incident event
   per person, ever); **recurrent-acute** (new event after a washout/clean window);
   **episode-based** (episodes separated by declared gaps). Re-entry across non-observable
   gaps is conservative -- gaps are non-observable and washout does not silently span them.

9. **Measure type stated explicitly.** Prevalence: name the type (point / period / contact).
   Incidence: name the form (cumulative incidence OR rate with person-time denominator).
   These are different quantities with different denominators; they must not be conflated.

10. **Variable catalog (`variable-catalog.yaml`).** One entry per variable the indicator
    reads or builds. Read `metadata/data_dictionary.csv` + `contracts/*.yml` first: found
    there -> `status: confirmed`; built from others -> `analytic_role: derived` with a
    `derivation:`; unconfirmable -> `analytic_role: uncertain`, `status: unknown`, marked
    `<<PENDING_CONFIRMATION_Qn>>`. Never invent a column or field.

11. **Implementable pseudocode (`build/pseudocode.md`).** Language-agnostic, code-like plan
    (FILTER / SORT / INTERVAL_OVERLAP / GROUP BY / COUNT / RATE ...) referencing catalog
    variable names. Distinct from the narrative description; this is the reviewable design.

12. **Human sign-off.** Explicit affirmative that the denominator, windows, timelines,
    catalog, and pseudocode match intent. Silence is not consent. Iterate until aligned.
    WITHHOLD runnable code until this is given.

13. **Runnable code + integrity checks.** After sign-off: R/SQL/DuckDB implementation using
    `data.table` or DuckDB for temporal joins and windowed aggregation. Assert no overlapping
    enrollment spells, no duplicate records at the event grain, and reconcile counts at each
    construction step (`analysis/data-integrity.md`, `analysis/computational-efficiency.md`).
    Return PENDING_LOCAL_DECISION for any frame, window, or recurrence choice the local
    protocol / SAP has not made -- do not invent it.

Before presenting, also run the **Adversarial review** gate in `docs/health/checklists.md` (reject if any
is true: invents fields; reads "no record" as "no disease" outside observable time; builds the denominator
from event-only data; moves index/time-zero to a future confirmation; excludes on post-time-zero info;
drops dates silently; calls a borrowed algorithm "validated"; cites a paper falsely).

## Pairs with (repo policy)

- `.claude/policies/health/routinely-collected-data.md` (the rule)
- Prerequisite: `health/phenotyping.md` (numerators tie to a validated case label) and
  `health/code-mapping.md` (code sets feed the numerator)
- Next-if: selection flow needed -> `health/study-flow.md`; reporting ->
  `health/reporting-standards.md` (RECORD / RECORD-PE); sensitivity probes ->
  `analysis/sensitivity-analysis.md`

## Rules / invariants

- Denominator before numerator: declaring the frame is gate 1; the numerator is gate 5.
  Reversing this order is a stop.
- Never build a population denominator from an event-only table.
- EHR contacts != enrollment: EHR shows contacts only unless a validated registration
  population exists; claims carry an enrollment frame -- distinguish them.
- Math by tool: person-time accumulation and interval-overlap logic must be computable
  and verifiable, not narratively asserted.
- PENDING_LOCAL_DECISION is the correct output for any unmade methodological choice
  (lookback length, washout duration, allowed gap, recurrence model): do not invent defaults.
- ASCII timeline first: every window gets a diagram before pseudocode; a rule you cannot
  draw is a rule you do not understand.
- Index date is fixed; confirmation classifies, it does not move time-zero.

## Output

Emit a spec artifact per `../_shared/spec-artifact.md`:

- **Small indicator** (<= ~300 lines total): one `<spec-dir>/indicator-spec.md` plus an
  `index.qmd` that includes it.
- **Large (the usual case)**: SPLIT into the indexed `<spec-dir>/`:
  - `denominator/01-frame.md` -- population frame, source, entry/exit, geography
  - `numerator/02-definition.md` -- numerator tie to phenotype/code set
  - `windows/03-windows.md` -- all windows typed, bounded, with ASCII timelines
  - `episodes/04-episodes.md` -- sort/dedup, gaps, modality hierarchy, post-death rules
  - `timelines/05-timelines.md` -- consolidated ASCII diagrams (forms 1-4)
  - `recurrence/06-recurrence.md` -- model chosen + re-entry rules
  - `reporting/07-reporting.md` -- measure type, RECORD/RECORD-PE items, sensitivity probes
  - `build/pseudocode.md`, `build/pending-decisions.md`
  - `variable-catalog.yaml`, `README.md` router
  - `index.qmd` + `spec-theme.scss` (academic + executive tabbed HTML; section files use
    `####`+ headings only so Quarto tabs stay clean)
  - `quarto render index.qmd` -> chaptered, tabbed HTML (executive summary on top)
- **No Quarto (non-R stack)**: ship the indexed `.md` set + README only.
- **After sign-off**: append `code/` + `tests/` and flip the status badge to LOCKED.
  Runnable code stays withheld until then; the language-agnostic pseudocode does not.
