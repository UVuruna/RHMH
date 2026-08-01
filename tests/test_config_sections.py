"""
THE CONFIG SECTION LAW guard.

Config files and data tables are STRUCTURES, not notebooks. A table, class or
constant is written ONCE, complete, in the section that owns it. This guard
fails the build on the three machine-checkable defects:

1. a top-level definition that sits above every section banner
2. post-definition patching of an earlier module-level table
   (`TABLE["x"] = ...` / `TABLE.update(...)` at module level)
3. duplicate keys inside a dict literal
"""

import ast
import re

from tests.guard_common import PROJECT_ROOT

# ═══════════════════════════ FILES UNDER THE LAW ═══════════════════════════

# The two files whose entire job is holding declarative config/data tables at
# module level. Other RHMH files hold config-like tables too (e.g.
# B4_Graph.py's Y_options/X_options, D2_FormPanel.py's form_entry,
# D3_MainPanel.py's inline SYSTEM/Values dicts) but those tables live nested
# inside class bodies or function scopes, not at module level where this
# guard's banner/patch checks operate — see REWORK-BRIEF.md "Config
# Centralization" for the full list flagged for a future rework.
CONFIG_FILES = [
    "A1_Variables.py",
    "fixing_modules/user.py",
]

# Legacy post-definition patching that cannot be folded in without behaviour
# risk. Same rules as the structure ratchet: may only SHRINK, each entry needs
# the owner's approval. Empty is the goal state — and the current state.
PATCHING_RATCHET: dict[str, str] = {}


# ═══════════════════════════ BANNER SYNTAX ═══════════════════════════

# A banner is a comment whose text contains a run of at least 8 box-drawing or
# '=' characters plus the section name, e.g.
#   # ═══════════════════════════ POINTER SHAPES ═══════════════════════════
BANNER = re.compile(r"^\s*#.*[=═─━—-]{8,}")

# Statements that may legally precede the first banner.
PREAMBLE = (ast.Import, ast.ImportFrom, ast.Expr)


# ═══════════════════════════ CHECKS ═══════════════════════════


def _read(rel):
    return (PROJECT_ROOT / rel).read_text(encoding="utf-8")


def _banner_lines(source: str) -> list[int]:
    return [i + 1 for i, line in enumerate(source.splitlines()) if BANNER.match(line)]


def test_every_definition_sits_under_a_banner():
    """No top-level definition may appear above the first section banner."""
    problems = []
    for rel in CONFIG_FILES:
        source = _read(rel)
        banners = _banner_lines(source)
        first_banner = banners[0] if banners else None

        for node in ast.parse(source).body:
            if isinstance(node, PREAMBLE):
                continue
            if first_banner is None:
                problems.append(f"{rel}: no section banner in the file at all")
                break
            if node.lineno < first_banner:
                problems.append(
                    f"{rel}:{node.lineno}: definition above the first banner "
                    f"(line {first_banner}) — give it its own section"
                )

    assert not problems, "THE CONFIG SECTION LAW — unsectioned definitions:\n  " + (
        "\n  ".join(problems)
    )


def test_no_post_definition_patching():
    """A module-level table is never patched after it is defined."""
    problems = []
    for rel in CONFIG_FILES:
        source = _read(rel)
        tree = ast.parse(source)
        defined: set[str] = set()

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined.add(target.id)
                    elif isinstance(target, ast.Subscript):
                        base = target.value
                        if isinstance(base, ast.Name) and base.id in defined:
                            problems.append(
                                f"{rel}:{node.lineno}: `{base.id}[...] = ...` patches a "
                                f"table defined earlier — edit the structure in place"
                            )
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                defined.add(node.target.id)
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func = node.value.func
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "update"
                    and isinstance(func.value, ast.Name)
                    and func.value.id in defined
                ):
                    problems.append(
                        f"{rel}:{node.lineno}: `{func.value.id}.update(...)` at module "
                        f"level patches an earlier table — edit it in place"
                    )

    problems = [p for p in problems if p.split(":")[0] not in PATCHING_RATCHET]
    assert not problems, "THE CONFIG SECTION LAW — post-definition patching:\n  " + (
        "\n  ".join(problems)
    )


def test_no_duplicate_dict_keys():
    """A dict literal never repeats a key — the classic silent config bug."""
    problems = []
    for rel in CONFIG_FILES:
        for node in ast.walk(ast.parse(_read(rel))):
            if not isinstance(node, ast.Dict):
                continue
            seen = set()
            for key in node.keys:
                if not isinstance(key, ast.Constant):
                    continue
                if key.value in seen:
                    problems.append(
                        f"{rel}:{key.lineno}: duplicate dict key {key.value!r}"
                    )
                seen.add(key.value)

    assert not problems, "THE CONFIG SECTION LAW — duplicate keys:\n  " + (
        "\n  ".join(problems)
    )


def test_ratchet_only_shrinks():
    """Every PATCHING_RATCHET entry must name a file still under the law."""
    stale = [rel for rel in PATCHING_RATCHET if rel not in CONFIG_FILES]
    assert not stale, f"PATCHING_RATCHET names files outside CONFIG_FILES: {stale}"
