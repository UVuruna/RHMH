# CLAUDE.md — RHMH

**Inherits ALL universal rules from the monorepo root
[CLAUDE.md](../../CLAUDE.md).** Read it first — it is the source of truth
for the mandatory workflow, MD-First documentation (`rules/DOCS.md`), the
priorities, model economy, the `UV/` owner-inbox, the version & commit
system, and every numbered rule. It also routes you to `rules/CODE.md` for
the Structure Law, the Config Section Law, and the guard-test/hook contract.
Nothing from those files is repeated here — only this project's facts and
laws stricter than the root.

**Visibility: Public.** Listed in the root `PROJECTS.md` and `README.md`
with a GitHub link — [UVuruna/RHMH](https://github.com/UVuruna/RHMH).

---

## Project Facts (never re-derive these)

- **What it is:** a LIVE medical patient-management desktop app for a
  reconstructive-surgery hospital department — patient records, medical
  imaging, the MKB-10 diagnosis catalog, staff data, operational analytics,
  AI-OCR for scanned surgery forms, and Google Drive backup/sync. This app
  is in real use — every session touches real patient data unless it is
  purely reading source code.
- **Stack:** Python, ttkbootstrap (Tkinter), customtkinter, SQLite, Google
  Drive API v3, PyTorch + EasyOCR (OCR), OpenCV, Matplotlib, Pandas.
- **Structure:** the app is a FLAT set of 17 letter-prefixed scripts at the
  project root — `A*` (config, decorators, splash), `B*` (services: Drive,
  SQLite, media, graph, AI), `C*` (controllers), `D*` (GUI panels),
  `E_Start.py` (entry point) — plus a `fixing_modules/` folder. It is **not**
  a Python package: no `__init__.py` anywhere, every file imports every
  other by bare module name (`from A1_Variables import *`,
  `from B2_SQLite import RHMH`, …), and the whole app runs from
  `python E_Start.py` with the project root on `sys.path`.
- **The single most important architectural fact**: `fixing_modules/` is
  **not** original RHMH code. It holds vendored (and in two cases,
  verified hand-patched) copies of third-party library internals
  (`ttkbootstrap`, `customtkinter`, `torch`) that the app does **not**
  import — the app imports the real, installed packages directly. Full
  finding: [REWORK-BRIEF.md](REWORK-BRIEF.md) → "Vendored & Patched
  Third-Party Code". Do not assume any file under `fixing_modules/` is live
  application logic without checking that finding first.
- **Status:** old codebase, zero pre-existing documentation, a BIG REWORK
  is planned by the owner. This documentation (MD-First 2.0 + the four
  guard tests) exists specifically so that future rework session can
  understand the app without re-reading 11,500 lines cold — start at
  [REWORK-BRIEF.md](REWORK-BRIEF.md).

---

## Project Laws (stricter than the root)

### This app is LIVE — read-only by default

Unless a session's explicit task is to CHANGE behavior, treat every module
as read-only. Never execute application logic, never open `RHMH.db`,
`LOGS.db`, or `GD_LOGS.db` for writing, never run `test.py` (a standalone
maintenance script that deletes all rows from `LOGS.db` at import time —
see [its doc](__about/test.md)), and never trigger a real Google Drive
sync from an agent session. Verification in a docs/refactor session means
`python -m py_compile` / `python -m compileall`, never a live app launch,
unless the owner explicitly asks for one.

### No god-file splits without the owner's go-ahead

`fixing_modules/dialogs.py`, `fixing_modules/widgets.py`,
`C3_SelectDB.py`, and `D3_MainPanel.py` all exceed the 1,000-line
Structure Law threshold and are ratcheted in
`tests/test_structure_law.py` under one owner-authorized reason: splitting
now would be redone/wasted once the REWORK redesigns these modules anyway.
Do not split them opportunistically — a session tasked with the REWORK
itself is the exception, and should re-read the RATCHET entries and
[REWORK-BRIEF.md](REWORK-BRIEF.md) first.

### Config Section Law scope

Only `A1_Variables.py` and `fixing_modules/user.py` are in
`test_config_sections.py`'s `CONFIG_FILES` — these are the two files whose
entire job is holding module-level declarative data. Several other files
(`B4_Graph.py`, `B5_AI.py`, `D2_FormPanel.py`, `D3_MainPanel.py`) hold real
config-like tables too, but nested inside class bodies or function scope,
outside what this guard's AST checks operate on — see
[REWORK-BRIEF.md](REWORK-BRIEF.md) → "Config Centralization" before adding
them to `CONFIG_FILES` casually.

---

## Enforcement in This Project

Four guard tests run from [tests (folder)](tests/___tests.md) via
`python tests/run_guards.py`, wired into `.claude/settings.json` as a
PostToolUse hook (`--fast`) and a Stop hook (all four). A red guard blocks
the session. RHMH has no application test suite of its own (see
[REWORK-BRIEF.md](REWORK-BRIEF.md) → Testing Baseline) — `run_guards.py` IS
the project's only automated safety net today.

---

## Where to Start Reading

[README](README.md) → the module docs under [__about](README.md#documentation)
and [fixing_modules (folder)](fixing_modules/___fixing_modules.md) → for
the synthesized cross-cutting picture, go straight to
[REWORK-BRIEF.md](REWORK-BRIEF.md) and [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md).

## Layout Teeth — pending migration (2026-08-06)

This project has a GUI and has NOT yet run the layout migration. Any GUI
work here follows [MIGRATE-LAYOUT.md](../../MIGRATE-LAYOUT.md) +
[GUI Rules](../../rules/GUI.md): the machine-wide layout guard already
bites in every session; what this project still owes is the per-project
audit — window registry, computed minimums fitting 1280x720, screenshots
opened and graded >= 8/10. Reference implementations: Remote User
(tests/test_layout_audit_qt.py) and DOMY Watch (tests/test_layout_audit.py).

GUI work here is also governed by the Zubi v2 Algorithmic Teeth & Grader v2
in [GUI Rules](../../rules/GUI.md#zubi-v2) — status: **pending rollout**
(no `layout_checks_qt.py` or equivalent installed teeth found in
`tests/` for this project).
