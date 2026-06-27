# CLAUDE.md — datavidence-healthdata (plugin dev guidance)

You are working inside the **datavidence-healthdata** plugin: the health-data / biostatistics
**domain** layer for the datavidence ecosystem.

## Read first
1. `docs/DEVELOPMENT_GUIDE.md` — the complete spec (skills, hooks, subagents, conventions, model
   tiers, orchestration, the frozen interface with the template repo). **This is the source of truth
   for what to build and how.**
2. `README.md` — the three-layer architecture and orthogonality rule.

## Hard rules (do not violate)
- **Orthogonality.** Only **domain** verbs/guards live here. Generic workflow → `psotobverse-utils`.
  Policies/structure → the `datavidence-template-project` repo. No project names/paths in skills.
- **Do NOT declare `"hooks"` in `plugin.json`** — `hooks/hooks.json` is auto-discovered (declaring it
  triggers "Duplicate hooks file detected" and the whole plugin fails to load).
- **Hooks are fail-open** and use the `python -c` bootstrapper that reads `CLAUDE_PLUGIN_ROOT` by name
  from `os.environ` (portable across bash/cmd/PowerShell; works in Cowork). If env var/script absent →
  `sys.exit(0)`. (Same pattern as psotobverse-utils v1.3.1.)
- **No command/skill name collisions** (a `commands/<x>.md` + `skills/<x>/SKILL.md` with the same name
  registers as a duplicate skill — keep one).
- **Math is never done by the model** — delegate to R / WolframAlpha MCP.
- Keep a `CHANGELOG.md`. After any `claude plugin` change, restart the session so hooks reload.

## The frozen interface
The template repo routes to this plugin **by name**. Do not rename skills/hooks/subagents without
updating the template's knowledge-map + policies. See `docs/DEVELOPMENT_GUIDE.md` → "Frozen interface".
