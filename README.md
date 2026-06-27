# datavidence-healthanalysis

A **domain plugin** (Claude Code) for reproducible **biostatistics / health-data analysis with R**.
It provides the **skills, governance hooks, and reviewer subagents** that the
[`datavidence-template-project`](https://github.com/psotob91/datavidence-template-project) policies
invoke. Companion to — and orthogonal with — [`psotobverse-utils`](https://github.com/psotob91/psotobverse-utils).

> **Status: SKELETON (v0.0.1).** Under construction. This repo currently ships only scaffolding +
> the development spec. Do not install for production use yet.

## The three-layer architecture

| Layer | Lives in | Holds |
| --- | --- | --- |
| **Governance / structure** | `datavidence-template-project` (the repo template) | policies (rules), folder contracts, doc templates, R stack, CI |
| **Generic workflow** | `psotobverse-utils` (plugin) | index, goal, reconcile, deliberate, tidy + generic hooks/subagents |
| **Health-data domain** | **this plugin** | domain skills, domain hooks, reviewer subagents |

**Orthogonality rule:** policies/standards live in the template repo; generic workflow lives in
`psotobverse-utils`; **only domain verbs/guards live here.** If a project name, path, or concrete
command leaks into a skill, it is in the wrong place.

## What this plugin will provide (planned)

- **Skills:** `numeric-check`, `data-contract`, `missingness-report`, `validate-assumptions`,
  `big-data-triage`, `table1`, `cohort-flow`, `eda`/`ida`, `onboard-data`, `method-audit`,
  `flowchart-sketch`, `process-diagram`; opt-in: `dag-causal`, `survey-design`,
  `prediction-validation`, `spatial`.
- **Hooks (fail-open):** `data_leak_guard`, `notation-check`, `provenance-stamp`.
- **Subagents:** `methodologist`, `statistician`, `reporting-reviewer` (+ reuse of `executor`/`explorer`).

## Build it

See **[`docs/DEVELOPMENT_GUIDE.md`](docs/DEVELOPMENT_GUIDE.md)** — the single, self-contained spec
for developing the skills, hooks, and subagents (conventions, model tiers, orchestration patterns,
math-via-tools rule, the frozen interface, and the reconciliation step with the template repo).

## License

[MIT](LICENSE) © 2026 Percy Soto-Becerra
