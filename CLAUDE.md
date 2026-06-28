# CLAUDE.md — datavidence-healthanalysis (plugin dev guidance)

You are working inside the **datavidence-healthanalysis** plugin: the health-data / biostatistics
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

## This repo governs itself (dogfooding)
`.claude/` opts this repo into the guardrails shipped by the installed `psotobverse-utils`:
`constitution.md` (follows that plugin's `_shared` charter + the domain rules above),
`knowledge-map.md`, `policy/paths.allow.json` (self-guard, consumed by the installed
`nothing_loose`), and `meta-learner.json` (captures plugin-authoring lessons to `learning/`).
Hygiene (`.editorconfig`/`.gitattributes`/`.gitleaks.toml`) + CI (`validate-plugin`) are in place.
The routing/recall/comprehension **mechanism is generic** (`psotobverse-utils`); this plugin will
ship only domain **data** (`routing.yml` rows) + validating skills, never its own routing engine.

## Safe-edit protocol (the circularity is safe)
This repo is **factory and plugin at once** — the installed plugins' hooks govern sessions that edit
it. Safe dogfooding, because:
- the **installed (cache) copy fires, not the source you edit here** — editing a hook is inert until
  `claude plugin update`, so you cannot brick the live session;
- per-project **config is read live** — adding `.claude/policy/paths.allow.json` guards this repo
  immediately (config live; hook *behavior* changes need an update);
- **fail-open ⇒ no lock-out**; test a hook by piping a simulated event
  (`echo '<json>' | python hooks/<hook>.py`) rather than trusting the live hook to validate its edit.
