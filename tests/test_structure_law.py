"""
THE STRUCTURE LAW guard — no god-files.

Fails the build when any source file exceeds the violation threshold and is not
named in RATCHET. The allowlist may only SHRINK: adding an entry requires the
owner's explicit approval in the same session, and every entry states WHY the
file is still whole and which session owes the split.
"""

from tests.guard_common import line_count, source_files

# ═══════════════════════════ THRESHOLD ═══════════════════════════

VIOLATION_LINES = 1000
SMELL_LINES = 500


# ═══════════════════════════ RATCHET ALLOWLIST ═══════════════════════════

# file -> (why it is still whole, session that owes the split)
#
# Seeded 2026-08-02 by the MD-First 2.0 documentation session (RHMH has no
# tests to baseline; docs-only, zero behavior change). The owner's task brief
# pre-authorized these four exact entries with this exact reason: the app is
# LIVE and awaiting a full REWORK — splitting a file now, only to redesign it
# again during the rework, wastes the split's own effort. All four exceed the
# 1,000-line violation threshold; three were named directly by the owner, the
# fourth (D3_MainPanel.py) was found during Phase 0 inventory (the brief
# explicitly pre-authorizes "any other >1,000-line finds" under the same
# reason) — no "pending owner ratification" marker needed for these four.
RATCHET = {
    "fixing_modules/dialogs.py": (
        "awaiting the REWORK — splitting before it wastes the effort (owner "
        "note 2026-08-02). Also: this file is a near-verbatim vendored copy "
        "of the third-party ttkbootstrap library's own dialogs.py (Dialog, "
        "MessageDialog, QueryDialog, DatePickerDialog, FontDialog, "
        "Messagebox, Querybox) with zero project-specific coupling — see "
        "REWORK-BRIEF.md for the vendoring finding.",
        "god-file split session (post-REWORK)",
    ),
    "C3_SelectDB.py": (
        "awaiting the REWORK — splitting before it wastes the effort (owner "
        "note 2026-08-02).",
        "god-file split session (post-REWORK)",
    ),
    "fixing_modules/widgets.py": (
        "awaiting the REWORK — splitting before it wastes the effort (owner "
        "note 2026-08-02). Also: a near-verbatim vendored copy of "
        "ttkbootstrap's widgets.py (DateEntry, Floodgauge, Meter) carrying a "
        "6-line hand patch (`# dodato`) that adds a configurable minimum to "
        "Meter — see REWORK-BRIEF.md.",
        "god-file split session (post-REWORK)",
    ),
    "D3_MainPanel.py": (
        "awaiting the REWORK — splitting before it wastes the effort (owner "
        "note 2026-08-02). Found during Phase 0 inventory (1,045 lines) — "
        "not one of the three files the owner named by path, but covered by "
        "the same pre-authorized reason for any file over the threshold.",
        "god-file split session (post-REWORK)",
    ),
}


# ═══════════════════════════ THE GUARD ═══════════════════════════


def test_no_god_files():
    """No source file exceeds the violation threshold unless it is ratcheted."""
    violations = []
    for rel in source_files():
        lines = line_count(rel)
        if lines > VIOLATION_LINES and rel not in RATCHET:
            violations.append(f"{rel}: {lines} lines (> {VIOLATION_LINES})")

    assert not violations, (
        "THE STRUCTURE LAW — god-file(s) found. Split by responsibility "
        "(see REFACTOR-GODFILES.md), or add a RATCHET entry with the owner's "
        "explicit approval:\n  " + "\n  ".join(violations)
    )


def test_ratchet_only_shrinks():
    """Every ratcheted file must still exist and still be over the threshold."""
    stale = []
    for rel in RATCHET:
        try:
            lines = line_count(rel)
        except FileNotFoundError:
            stale.append(f"{rel}: file no longer exists — remove the RATCHET entry")
            continue
        if lines <= VIOLATION_LINES:
            stale.append(
                f"{rel}: now {lines} lines — split done, remove the RATCHET entry"
            )

    assert not stale, (
        "RATCHET entries are obsolete; the list may only shrink:\n  "
        + "\n  ".join(stale)
    )
