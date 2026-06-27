# datavidence-healthdata — Development Guide (single handoff spec)

> **Purpose.** This is the complete, self-contained brief for building the `datavidence-healthdata`
> Claude Code plugin. Hand this file's path to a fresh Claude Code session (plus any ChatGPT-prepared
> material) and it has everything needed to build the skills, hooks, and subagents correctly and to
> couple cleanly with the `datavidence-template-project` repo.
>
> **Status:** the repo is a skeleton (v0.0.1). Nothing functional is built yet.

---

## 1. Where this plugin sits (orthogonality — read this first)

Three layers, never mixed:

| Layer | Lives in | Holds |
| --- | --- | --- |
| Governance / structure | `datavidence-template-project` (repo template) | **policies (rules)**, folder contracts, doc templates, R stack, CI |
| Generic workflow | `psotobverse-utils` (plugin) | index, goal, reconcile, deliberate, tidy + generic hooks/subagents |
| **Health-data domain** | **this plugin** | **domain skills, domain hooks, reviewer subagents** |

**Rules of placement:**
- A standing **rule/standard** → it is a **policy** and belongs in the template repo, NOT here.
- A **procedure you invoke** → **skill** (here).
- A **deterministic block** → **hook** (here).
- A **separate evaluating role** → **subagent** (here).
- Many items are a **policy + skill pair**: the repo policy states the rule and routes (by name) to a
  skill in this plugin that performs it.
- **Golden rule:** if a concrete project name, path, or command leaks into a skill, it is misplaced.

---

## 2. The frozen interface (contract with the repo)

The template repo's `knowledge-map` and policies route to this plugin **by name**. Treat these names
as a **frozen contract** — renaming requires updating the repo too. Invocation is namespaced:
`/datavidence-healthdata:<skill>`.

**Skills (build these):**
| Skill | Pairs with repo policy | Backing R package(s) |
| --- | --- | --- |
| `numeric-check` | numeric-computation | (R code; WolframAlpha MCP for symbolic) |
| `data-contract` | data-integrity | `pointblank` |
| `missingness-report` | missingness | `mice`, `naniar` |
| `validate-assumptions` | (assumptions guideline) | `performance`, `car`, `survival::cox.zph` |
| `big-data-triage` | long-compute | `data.table`, `duckdb`, `arrow` |
| `table1` | reporting | `gtsummary` |
| `cohort-flow` | diagrams | `flowchart` (bruigtp) |
| `eda` / `ida` | (IDA guideline) | `summarytools` |
| `onboard-data` | data-onboarding | `rio`, `here`, `summarytools` |
| `method-audit` | (verification-effort) | panel of subagents (see §5) |
| `flowchart-sketch` | diagrams | text/line sketch first (no numbers) |
| `process-diagram` | diagrams | mermaid (ISO 5807 nomenclature) |

**Opt-in skills (only when the project needs them — never forced):**
`dag-causal` (`dagitty`/`ggdag`), `survey-design` (`survey`/`srvyr`), `prediction-validation`
(`rms`/`pmsampsize`, TRIPOD), `spatial` (`sf`/`terra`/`stars`).

**Hooks (fail-open):** `data_leak_guard`, `notation-check`, `provenance-stamp`.

**Subagents:** `methodologist`, `statistician`, `reporting-reviewer` (+ reuse `executor`/`explorer`
from `psotobverse-utils`).

---

## 3. Skill conventions (progressive disclosure)

- One folder per skill: `skills/<name>/SKILL.md` (see `skills/SKILL_TEMPLATE.md`).
- Frontmatter `description` = natural-language triggers that make the skill **auto-invoke**. Include
  phrases users actually say. Keep triggers **disjoint** across skills (avoid ambiguous matches).
  Conflict rule: **narrowest applicable skill wins** — state the boundary in the description.
- Body ≤ ~250 lines; push detail into referenced files (progressive disclosure).
- Each skill: state when-to-use / when-NOT, the procedure, the policy it pairs with, invariants, output.
- **Never compute math in the model** — delegate to R (via `executor`) or WolframAlpha MCP (§6).
- Anchor every claim to `file:line` or reproducible output (no invented numbers/citations).

---

## 4. Hook conventions (fail-open, stdlib only)

- Register in `hooks/hooks.json`. **Do NOT declare `"hooks"` in `plugin.json`** (auto-discovered;
  declaring it → "Duplicate hooks file detected" → whole plugin fails to load).
