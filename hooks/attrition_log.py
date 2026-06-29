#!/usr/bin/env python3
"""PostToolUse hook: informational attrition-logging check.

After writing/editing an analysis script that DROPS ROWS (filter/subset/where/...),
prints a non-blocking notice if the script does not also call log_attrition(...), so the
participant-flow (CONSORT/STROBE) counts accumulate from the start instead of being
reconstructed at the end. Opt-in: health children only (CLAUDE_PROJECT_DIR/.claude/
policies/health or CLAUDE_PROJECT_DIR/metadata exists). Stdlib only. FAIL-OPEN.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

_SCRIPT_EXT = (".r", ".qmd", ".py", ".sql")
_DROP_RE = re.compile(
    r'(\bfilter\s*\(|\bsubset\s*\(|\bdrop_na\s*\(|\bslice\s*\(|\banti_join\s*\('
    r'|\.query\s*\(|\.dropna\s*\(|\bna\.omit\s*\(|\bcomplete\.cases\s*\(|\bWHERE\b)')
_LOG_RE = re.compile(r'\blog_attrition\s*\(', re.IGNORECASE)


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
        if not ((root / ".claude" / "policies" / "health").is_dir() or (root / "metadata").is_dir()):
            return
        ti = event.get("tool_input", {}) or {}
        fp = str(ti.get("file_path") or ti.get("path", ""))
        if not fp or Path(fp).suffix.lower() not in _SCRIPT_EXT:
            return
        p = Path(fp)
        try:
            text = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        except Exception:
            text = ""
        text = text + "\n" + str(ti.get("content", "") or "") + "\n" + str(ti.get("new_string", "") or "")
        if _DROP_RE.search(text) and not _LOG_RE.search(text):
            print("[attrition_log] '%s' drops rows but does not call "
                  "log_attrition(step, n_in, n_out, excludes_target_population, reason). "
                  "Log each filter so the participant-flow counts accumulate from the start "
                  "(target -> accessible -> sampled -> study)." % p.name)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
