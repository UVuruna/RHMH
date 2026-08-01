"""
THE DOCS LAW guard, part 2 — tier coverage.

Every source file carries the documentation its TIER requires
(spec: rules/DOCS.md):

| Tier        | Obligation                                    |
|-------------|-----------------------------------------------|
| Trivial     | one line in `___folder.md` only — no own docs |
| Standard    | `__about/{name}.md`                           |
| Algorithmic | `__about/{name}.md` + `__flow/{name}.md`      |
| tests/      | `___tests.md` folder doc only                 |

The tier lists below ARE the tier assignment. Moving a file between them is a
documentation change and belongs in the same commit as the docs it adds or
removes.

RHMH has no `__init__.py`/glue files at all (it is not a Python package — the
app is a flat set of letter-prefixed scripts run via `E_Start.py`), so the
TRIVIAL tier is empty here; every file carries real content.
"""

from tests.guard_common import ABOUT_DIR, FLOW_DIR, PROJECT_ROOT, source_files

# ═══════════════════════════ TIER — TRIVIAL ═══════════════════════════

TRIVIAL: frozenset[str] = frozenset()


# ═══════════════════════════ TIER — ALGORITHMIC ═══════════════════════════

# Real algorithms, nontrivial GUI/animation flows, and config/data structures
# whose shape needs a picture: about + flow.
ALGORITHMIC = frozenset({
    # root — config, startup and algorithmic controllers/services
    "A1_Variables.py",
    "A3_LoadSplash.py",
    "B2_SQLite.py",
    "B4_Graph.py",
    "B5_AI.py",
    "C3_SelectDB.py",
    "D3_MainPanel.py",
    "E_Start.py",
    # fixing_modules — vendored library code with genuine multi-step logic
    "fixing_modules/scaling_base_class.py",
    "fixing_modules/scrolled.py",
    "fixing_modules/widgets.py",
    "fixing_modules/dialogs.py",
})

# Everything not listed above is Standard tier: `__about/{name}.md` only.

# ═══════════════════════════ TIER — TESTS ═══════════════════════════

TESTS_PREFIX = "tests/"


# ═══════════════════════════ THE GUARD ═══════════════════════════


def _doc_path(rel: str, doc_dir: str) -> str:
    """`fixing_modules/x.py` -> `fixing_modules/{doc_dir}/x.md`; `x.py` -> `{doc_dir}/x.md`."""
    folder, _, name = rel.rpartition("/")
    return f"{folder}/{doc_dir}/{name[:-3]}.md" if folder else f"{doc_dir}/{name[:-3]}.md"


def _code_folders() -> set[str]:
    """Every folder that holds at least one non-test source file."""
    return {rel.rpartition("/")[0] for rel in source_files() if "/" in rel}


def test_no_file_has_two_tiers():
    """A file is Trivial OR Algorithmic OR (by omission) Standard — never two."""
    both = sorted(TRIVIAL & ALGORITHMIC)
    assert not both, (
        "these files are listed in both tier lists; a file has exactly one "
        "tier:\n  " + "\n  ".join(both)
    )


def test_stale_tier_entries():
    """Tier lists never name a file that no longer exists."""
    stale = sorted(
        rel for rel in (TRIVIAL | ALGORITHMIC) if not (PROJECT_ROOT / rel).exists()
    )
    assert not stale, (
        "tier lists name files that no longer exist — update them in the same "
        "commit as the move/delete:\n  " + "\n  ".join(stale)
    )


def test_about_doc_per_source_file():
    """Standard and Algorithmic files have their `__about/` doc."""
    missing = []
    for rel in source_files():
        if rel in TRIVIAL or rel.startswith(TESTS_PREFIX):
            continue
        doc = _doc_path(rel, ABOUT_DIR)
        if not (PROJECT_ROOT / doc).exists():
            missing.append(f"{rel} -> {doc}")

    assert not missing, (
        f"THE DOCS LAW — {len(missing)} missing `__about/` doc(s):\n  "
        + "\n  ".join(missing)
    )


def test_flow_doc_per_algorithmic_file():
    """Algorithmic files also have their `__flow/` doc."""
    missing = []
    for rel in sorted(ALGORITHMIC):
        doc = _doc_path(rel, FLOW_DIR)
        if not (PROJECT_ROOT / doc).exists():
            missing.append(f"{rel} -> {doc}")

    assert not missing, (
        f"THE DOCS LAW — {len(missing)} missing `__flow/` doc(s):\n  "
        + "\n  ".join(missing)
    )


def test_no_flow_doc_for_non_algorithmic_files():
    """Tier discipline both ways: no `__flow/` doc for glue or plain modules."""
    extra = []
    for rel in source_files():
        if rel in ALGORITHMIC or rel.startswith(TESTS_PREFIX):
            continue
        doc = _doc_path(rel, FLOW_DIR)
        if (PROJECT_ROOT / doc).exists():
            extra.append(f"{doc} (for {rel}, tier is not Algorithmic)")

    assert not extra, (
        "THE DOCS LAW — `__flow/` docs written for non-Algorithmic files; "
        "delete them or raise the file's tier:\n  " + "\n  ".join(extra)
    )


def test_no_docs_for_trivial_files():
    """Trivial files are documented by one line in `___folder.md`, nothing more."""
    extra = []
    for rel in sorted(TRIVIAL):
        for doc_dir in (ABOUT_DIR, FLOW_DIR):
            doc = _doc_path(rel, doc_dir)
            if (PROJECT_ROOT / doc).exists():
                extra.append(f"{doc} (for Trivial file {rel})")

    assert not extra, (
        "THE DOCS LAW — docs written for Trivial-tier files; delete them or "
        "raise the file's tier:\n  " + "\n  ".join(extra)
    )


def test_folder_doc_per_code_folder():
    """Every code folder has its `___folder.md` entry point."""
    missing = []
    for folder in sorted(_code_folders()):
        name = folder.rpartition("/")[2]
        doc = f"{folder}/___{name}.md"
        if not (PROJECT_ROOT / doc).exists():
            missing.append(doc)

    assert not missing, (
        f"THE DOCS LAW — {len(missing)} folder(s) without `___folder.md`:\n  "
        + "\n  ".join(missing)
    )
