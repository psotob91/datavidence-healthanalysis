#!/usr/bin/env python3
"""PreToolUse hook: advisory egress guard for health-data projects.

Emits permissionDecision="ask" (never "deny") when a Write/Edit/Bash looks like it
could send identifiable patient data OUTSIDE the project. Opt-in: only acts when the
project looks like a health-data child (<CLAUDE_PROJECT_DIR>/.claude/policies/health/
or <CLAUDE_PROJECT_DIR>/metadata/ exists). Otherwise exits 0. Stdlib only. FAIL-OPEN.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

_PII_RE = re.compile(
    r'(?<![A-Za-z])(dni|hist(oria)?_?clinica|nombre|apellido|fecha_?nac(imiento)?'
    r'|direccion|telefono|e?mail|id_?paciente)(?![A-Za-z])', re.IGNORECASE)
_EGRESS_RE = re.compile(
    r'(aws\s+s3\s+cp|gsutil\s+cp|az\s+storage|curl\s+\S*\s*-[FTd]|wget\s+--post'
    r'|sendmail|mutt|mail\s+-s|rclone\s+copy|scp\s+|sftp\s+'
    r'|git\s+add\s+\S*(raw|data)[\/])', re.IGNORECASE)
_DATA_EXT = (".csv", ".xlsx", ".tsv", ".parquet", ".dta", ".sav", ".json")
_DATA_PATH_RE = re.compile(r'(raw|data)/', re.IGNORECASE)


def _refs_data(cmd: str) -> bool:
    """True if a Bash command references a data file (by extension) or a raw/ | data/
    path segment -- so the egress guard fires on file exports, not only when a PII
    field NAME literal happens to appear in the command string."""
    low = cmd.lower()
    return bool(_DATA_PATH_RE.search(low)) or any(ext in low for ext in _DATA_EXT)


def _ask(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "ask",
        "permissionDecisionReason": reason}}))


def _outside(path_str: str, root: Path) -> bool:
    """True if an ABSOLUTE path is outside the project root. Relative paths are
    treated as inside (they resolve under the project)."""
    try:
        p = Path(path_str)
        if not p.is_absolute():
            return False
        p.resolve().relative_to(root.resolve())
        return False
    except ValueError:
        return True
    except Exception:
        return False  # unknown -> do not nag


def main() -> None:
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
        if not ((root / ".claude" / "policies" / "health").is_dir() or (root / "metadata").is_dir()):
            return
        tool = event.get("tool_name", "")
        ti = event.get("tool_input", {}) or {}
        if tool in ("Write", "Edit", "MultiEdit"):
            fp = ti.get("file_path") or ti.get("path", "")
            content = ti.get("content", "") or ""
            if fp and _outside(str(fp), root):
                if (not content) or _PII_RE.search(content) or Path(fp).suffix.lower() in _DATA_EXT:
                    _ask("[guard_data_export] Target '%s' is OUTSIDE the project root. If it "
                         "carries identifiable patient data, confirm this egress is intended and "
                         "the data is de-identified/authorised." % fp)
        elif tool == "Bash":
            cmd = ti.get("command", "") or ""
            if _EGRESS_RE.search(cmd) and (_PII_RE.search(cmd) or _refs_data(cmd)):
                m = _PII_RE.search(cmd)
                what = ("references a PII field (%r)" % m.group()) if m else "moves a data file"
                _ask("[guard_data_export] This command %s together with a data-egress "
                     "operation. Confirm the data is de-identified/authorised before sending it out."
                     % what)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
