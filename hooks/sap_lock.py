#!/usr/bin/env python3
"""PreToolUse hook: pre-registration lock gate (no analysis before lock).

Advisory: emits permissionDecision ask (never deny) when a Write/Edit targets a
productive analysis/model script while the canonical pre-registration is NOT locked
(no validation/logs/sap_lock.json). Opt-in: only acts when the project adopted
pre-registration (CLAUDE_PROJECT_DIR/analysis/prereg/pre-registration.yaml exists).
Stdlib only. FAIL-OPEN.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

_SCRIPT_RE = re.compile(r'(^|/)(analysis|R|scripts|src)/.*\.(r|qmd|py|sql)$', re.IGNORECASE)
_PREREG_RE = re.compile(r'/prereg/', re.IGNORECASE)


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
        if not (root / "analysis" / "prereg" / "pre-registration.yaml").exists():
            return
        if (root / "validation" / "logs" / "sap_lock.json").exists():
            return
        if event.get("tool_name", "") not in ("Write", "Edit", "MultiEdit"):
            return
        ti = event.get("tool_input", {}) or {}
        fp = str(ti.get("file_path") or ti.get("path", ""))
        if not fp:
            return
        norm = fp.replace("\\", "/")
        if _PREREG_RE.search(norm):
            return
        if not _SCRIPT_RE.search(norm):
            return
        _ask("[sap_lock] The canonical pre-registration "
             "(analysis/prereg/pre-registration.yaml) is not locked (no "
             "validation/logs/sap_lock.json). Lock it (status: locked) via "
             "/datavidence-healthanalysis:preregister before writing analysis/model "
             "code, or record a deviation. Confirm to proceed anyway.")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
