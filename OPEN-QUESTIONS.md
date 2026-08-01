# Open Questions — RHMH

Dilemmas the 2026-08-02 MD-First 2.0 documentation session could not
resolve alone (per its instructions: write them here rather than guess).
Each links back to the relevant finding in
[REWORK-BRIEF.md](REWORK-BRIEF.md).

## 1. Where does the actual database schema (DDL) live?

[B2 SQLite](__about/B2_SQLite.md) never issues a `CREATE TABLE` — the
schema is introspected at runtime via `PRAGMA table_info(...)`. The 10
tables and their columns documented in
[REWORK-BRIEF.md → Database Schema Summary](REWORK-BRIEF.md#db-schema)
are reconstructed from every query that names a column, across 5 files —
this is a best inference, not authoritative DDL (no types, constraints,
defaults, or explicit foreign keys are known). Is there a setup/migration
script, an old `.sql` file, or should the schema be dumped directly from
the live `RHMH.db`/`LOGS.db` (`sqlite3 RHMH.db .schema`)? This should be
the first thing the rework session does — it needs an authoritative schema
before it can safely alter anything.

## 2. Should the 5 inert `fixing_modules/` vendor copies be deleted?

`dialogs.py`, `scrolled.py`, `window.py`, `scaling_base_class.py`, and
`_ufuncs.py` are vendored third-party code (`ttkbootstrap`, `customtkinter`,
`torch`) that this session verified is **not imported by any file in the
project** — see
[REWORK-BRIEF.md → Vendored & Patched Third-Party Code](REWORK-BRIEF.md#vendored).
Two of them (`scaling_base_class.py`, `_ufuncs.py`) cannot even import
successfully from their current location (broken relative imports). This
session did not delete them (Guideline #3 — ask before deleting; also out
of a docs-only session's zero-behavior-change scope). Should they be
deleted now, or left for the rework session to remove alongside whatever
else it touches in that area?

## 3. Are the "unused" imports actually unused?

`B4_Graph.py` and `B5_AI.py` both `from B3_Media import Media` with no
call site found during this session's per-file review; `D4_Window.py`
imports `GoogleDrive` from `B1_GoogleDrive.py` with no reference found in
its body. This session reviewed each file in isolation and did not run a
whole-repo static-usage tool — a dedicated grep/AST pass across the full
project (including any dynamically-constructed attribute access this
session's manual review could have missed) would confirm before anyone
removes these imports.

## 4. Should `widgets.py`'s and `user.py`'s real patches be extracted now?

[REWORK-BRIEF.md → Vendored & Patched Third-Party Code](REWORK-BRIEF.md#vendored)
found that `fixing_modules/widgets.py`'s `Meter.amountmin` patch (6 lines)
and `fixing_modules/user.py`'s custom theme table are both currently
"live" only because they were manually copy-pasted into this development
machine's installed `ttkbootstrap` package — outside pip, outside any
lockfile, invisible to a fresh `pip install`. There is also no
`requirements.txt` in this repo today. Two related decisions for the
owner: (a) should a `requirements.txt`/lockfile be added now (pinning the
exact `ttkbootstrap` version the patch was written against), independent
of the rework, so a fresh install doesn't silently lose the patch? (b)
should the patch itself be reduced to a small subclass/monkeypatch module
instead of carrying the full vendored file forward — now, or deferred to
the rework alongside the god-file split?

## 5. Is `GodMode`'s hardcoded-password model intentional, or legacy?

[REWORK-BRIEF.md → Security Observations](REWORK-BRIEF.md#security) found
3 hardcoded plaintext passwords gating a raw-SQL execution console with no
audit-proof undo, and no role/user table anywhere in the reconstructed
schema. This is flagged as the highest-risk item in the codebase but was
NOT changed (zero-behavior-change, docs-only scope). Is this acceptable as
a stopgap until the rework, or does it need an interim fix (e.g.
disabling `FreeQuery_Execute` specifically) before the rework lands?
