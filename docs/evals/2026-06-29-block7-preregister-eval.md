# Block 7 — pre-registration enforcement: audit + behavior-eval

**Date:** 2026-06-29
**Branch:** feat/healthanalysis-block7-enforcement
**Scope:** the tsukuba "mandatory pre-registration" enforcement layer for the plugin:
the `preregister` skill + 3 hooks (`sap_lock`, `attrition_log`, `variable_catalog_gate`).
Source spec: the blueprint Block-7 backlog + `docs/audits/2026-06-28-tsukuba-audit/`.

## 1. What was built (and what was deliberately deferred)

- **`preregister` skill** -- consolidates the upstream design artifacts into ONE lockable
  `analysis/prereg/pre-registration.yaml` (+ `population_cascade.yaml`), locks on explicit
  human sign-off via a content-hashed `validation/logs/sap_lock.json`, and tracks post-lock
  changes in a deviations log. The file-existence lock is the gate (the most reliable mechanism
  in the audited repo).
- **3 hooks** (fail-open, opt-in, stdlib-only, stdin-tested):
  - `sap_lock` (PreToolUse) -- asks before productive analysis/model writes when the
    pre-registration is not locked.
  - `attrition_log` (PostToolUse) -- flags filtering scripts that drop rows without calling
    `log_attrition(step, n_in, n_out, excludes_target_population, reason)`.
  - `variable_catalog_gate` (PreToolUse) -- asks on scripts referencing a `status: unknown`
    variable in the variable spec catalog.
- **Deferred (NOT this plugin, per blueprint):** the generic `rescue-manifest` skill (belongs in
  `psotobverse-utils` -- migration is domain-agnostic) and the template structure changes
  (human/agent `source/`-vs-`context/` split, metadata two-taxonomy). Wiring `preregister` into
  the template `knowledge-map.md.jinja` / trigger-lexicon is a small follow-up (template repo).

## 2. Cold-read audit (generator != auditor; Sonnet)

A fresh Sonnet auditor that did not see the design reasoning tried to refute the skill + hooks.
Findings and dispositions:

| Sev | Finding | Disposition |
|---|---|---|
| P1 | `variable_catalog_gate` catalog parser: `status:` in a free-text string, or `status:` appearing before its `variable_id:`, mis-flags a variable | FIXED -- anchored `_VAR_RE`/`_STATUS_RE` to line-start; reset `cur` after each status |
| P2 | `attrition_log` `\bWHERE\b` with IGNORECASE fires on "where" in prose/comments | FIXED -- dropped IGNORECASE from `_DROP_RE` (SQL `WHERE` uppercase; lowercase function calls) |
| P2 | skill documents only `variable_spec_catalog.yaml`; hook also accepts the `variable-catalog.yaml` alias | FIXED -- alias documented in the skill |
| P2 | `sap_lock`/`variable_catalog_gate` matchers omit `Bash` (`echo > x.R` bypasses) | DECLINED -- the model authors via Write/Edit; parsing shell redirection adds false-positive risk to an advisory gate. Documented as a known limitation |
| P2 | `attrition_log` opt-in gate (`metadata/`) is broad | DECLINED -- consistent with the sibling `guard_data_export` gate; an advisory good-practice nudge for health children |
| P3 | trigger overlap `preregister` vs frame-study ("lock the SAP") | No change -- differentiated (draft vs lock); auditor agreed |
| P3 | "no lock over PENDING" not hook-enforced | Acceptable -- enforced within the skill workflow (advisory posture) |

All hook fixes re-verified: 8/8 behavioral tests pass, incl. the string-trap false-positive guard
and WHERE/where case-sensitivity; opt-in no-op + empty-stdin fail-open confirmed.

## 3. Behavior-eval (with-skill vs baseline; Sonnet producers, rubric-scored)

Task: "freeze our estimand/SAP + sensitivity plan + phenotype definitions before any code; how do
we lock this in and what does the artifact look like?"

| | Baseline | With-skill | Delta |
|---|---|---|---|
| `preregister` | 35% (3.5/10) | 100% (10/10) | +0.65 |

Baseline gave reasonable generic advice (git tag + SHA manifest + signed freeze certificate +
amendment protocol + OSF) but no single canonical artifact, no `status: locked` gate file that
tooling checks, no `population_cascade`, no `log_attrition` contract, and no "PENDING blocks the
lock" rule. With-skill produced exactly the enforceable single-artifact paradigm with the gate file,
the cascade, the deviations log, and the content hash. Consistent with Blocks 1-4 (+0.51..+0.64).
