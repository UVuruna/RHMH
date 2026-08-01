"""
Shared discovery helpers for the four guard tests.

The guards must agree on WHICH files they judge; keeping that decision in one
place is the reason this module exists (no duplicated walk logic in four
tests).
"""

from pathlib import Path

# ═══════════════════════════ PROJECT LAYOUT ═══════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directory NAMES no guard ever descends into, at any depth.
#   - caches: not ours
#   - UV: the owner's private inbox (root Rule #18)
#   - .claude: agent configuration, not project documentation
#   - Slike: image/GIF asset tree (no .py or .md content)
#   - temporary: gitignored scratch DB used during manual maintenance
EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".vscode",
        ".claude",
        "UV",
        "__pycache__",
        "htmlcov",
        "node_modules",
        "venv",
        ".venv",
        "Slike",
        "temporary",
    }
)

# Build/output trees, excluded by PATH so same-named source folders survive.
EXCLUDED_PREFIXES: tuple[str, ...] = ()

# Doc-folder names introduced by MD-First 2.0.
ABOUT_DIR = "__about"
FLOW_DIR = "__flow"


# ═══════════════════════════ FILE DISCOVERY ═══════════════════════════


def _walk(root: Path, suffix: str):
    """Yield every file under `root` with `suffix`, honouring both exclusions."""
    for path in sorted(root.rglob(f"*{suffix}")):
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if rel.as_posix().startswith(EXCLUDED_PREFIXES):
            continue
        yield path


def source_files() -> list[str]:
    """Every Python file the structure and docs laws apply to (excludes tests/)."""
    out = []
    for path in _walk(PROJECT_ROOT, ".py"):
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if rel.startswith("tests/"):
            continue
        out.append(rel)
    return out


def markdown_files() -> list[str]:
    """Every project `.md` file the docs law applies to."""
    return [p.relative_to(PROJECT_ROOT).as_posix() for p in _walk(PROJECT_ROOT, ".md")]


def line_count(rel_path: str) -> int:
    """Number of lines in a project-relative file."""
    with open(PROJECT_ROOT / rel_path, encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)
