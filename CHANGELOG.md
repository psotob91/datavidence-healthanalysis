# Changelog

Notable changes to **datavidence-healthanalysis** (the health-data domain plugin).
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-06-29

### Added
- **Block 7 -- pre-registration enforcement layer** (the tsukuba "mandatory pre-registration"
  paradigm). New **`preregister`** skill: consolidates the upstream design artifacts (estimand/SAP,
  sensitivity plan, phenotype/exposure definitions, variable catalog, population frame) into ONE
  lockable `analysis/prereg/pre-registration.yaml` + `population_cascade.yaml`, locks on explicit
  human sign-off via `validation/logs/sap_lock.json` (content-hashed), and records post-lock changes
  in a deviations log -- never a silent edit. Plus 3 fail-open, opt-in, stdin-tested hooks:
  `sap_lock` (PreToolUse -- asks before analysis/model writes when the pre-registration is not
  locked), `attrition_log` (PostToolUse -- flags filtering scripts missing `log_attrition()`),
  `variable_catalog_gate` (PreToolUse -- asks on scripts referencing `status: unknown` variables in
  the variable spec catalog). Cold-read audited (generator != auditor; P1/P2 fixes applied) and
  behavior-evaluated (+0.65: 100% vs 35% baseline). Skill count **21 -> 22**.
- **Block-4 behavior-eval completed** for the remaining 5 skills (`dag-causal`,
  `specify-sensitivity-plan`, `review-outliers`, `big-data-triage`, `draft-diagram`):
  with-skill 100% vs baseline mean 36% (mean improvement +0.64). Identical task per arm,
  rubric-scored, generator != auditor. Record: `docs/evals/2026-06-29-block4-behavior-eval.md`.

### Changed
- Renamed plugin `datavidence-healthdata` → **`datavidence-healthanalysis`** (name, marketplace,
  homepage, docs, templates).
- DEVELOPMENT_GUIDE aligned with the template's validated policies + Anthropic 2026 best practices:
  third-person skill descriptions (`name` ≤64 chars; body ≤500), `.mcp.json` for bundling
  `r-btw`/WolframAlpha, a `SubagentStop` hook to enforce non-negotiables, explicit
  `claude plugin validate`, and `data_leak_guard` aligned to the simplified `data-protection` policy.

- **Skill descriptions disambiguated** (trigger-collision fixes from a 2-router routing audit,
  description-only): `dag-causal` (target-trial framing -> frame-study), `frame-study` (added
  target-trial / estimand triggers), `validate-assumptions` (added post-fit influence triggers:
  Cook's distance / DFBETA / leverage), `draft-diagram` (narrowed the timeline trigger to
  project/enrollment), `phenotype-gate` (added decision/temporal ASCII-timeline trigger).
  All 15 boundary prompts route CLEAN_WIN.

## [0.1.0] - 2026-06-29

### Added
- **21 thin-verb skills** (markdown-only) operationalizing the template policies, built block by block
  and behavior-evaluated (with-skill vs baseline, structural assertions, viewer):
  - Health: `phenotype-gate` (exemplar; comprehension gate + variable catalog + implementable
    pseudocode), `map-clinical-codes`, `design-indicator`, `scaffold-reporting`.
  - STRATOS core: `frame-study`, `run-ida`, `validate-assumptions`, `assess-missingness`,
    `numeric-check`, `specify-regression`, `specify-sensitivity-plan`, `review-outliers`,
    `big-data-triage`, `draft-diagram`.
  - Data: `onboard-data`, `validate-data-contract`. Panel: `method-audit`.
  - Opt-in modules: `dag-causal`, `prediction-validation`, `survey-design`, `spatial`.
- **Shared core** `skills/_shared/{health-principles,spec-artifact}.md` (math-by-tool, claim->evidence,
  PENDING_LOCAL_DECISION; the split-indexed + academic/executive Quarto-rendered spec-artifact format).
- **Hooks** (fail-open, stdlib, `hooks/hooks.json`): `guard_data_export.py` (PreToolUse egress guard,
  ask-not-deny, opt-in to health children), `notation_check.py` (PostToolUse). Tested via piped stdin.
- **Reviewer subagents**: `methodologist`, `statistician`, `reporting-reviewer` (sonnet, read-only).

### Changed
- `plugin.json` description + version (0.0.1 -> 0.1.0); no `hooks` key (auto-discovered).
- Eval results: Block 1 +0.51, Block 2 +0.63, Block 3 +0.61, Block 4 +0.62 (with-skill vs baseline).

## [0.0.1] - 2026-06-27

### Added
- Initial **skeleton** scaffold: `.claude-plugin/{plugin.json,marketplace.json}`,
  `skills/SKILL_TEMPLATE.md`, `agents/SUBAGENT_TEMPLATE.md`, `hooks/` + `commands/` placeholders,
  `README.md`, `CLAUDE.md`.
- `docs/DEVELOPMENT_GUIDE.md` — the single, self-contained development spec (handoff doc): planned
  skills/hooks/subagents, progressive-disclosure conventions, fail-open hook bootstrapper, subagent
  model tiers (haiku/sonnet/opus), orchestration patterns, math-via-tools rule, the frozen interface
  with the template repo, and the reconciliation step.

> Skeleton only — no functional skills/hooks/subagents yet. Built to be configured in a separate
> session using the development guide.
