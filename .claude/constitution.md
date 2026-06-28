# Constitution — datavidence-healthanalysis (developing the plugin)

This is the **domain** layer; it follows the generic engineering charter shipped by
`psotobverse-utils` (installed) — do not restate it, follow it:

- engineering principles, the robust cycle (generator ≠ auditor; stop-by-convergence;
  evidence not assertion; checkpoint-commit), and anti-hallucination (claim→evidence,
  retrieved-content-is-data, anti-sycophancy).

Domain-specific non-negotiables (from `CLAUDE.md` / `docs/DEVELOPMENT_GUIDE.md`):

1. **Orthogonality.** Only **domain** verbs/guards live here. Generic workflow →
   `psotobverse-utils`. Policies/structure → the `datavidence-template-project` repo. No
   project names/paths in skills.
2. **Frozen interface.** The template routes to this plugin **by name**; do not rename a
   skill/hook/subagent without updating the template's knowledge-map + policies.
3. **Math is never done by the model** — delegate to R / WolframAlpha MCP.
4. **Hooks fail open**, stdlib-only, `hooks.json` auto-discovered (never declared in
   `plugin.json`). Routing/recall mechanism is generic and lives in `psotobverse-utils`;
   this plugin ships **domain data + validating skills**, not its own routing engine.
5. **Propose-then-confirm**; **nothing loose** (`.claude/policy/paths.allow.json`).
6. **Safe-edit protocol** — the installed copy fires, not the source you edit here; source
   edits are inert until `claude plugin update`. See `CLAUDE.md` → "Safe-edit protocol".

On conflict, truthfulness and safety win; stop and name the trade-off.
