# Changelog

Notable changes to **datavidence-healthanalysis** (the health-data domain plugin).
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Changed
- Renamed plugin `datavidence-healthdata` → **`datavidence-healthanalysis`** (name, marketplace,
  homepage, docs, templates).
- DEVELOPMENT_GUIDE aligned with the template's validated policies + Anthropic 2026 best practices:
  third-person skill descriptions (`name` ≤64 chars; body ≤500), `.mcp.json` for bundling
  `r-btw`/WolframAlpha, a `SubagentStop` hook to enforce non-negotiables, explicit
  `claude plugin validate`, and `data_leak_guard` aligned to the simplified `data-protection` policy.

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
