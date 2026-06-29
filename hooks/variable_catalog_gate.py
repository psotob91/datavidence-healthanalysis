#!/usr/bin/env python3
"""PreToolUse hook: variable-catalog status gate.

Advisory: emits permissionDecision ask (never deny) when a Write/Edit to a productive
script references a variable whose entry in the variable spec catalog has status: unknown
(an unresolved PENDING_CONFIRMATION variable). Opt-in: only acts when a catalog exists
(CLAUDE_PROJECT_DIR/metadata/variable_spec_catalog.yaml or .../variable-catalog.yaml).
Stdlib only (no PyYAML). FAIL-OPEN.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

_SCRIPT_RE = re.compile(r'(^|/)(analysis|R|scripts|src)/.*\.(r|qmd|py|sql)$', re.IGNORECASE)
_CATALOG_NAMES = ("variable_spec_catalog.yaml", "variable-catalog.yaml")
_VAR_RE = re.compile(r'^\s*-?\s*variable_id\s*:\s*["]?([A-Za-z0-9_.]+)')
_STATUS_RE = re.compile(r'^\s*status\s*:\s*["]?([A-Za-z_]+)')


def _unknown_vars(catalog_path):
    out, cur = set(), None
    try:
        for line in catalog_path.read_text(encoding="utf-8", errors="replace").splitlines():
            mv = _VAR_RE.search(line)
            if mv:
                cur = mv.group(1)
                continue
            ms = _STATUS_RE.search(line)
            if ms and cur:
                if ms.group(1).lower() == "unknown":
                    out.add(cur)
                cur = None  # each variable_id pairs with its first following status
    except Exception:
        pass
    return out


def _ask(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "ask",
        "permissionDecisionReason": reason}}))


def main():
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        return
    try:
        rd = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if not rd:
            return
        root = Path(rd)
        catalog = next((root / "metadata" / n for n in _CATALOG_NAMES
                        if (root / "metadata" / n).exists()), None)
        if catalog is None:
            return
        if event.get("tool_name", "") not in ("Write", "Edit", "MultiEdit"):
            return
        ti = event.get("tool_input", {}) or {}
        fp = str(ti.get("file_path") or ti.get("path", ""))
        if not fp or not _SCRIPT_RE.search(fp.replace("\\", "/")):
            return
        unknown = _unknown_vars(catalog)
        if not unknown:
            return
        content = ti.get("content", "") or ""
        if not content:
            try:
                content = Path(fp).read_text(encoding="utf-8", errors="replace") if Path(fp).exists() else ""
            except Exception:
                content = ""
        content = content + "\n" + str(ti.get("new_string", "") or "")
        hit = sorted(v for v in unknown if re.search(r'\b' + re.escape(v) + r'\b', content))
        if hit:
            _ask("[variable_catalog_gate] This script references variable(s) with status: "
                 "unknown in %s: %s. Resolve their status (confirm provenance/derivation) "
                 "before using them. Confirm to proceed anyway." % (catalog.name, ", ".join(hit)))
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
