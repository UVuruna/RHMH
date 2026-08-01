# C1 Controller

**Script:** [C1 Controller (script)](../C1_Controller.py)

## Purpose

Two classes: **`Controller`**, the base class holding essentially all
cross-cutting shared GUI state (roughly 60 class attributes referencing
every major widget/table/form-dict in the app) plus generic widget
get/set/clear helpers, the app's startup/connect flow, settings persistence,
and session/query audit logging; and **`GodMode`**, a hidden multi-tier
password-gated admin unlock that reveals the Logs/Session tabs and a raw-SQL
console. `Controller` is the shared parent every other controller
([C2 Manage DB](C2_ManageDB.md), [C3 Select DB](C3_SelectDB.md)) and every
GUI panel inherits from or reaches into directly.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B1 Google Drive](B1_GoogleDrive.md) — `from B1_GoogleDrive import
  GoogleDrive`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH,LOGS,Database`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media,Loading_Splash`.

### Used by
- [C2 Manage DB](C2_ManageDB.md), [C3 Select DB](C3_SelectDB.md) — both
  subclass `Controller`.
- [B4 Graph](B4_Graph.md), [B5 AI](B5_AI.md), [D1 Top Panel](D1_TopPanel.md),
  [D2 Form Panel](D2_FormPanel.md), [D3 Main Panel](D3_MainPanel.md),
  [D4 Window](D4_Window.md), [E Start](E_Start.md) — import `Controller`
  and/or `GodMode` directly.

## Classes

### GodMode
Hidden admin/superadmin unlock and log-maintenance tools, gated by
hardcoded passwords (flagged below — see Security note).
- `Admin_Unlocking(PARENT)`: password-entry `Toplevel` (Hint/Activate
  buttons), returns a result dict.
- `GodMode_Password(event)`: checks 3 hardcoded literal passwords; unlocks
  "Admin" (reveals the Logs/Session tabs) or "God Mode" (adds the Free
  Query console + Upload LOGS button).
- `ProgressBar_JoiningLogs(count)`: progress `Toplevel` (label, scrollable
  log Text, `Floodgauge`, gif splash).
- `JoiningLogs()`: downloads every user's remote per-user log database from
  Google Drive, merges their `logs`+`session` tables into the local
  `Controller.GD_LOGS` database, deletes the remote files, re-uploads the
  merged LOGS db (threaded).
- `upload_GD_LOGS()`: confirm dialog + threaded re-upload of the LOGS db.
- `FreeQuery_Execute()`: executes an **arbitrary, unparameterized raw SQL
  string** typed by the (GodMode-gated) user against RHMH or LOGS, after a
  yes/no confirm showing the formatted query. See Security note.
- `money()`: an easter-egg method computing a number from a hardcoded date —
  not app logic.

### Controller
Shared-state registry + core static utilities.
- Class-attribute groups (state, not methods): connection/session flags,
  per-tab Treeview references + column tuples, per-tab FormVariables dicts,
  search-bar state, patient-focus/validation state, Graph canvas/state, MKB/
  Zaposleni validation caches.
- `block_manageDB()`: decorator factory blocking any write action while the
  app is offline.
- `toplevel_buttons(frame, commands)`: reusable 3-button row (RESTORE/SAVE/
  RUN) shared by the [B4 Graph](B4_Graph.md) and [B5 AI](B5_AI.md) settings
  dialogs.
- `load_loading_GIF()`, `process_queue()`: threaded asset preloading + a
  thread→UI queue pump (`after(100, ...)` self-reschedule).
- `starting_application()`: connects to Google Drive, downloads `RHMH.db` +
  `Default.json`, version-checks against local Settings, shows connect/
  update messages.
- `create_new_user()`: re-runs Google OAuth, updates `Settings.json`.
- `update_settings()` / `restore_default_settings()`: persist/restore
  `Settings.json` from/to the Settings tab's form widgets.
- `Upload_RHMH()`: uploads `RHMH.db` to Google Drive.
- `Upload_local_LOGS()`: on logout — pickles most of `UserSession`'s
  sub-dicts, inserts one row into the LOGS `session` table, uploads it as a
  file, then clears+vacuums the local `logs`/`session` tables.
- `Clear_Form()`, `empty_widget()`, `get_widget_value()`,
  `set_widget_value()`: generic isinstance-dispatch widget helpers
  (Entry/Combobox/DateEntry/Text/Label/Treeview), including DB-date ↔
  display-date conversion and mini-table (4-column chunked) population.
- `LoggingData(result, query_type, loggingdata)`: writes every DB mutation
  to the LOGS `logs` table (threaded).
- `get_image_fromGD(GoogleID, queue)`: downloads a Drive blob, with optional
  cross-thread queue handoff.
- `lose_focus`, `is_DB_date`, `open_link`, `open_email`: small utilities.

## Security note (for REWORK-BRIEF.md)

`GodMode_Password` compares user input against 3 hardcoded plaintext
password strings by equality — there is no role table, no hashing, and
`FreeQuery_Execute` is a genuine raw-SQL execution console gated only by
that password, with no injection guard and no undo. This is the
single highest-risk item found across the whole codebase (see
[REWORK-BRIEF.md](../REWORK-BRIEF.md) → Security Observations). Documented
here as-is per this session's zero-behavior-change scope — not fixed.
