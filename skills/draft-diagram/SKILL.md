---
name: draft-diagram
description: >-
  Drafts PROCESS and METHOD diagrams for health-data studies: pipeline flowcharts, analysis
  method diagrams, ER diagrams, and timeline/Gantt charts using Mermaid with ISO 5807
  nomenclature and colorblind-safe encoding. Use when the user asks for a process diagram,
  method diagram, flowchart of the pipeline, mermaid diagram, ER diagram, data-flow diagram,
  entity-relationship diagram, analysis pipeline diagram, data model diagram, or a Gantt chart for a project schedule or enrollment-milestone timeline.
  Operationalizes analysis/diagrams.md (sketch-first approval gate, ISO 5807 shapes,
  Okabe-Ito colors, Crow's Foot ER, ISO 8601 dates).
  NOT for participant or cohort flow diagrams (CONSORT/STROBE/PRISMA) — use scaffold-reporting.
  NOT for phenotype decision or temporal-logic diagrams — those use the ASCII notation in
  phenotype-gate and design-indicator (docs/health/ascii-timelines.md).
---

# /datavidence-healthanalysis:draft-diagram

> Operationalizes `.claude/policies/analysis/diagrams.md`. Apply
> `../_shared/health-principles.md` (claim-to-evidence, PENDING_LOCAL_DECISION,
> comprehension-before-code) and emit the artifact per `../_shared/spec-artifact.md`.
> The sketch-first approval gate runs for EVERY diagram type before any Mermaid code
> is written.

## When to use / when NOT to use

- **Use it when:** the user needs a process or method diagram — pipeline flowchart,
  analysis workflow, data-flow diagram, ER / data-model diagram, or a timeline / Gantt
  for enrollment milestones, project schedule, or follow-up windows.
- **Do NOT use it when:**
  - The user needs a participant or cohort flow diagram (CONSORT / STROBE / PRISMA
    or a RECORD-style selection flow) — use `scaffold-reporting`.
  - The user needs a clinical time-based decision or temporal diagram for a phenotype
    algorithm or indicator window — use `phenotype-gate` or `design-indicator` (they
    draw ASCII timelines per `docs/health/ascii-timelines.md` as the comprehension gate).

## Step 0 — Sketch-first approval gate (ALL diagram types, no skipping)

Before producing any Mermaid block, produce a **plain-text sketch** listing:
- Nodes / boxes with their label and shape type (process, decision, data, database, …)
- Connections (arrows + optional labels)
- Any PENDING choices (e.g. "legend color assignment unmade")

**No numbers in the sketch** -- counts, rates, or computed values must NOT
appear in the plain-text sketch (they come from code output in the final diagram,
per the math-by-tool invariant). Present structure only.

**No Mermaid syntax yet.** Present the sketch and **get explicit human approval**.
Silence is not consent. Iterate until the structure is agreed. Only after sign-off
proceed to the type-specific step below.

If a design choice is unmade, return `PENDING_LOCAL_DECISION` and name the choice;
do not invent a default layout.

---

## Type A — Process / method flowchart (Mermaid `flowchart`)

> **Note:** data-flow diagrams are handled as Type A process flowcharts --
> they share the same ISO 5807 shapes and Okabe-Ito encoding; no separate
> diagram type is defined in the policy.

**Policy:** `.claude/policies/analysis/diagrams.md` (ISO 5807 shapes + Okabe-Ito colors)

After the sketch is approved:

1. Map every node to an ISO 5807 shape using Mermaid syntax:

   | Kind | ISO 5807 | Mermaid syntax |
   |---|---|---|
   | Process / step | Rectangle | `[Label]` |
   | Decision | Diamond | `{Label}` |
   | Data I/O | Parallelogram | `[/Label/]` or `[\Label\]` |
   | Database / store | Cylinder | `[(Label)]` |
   | Terminator (start/end) | Stadium | `([Label])` |
   | Predefined process / subroutine | Double-rectangle | `[[Label]]` |
   | Document | Document shape | `[/Label\]` *(Mermaid approximation)* |

2. Apply **colorblind-safe, shape-redundant encoding** (Okabe-Ito palette):
   use `style` or `classDef` directives; pair each color with its distinct shape so
   the diagram is readable without color. Include a concise legend node or comment.

3. Emit the Mermaid block and the diagram spec (see Output). Mark any unmade styling
   or layout choice as `PENDING_LOCAL_DECISION`.

---

## Type B — ER diagram (Mermaid `erDiagram`)

**Policy:** `.claude/policies/analysis/diagrams.md` (Crow's Foot / IE; tied to `contracts/`)

After the sketch is approved:

1. Use `erDiagram` with **Crow's Foot / Information Engineering notation** (the
   Mermaid default). Do NOT mix ER notations within a project.
   - Reserve **UML class diagram** (`classDiagram`) if ISO/IEC 19505 notation is
     explicitly requested.
   - Reserve **IDEF1X** for formal contractual schemas only (ISO/IEC/IEEE 31320-2).
2. Tie every entity and attribute to `contracts/*.yml` or `metadata/data_dictionary.csv`.
   An entity that cannot be anchored gets a `<<PENDING_CONFIRMATION_Qn>>` comment.
3. State cardinality explicitly on each relationship line.

---

## Type C — Timeline / Gantt (Mermaid `timeline` or `gantt`)

**Policy:** `.claude/policies/analysis/diagrams.md` (ISO 8601 dates, no ISO notation standard)

After the sketch is approved:

1. Use `gantt` for task / milestone charts; use `timeline` for narrative chronology.
2. Conventions:
   - One clearly-labeled, monotonic time axis.
   - Tasks as bars; milestones as diamonds (`milestone`); dependencies as arrows.
   - All dates in **ISO 8601** (`YYYY-MM-DD`); durations in explicit units.
3. Gantt charts are **code-generated** — do not hard-code counts or dates that should
   come from a data step. If real values are unavailable, use placeholder labels and
   mark them `PENDING_LOCAL_DECISION`.

> Note: ISO 21500/21502 cover project management *process*, not Gantt notation —
> there is no ISO Gantt notation standard. Follow the Mermaid convention above.

---

## Pairs with (repo policy)

- `.claude/policies/analysis/diagrams.md` (the rule — shapes, colors, notation choice)
- **NOT-for boundary:**
  - Participant/cohort flow (CONSORT / STROBE / PRISMA / RECORD selection flow) →
    `scaffold-reporting` (uses the `flowchart` R package, not Mermaid).
  - Clinical temporal-logic and decision diagrams for phenotypes / indicators →
    `phenotype-gate` / `design-indicator` (ASCII timelines in `docs/health/ascii-timelines.md`).

## Rules / invariants

- Sketch first, always: no Mermaid code before the plain-text sketch is approved.
- One notation per project: do not mix Crow's Foot / UML class / IDEF1X within a project.
- Shape-redundant encoding: color alone does not convey information; pair color with shape.
- Colorblind-safe: use Okabe-Ito (`#E69F00`, `#56B4E9`, `#009E73`, `#F0E442`,
  `#0072B2`, `#D55E00`, `#CC79A7`, `#000000`).
- ISO 8601 dates in all Gantt / timeline charts; no ambiguous date formats.
- PENDING_LOCAL_DECISION for any unmade design choice; do not invent a layout default.
- Math by tool (from `../_shared/health-principles.md`): counts or computed values that
  appear in a diagram node must come from code output, not mental arithmetic.

## Output

Emit a simple diagram artifact:
- **Single diagram:** one file `docs/analysis/diagrams/<name>-diagram.md` containing
  the approved sketch (plain text), the final Mermaid block, a brief legend / key,
  and any `PENDING_LOCAL_DECISION` items.
- **Multi-diagram spec** (e.g. pipeline + ER + Gantt for the same study): split into
  `docs/analysis/diagrams/<name>/` with one file per diagram type and a `README.md`
  router (one row per file: `| File | Diagram type |`).
- After sign-off and all PENDING items resolved: the Mermaid blocks are the final
  deliverable; no separate "code" step needed (the diagram IS the code).
