"""
THE DOCS LAW guard, part 1 — the navigation chain.

From `README.md` every project `.md` file must be reachable by following
links, and every relative `.md` link must resolve. A doc nobody can reach is a
doc nobody reads; a broken link is a lie about where information lives.
"""

import re
from urllib.parse import unquote
from pathlib import Path

from tests.guard_common import EXCLUDED_DIRS, PROJECT_ROOT, markdown_files

# ═══════════════════════════ LINK SYNTAX ═══════════════════════════

# [text](target)  — inline markdown links only; reference links are not used.
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

ROOT_DOC = "README.md"


# ═══════════════════════════ STATED EXCEPTIONS ═══════════════════════════

# `.md` files that are DATA or ONE-OFF TASK BRIEFS, not living documentation.
EXEMPT_FILES: frozenset[str] = frozenset()

EXEMPT_PREFIXES: tuple[str, ...] = ()

# Link targets that are never asserted to exist: the owner's gitignored `UV/`
# inbox (volatile by design, never tracked).
UNASSERTED_TARGET_PREFIXES = ("UV/",)


def _is_exempt(rel: str) -> bool:
    return rel in EXEMPT_FILES or rel.startswith(EXEMPT_PREFIXES)


def _targets(rel: str) -> list[tuple[str, str]]:
    """Return (raw_target, resolved_rel_or_empty) for each relative link."""
    text = (PROJECT_ROOT / rel).read_text(encoding="utf-8", errors="replace")
    here = Path(rel).parent
    out = []
    for raw in LINK.findall(text):
        # `<path with spaces.md>` is the markdown way to write a spaced target.
        raw = raw.strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1]
        target = unquote(raw.split("#", 1)[0]).strip()
        if not target:
            continue  # pure anchor, same document
        if "://" in target or target.startswith(("mailto:", "data:", "#", "/")):
            continue
        resolved = (here / target).as_posix()
        # Normalise ../ segments without touching the filesystem.
        parts: list[str] = []
        for part in resolved.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)
        out.append((target, "/".join(parts)))
    return out


# ═══════════════════════════ CHECKS ═══════════════════════════


def test_no_broken_relative_links():
    """Every relative link in every project `.md` resolves to a real file."""
    broken = []
    for rel in markdown_files():
        if _is_exempt(rel):
            continue
        for raw, resolved in _targets(rel):
            if resolved.startswith(UNASSERTED_TARGET_PREFIXES):
                continue
            if not (PROJECT_ROOT / resolved).exists():
                broken.append(f"{rel} -> {raw}")

    assert not broken, (
        f"THE DOCS LAW — {len(broken)} broken relative link(s):\n  "
        + "\n  ".join(broken)
    )


def test_every_doc_reachable_from_readme():
    """Walking links from README.md reaches every project `.md` file."""
    seen = {ROOT_DOC}
    queue = [ROOT_DOC]
    while queue:
        current = queue.pop()
        if not (PROJECT_ROOT / current).exists():
            continue
        for _raw, resolved in _targets(current):
            if not resolved.endswith(".md") or resolved in seen:
                continue
            if any(part in EXCLUDED_DIRS for part in Path(resolved).parts):
                continue
            seen.add(resolved)
            queue.append(resolved)

    orphans = sorted(
        rel for rel in markdown_files() if rel not in seen and not _is_exempt(rel)
    )
    assert not orphans, (
        f"THE DOCS LAW — {len(orphans)} doc(s) unreachable from {ROOT_DOC}. "
        "Link them from their folder doc (or add them to the stated exceptions "
        "with a reason):\n  " + "\n  ".join(orphans)
    )
