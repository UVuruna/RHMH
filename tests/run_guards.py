"""
Guard runner — the blocking half of the enforcement layer.

Runs the four guard tests and exits **2** on failure, which is what makes a
Claude Code hook BLOCKING. Kept fast and deterministic: guards only, never the
project's own test suite (RHMH has none — see REWORK-BRIEF.md).

Usage:
    python tests/run_guards.py            # all four guards (Stop hook)
    python tests/run_guards.py --fast     # structure + config only (PostToolUse)

As a PostToolUse hook it receives the hook payload as JSON on stdin and exits 0
immediately when the edited file is not a source file — a docs session must not
pay the guard cost on every one of hundreds of `.md` writes.
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FAST_GUARDS = ["tests/test_structure_law.py", "tests/test_config_sections.py"]
FULL_GUARDS = FAST_GUARDS + ["tests/test_docs_coverage.py", "tests/test_doc_links.py"]

# Suffixes whose edits can break the fast guards. Anything else short-circuits.
SOURCE_SUFFIXES = (".py",)

EXIT_BLOCK = 2


def _edited_path():
    """Read the Claude Code hook payload from stdin; None when there is none."""
    if sys.stdin is None or sys.stdin.closed or sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
    except OSError:
        return None
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    tool_input = payload.get("tool_input") or {}
    return tool_input.get("file_path") or tool_input.get("notebook_path")


def main() -> int:
    fast = "--fast" in sys.argv

    if fast:
        edited = _edited_path()
        if edited is not None and not edited.endswith(SOURCE_SUFFIXES):
            return 0  # docs edit — nothing the fast guards can judge

    os.chdir(PROJECT_ROOT)
    sys.path.insert(0, str(PROJECT_ROOT))

    import pytest

    targets = FAST_GUARDS if fast else FULL_GUARDS
    code = pytest.main(["-q", "--no-header", "-p", "no:cacheprovider", *targets])
    if code != 0:
        print(
            "\nGUARD FAILURE — a law of this monorepo is red. Fix it before "
            "finishing (rules/CODE.md, rules/DOCS.md).",
            file=sys.stderr,
        )
        return EXIT_BLOCK
    return 0


if __name__ == "__main__":
    sys.exit(main())
