# Knowledge map — datavidence-healthanalysis (developing the plugin)

A router. Open the one file the task needs.

## Read-first
1. `.claude/constitution.md`
2. `docs/DEVELOPMENT_GUIDE.md` — the source of truth for what to build and how
3. `README.md`, then this map

## Task → consult

| Task | Consult |
|------|---------|
| What to build / the frozen interface | `docs/DEVELOPMENT_GUIDE.md` |
| The pending spec (skills + hooks) | `datavidence-template-project/docs/plugins/datavidence-healthanalysis-blueprint.md` |
| Add a domain **skill** | `skills/<name>/SKILL.md` (template: `skills/SKILL_TEMPLATE.md`) |
| Add a domain **hook** | `hooks/<name>.py` + create `hooks/hooks.json` (fail-open bootstrap; auto-discovered) |
| Add a subagent | `agents/<name>.md` (template: `agents/SUBAGENT_TEMPLATE.md`) |
| Routing / recall / comprehension | generic — lives in `psotobverse-utils`; this plugin ships `routing.yml` data + validating skills, not the engine |
| Safe-edit a live hook | `CLAUDE.md` → "Safe-edit protocol" |
| Self-guard allowlist | `.claude/policy/paths.allow.json` |
| Release | bump `.claude-plugin/plugin.json` + `CHANGELOG.md` |

## Lazy-loading
One row, one file. Do not preload `docs/` or `temporal-expansion-ideas/` wholesale.
