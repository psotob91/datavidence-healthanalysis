---
name: skill-name-here
description: >-
  One paragraph in natural language that makes this skill AUTO-INVOKE via progressive
  disclosure. Include the phrases a user would actually say ("build a Table 1", "check
  this number", "draw the participant flow"). Keep triggers DISJOINT from other skills
  to avoid ambiguous invocation. State the boundary explicitly: "for X use this; for the
  generic workflow use psotobverse-utils; for Y use <other-skill>." Narrowest applicable
  skill wins.
---

# /datavidence-healthdata:skill-name-here

> Reference template. Copy this folder to `skills/<name>/SKILL.md` and fill it in.
> Body should stay under ~250 lines (progressive disclosure — push detail to referenced files).

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