- Use the **`python -c` bootstrapper** that reads `CLAUDE_PLUGIN_ROOT` **by name** from `os.environ`
  (no `${...}`, no inner double quotes → portable bash/cmd/PowerShell; works in Cowork) and `runpy`s
  the real hook; if env var/script absent → `sys.exit(0)` (**FAIL-OPEN**). This is the
  `psotobverse-utils` v1.3.1 pattern — reuse it verbatim.
- **Do NOT redefine** the generic write-guards (`nothing_loose`, `env_protect`) — those are owned by
  `psotobverse-utils`.
- Domain hooks to build:
  - `data_leak_guard` — block identifiable datasets/PII from reaching git / `outputs/` / `context/`
    and from being dumped into the prompt; small-cell awareness.
  - `notation-check` — verify mathematical notation used in methods exists in the repo's `notation.md`.
  - `provenance-stamp` — stamp outputs with commit SHA + data hash + timestamp.

---

## 5. Subagents and orchestration

- Define roles in `agents/<role>.md` (see `agents/SUBAGENT_TEMPLATE.md`): `description`, minimal
  `tools`, and `model`.
- Reviewer roles for `method-audit`: `methodologist` (design validity), `statistician` (statistical
  correctness), `reporting-reviewer` (EQUATOR / reporting standards).
- **Model tiers** (per Anthropic guidance, Jun 2026):
  - Mechanical/execution (`executor`, `explorer`) → **haiku**.
  - Evaluation/judgment (the reviewers, adversarial verifiers) → **sonnet** by default
    (best anti-hallucination profile; Anthropic advises starting judges at Sonnet).
  - Deep/critical gates (final `method-audit`, publication numbers) → **opus**.
- **Orchestration patterns** (pick by stakes):
  1. **Voting panel** (independent, perspective-diverse) → high-stakes/multifaceted judgments
     (`method-audit`; "is this number/finding real?"). The fan-out + synthesis is done by a **skill**,
     not by a subagent.
  2. **Deliberation/consensus** (agents converse and converge) → hard, open design choices. Expensive
     → **rare and gated**.
  3. **Generator ≠ auditor** (fresh cold-read tries to refute) → routine verification (already in
     `psotobverse-utils`).
- **Adversarial depth tiers** (tie to the repo's `verification-effort` policy):
  - **Light** = 1 cold-read auditor. **Standard** = 3 voters (2/3 majority).
    **Deep** = 5 diverse voters + synthesis, with anti-sycophancy gate (concede only at evidence ≥4/5).
  - Default = light; escalate by stakes (paper numbers, key conclusions, final method-audit).
- **Do NOT orchestrate** cheap/mechanical tasks (single agent). Panels cost tokens → critical gates only.

---

## 6. Mathematics: ALWAYS via tools (LLMs do not compute)

- **No mental math, ever** — for any number, percentage, CI, p-value, count, or table total.
- Numeric computation → **R code** (run via the `executor` subagent or the analysis pipeline).
- Symbolic/algebraic → **WolframAlpha MCP** (available in session) or `sympy` / `Ryacas` / `symengine`.
- Subagents **reason** about methodology; when they need a figure they **delegate to code** and cite
  the result. This enforces the repo's `numeric-computation` policy: *reasoning ≠ computing*.

---

## 7. Validation & release

- **Test everything installed together** (`psotobverse-utils` + this + `posit-dev/skills` +
  `arthurgailes/r-package-skills`): no ambiguous triggers, no conflicting hooks.
- Validate skills `r-package-skills`-style: baseline without the skill → write the minimal SKILL.md →
  iterate until tests pass (≥90%).
- Keep `CHANGELOG.md` (Keep a Changelog + SemVer).
- Remember the **Cowork plugin-sync lag** (server-side sync, separate from CLI `~/.claude`; see the
  template's ADR-0002). After any `claude plugin` change, restart the session so hooks reload.

---

## 8. Reconciliation with the repo (the final step)

Once this plugin has minimal working skills, run a coupling pass **with the template repo**:
1. Install all plugins; render a project from `datavidence-template-project`.
2. Verify the skills auto-invoke from the repo's knowledge-map/policy routing.
3. Verify there are no trigger/hook conflicts across plugins.
4. Verify graceful degradation: the rendered project still works with this plugin **absent**.

Use the `/reconcile` pattern (generator ≠ auditor, cold-read). Fix drift on **either** side
(rename here ⇒ update repo routing, or vice versa) until the interface matches.
