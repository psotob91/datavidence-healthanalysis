---
name: skill-name-here   # lowercase letters / numbers / hyphens, <= 64 chars, no reserved words
description: >-
  THIRD PERSON — what it does + when to use it (<= 1024 chars). Include the phrases a user would
  actually say so the skill AUTO-INVOKES. Example: "Builds a publication-ready Table 1
  (descriptive or comparative) with gtsummary, honoring variable labels and the reporting policy;
  use when the user asks for a baseline / participant-characteristics table." Do NOT write in
  second person ("You can use this…") — that breaks Skill discovery. Keep triggers DISJOINT from
  sibling skills; the narrowest applicable skill wins (state the boundary here).
---

# /datavidence-healthanalysis:skill-name-here

> Reference template. Copy this folder to `skills/<name>/SKILL.md` and fill it in.
> Body ≤ 500 lines (aim ≤ 250): state *what* to do, not why — the loaded body is a recurring
> token cost. Push detail into referenced files (progressive disclosure).

## When to use / when NOT to use
- Use it when: …
- Do NOT use it when: … (point to the right skill instead)

## What it does (the procedure)
1. …
2. …

## Pairs with (repo policy)
- This skill operationalizes the repo policy `…` (the policy states the rule; this skill performs it).

## Rules / invariants
- Delegate ALL math to tools (R / WolframAlpha MCP) — never compute mentally.
- Anchor every claim to `file:line` or reproducible output.
- Ask before irreversible or outward-facing actions.

## Output
- … (what the user gets back)
