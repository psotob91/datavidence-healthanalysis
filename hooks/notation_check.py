#!/usr/bin/env python3
"""PostToolUse hook: informational notation-consistency check.

After writing/editing a methods document, scans LaTeX math tokens in the file and
prints a non-blocking notice listing any symbol/command NOT registered in the
child project's docs/analysis/notation.md.

Triggers on Write|Edit|MultiEdit; activates only for files matching
*methods* / *supplement*.qmd / analysis/*.qmd AND only when
<CLAUDE_PROJECT_DIR>/docs/analysis/notation.md exists. Otherwise exits 0.
Stdlib only. FAIL-OPEN (any error -> exit 0).
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

# LaTeX math tokens: inline $...$ OR a backslash-command \name
_MATH_TOKEN_RE = re.compile(r'\$[^$\n]{1,200}\$|\[a-zA-Z]+')

# A methods/supplement/analysis .qmd path (slash OR backslash separators)
_METHODS_RE = re.compile(r'(methods|supplement.*\.qmd$|analysis[\/][^\/]+\.qmd$)', re.IGNORECASE)


def _tokens(path: Path) -> set:
    try:
        return set(_MATH_TOKEN_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
    except Exception:
        return set()


def main() -> None:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        return
    try:
        root = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if not root:
            return
        notation = Path(root) / "docs" / "analysis" / "notation.md"
        if not notation.exists():
            return
        ti = event.get("tool_input", {}) or {}
        fp = ti.get("file_path") or ti.get("path", "")
        if not fp or not _METHODS_RE.search(str(fp)):
            return
        p = Path(fp)
        if not p.exists():
            return
        unregistered = sorted(_tokens(p) - _tokens(notation))
        if unregistered:
            shown = unregistered[:30]
            print("[notation_check] %d math token(s) in '%s' not in docs/analysis/notation.md: %s%s"
                  % (len(unregistered), p.name, ", ".join(shown),
                     " ..." if len(unregistered) > 30 else ""))
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
