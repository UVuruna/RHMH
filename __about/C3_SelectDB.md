# C3 Select DB

**Script:** [C3 Select DB (script)](../C3_SelectDB.py) ·
**Flow:** [diagram](../__flow/C3_SelectDB.md)

## Purpose

The read-path controller and the single largest file in the project
(1,257 lines — a **god-file**, ratcheted in `tests/test_structure_law.py`,
awaiting the REWORK rather than a split now). One class, `SelectDB`, that
builds and refreshes all 6 data-tab Treeviews (Patients, Images, MKB
catalog, Staff catalog, Logs, Session), the entire dynamic search-bar UI +
query criteria gathering, patient/MKB/staff form-fill on selection, the full
Graph-tab configuration wizard, the image/video full-screen viewer, and
session-telemetry report rendering. At least four largely independent
domains live in this one class — see the responsibility table below and
[REWORK-BRIEF.md](../REWORK-BRIEF.md).

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B1 Google Drive](B1_GoogleDrive.md) — `from B1_GoogleDrive import
  GoogleDrive`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH,Database,LOGS`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media`.
- [B4 Graph](B4_Graph.md) — `from B4_Graph import Graph`.
- [C1 Controller](C1_Controller.md) — subclasses `Controller`.

### Used by
- [C2 Manage DB](C2_ManageDB.md) — calls `refresh_tables`,
  `fill_PatientForm`, `Show_Image_FullScreen` (C2 → C3; this direction
  only — C3 never imports C2, so any future split of C3 must preserve these
  three call sites).
- [D2 Form Panel](D2_FormPanel.md), [D3 Main Panel](D3_MainPanel.md),
  [D4 Window](D4_Window.md), [E Start](E_Start.md).

## Responsibility breakdown (the 1,257 lines, by feature)

| Lines (approx.) | Feature |
|---|---|
| ~11–120 | Generic Treeview plumbing shared by all 6 tabs — `empty_tables`, `refresh_tables` (re-runs the `Database.LastQuery` cache), `selectall_tables`, `shift_up`/`shift_down` |
| ~122–286 | Dynamic search bar (1–7 rows) — `search_bar_add/remove`, `selected_columns` (visibility + click-to-sort, type-aware comparators for dates and "12.3 MB"/"5 MP"-style strings), `search_options` (column-type-driven widget morphing), `search_options_swap` (rotates `=`/`LIKE`/`NOT LIKE`/`BETWEEN`/`GREATER`/`LESS`) |
| ~288–601 | **Graph-tab wizard** (~25% of the file) — `Show_Graph`, `graph_type_create`, `Configure_Graph`, `Show_Graph_execute` (embeds the matplotlib canvas), `graph_activating_X2`, `graph_remove_afterchoice`/`graph_activate_afterchoice`, and `graph_choice_analyze` — the cascading Y→X1→(X1-2/X1-3)→X2→(X2-2/X2-3)→plot-type combobox state machine; see [flow](../__flow/C3_SelectDB.md) |
| ~602–685 | Table fill/display — `fill_TablePacijenti`, `fill_Tables_Other`, `fill_TableSlike` (date/comma-list/MB-MP formatting), `showall_data` |
| ~686–812 | Search execution — `search_data` (walks active search-bar rows into a column→sign→values dict, dispatches to `execute_join_select`/`execute_select`), `filter_data` (a **second, separate** filter mechanism via `Controller.FilterOptions`) |
| ~813–906 | MKB / Staff / Patient form-fill — `fill_MKBForm`, `MKB_double_click`, `fill_ZaposleniForm`, `Zaposleni_double_click`, `fill_PatientForm` (core patient-load) |
| ~907–1046 | Logs & Session report viewer — `fill_LogsForm`, `fill_SessionForm`/`swapping_session_data` (unpickles the session telemetry BLOB, paginates), `methods_name_fix`, `highlight_numbers` (regex magnitude-threshold coloring), `Dict_To_String` (recursive nested-dict → indented text report) — a self-contained formatting engine unrelated to "selecting DB rows" |
| ~1048–1129 | Tab-switch handler — `tab_change`: per-tab hide/show of the two conditionally-visible tabs, search-bar column reconfiguration, Filter button toggling; the same hide-block is duplicated verbatim in 5 of 7 branches |
| ~1130–1257 | Image/video full-screen viewer — `Show_Image_FullScreen`, `Show_Image` (OS-aware modifier-key detection, Windows/macOS only), `Show_Image_execute` (background Drive fetch via queue-polling, zoom/pan or video-thumbnail click-to-play) |

Named features for the rework brief: (1) generic table utilities, (2) dynamic
multi-row search bar, (3) column sort/visibility, (4) patient selection +
detail form, (5) images table + full-screen viewer, (6) MKB-10 catalog
browser + quick-append, (7) staff catalog browser + quick-append, (8) logs
viewer, (9) session telemetry report viewer, (10) Graph configuration
wizard, (11) tab-switch orchestration, (12) a second/separate quick-filter
panel.

## Database interactions

Reads `pacijent` (via `execute_join_select` — joins across
`dijagnoza`/`operacija`/`mkb10`/`zaposleni`), `slike`, `mkb10`, `zaposleni`,
and — on the separate `Controller.GD_LOGS` database instance — `logs`,
`session`. `Database.LastQuery[db_name]` drives `refresh_tables`. Logs/
Session detail fetches use raw f-string SQL (same pattern flagged in
[B2 SQLite](B2_SQLite.md)/[C1 Controller](C1_Controller.md)).

## Architecture notes

- Textbook god-file: at least four largely independent domains (table/search
  plumbing, Graph wizard, image/video viewer, session-report text engine).
- The Graph wizard (~310 lines, ~25% of the file) is already self-segregated
  by `graph_*` naming and is the strongest standalone-module candidate.
- Heavy duplication: `showall_data`, `search_data`, `refresh_tables`,
  `empty_tables`, `selectall_tables` each repeat a near-identical 5-branch
  `if/elif TAB==...` chain — a single tab-config table
  (`{tab_name: {treeview, db_table(s), fill_method, columns}}`) driving one
  generic dispatcher would replace all five.
- Every method reads/writes `Controller.*` class attributes directly rather
  than receiving parameters — nothing here is unit-testable without a live
  GUI instance.
- `Show_Image` hardcodes Windows/macOS modifier-key bitmasks inline with no
  Linux branch.

See [REWORK-BRIEF.md](../REWORK-BRIEF.md) for the full cross-cutting
architectural discussion.
