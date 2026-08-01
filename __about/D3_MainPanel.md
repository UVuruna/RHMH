# D3 Main Panel

**Script:** [D3 Main Panel (script)](../D3_MainPanel.py) ·
**Flow:** [diagram](../__flow/D3_MainPanel.md)

## Purpose

Builds almost the entire right-hand side of the application: the search bar
and an 8-tab `Notebook` covering patient records, the image gallery, the
MKB-10/staff catalog, analytics/charting, logs, session history, settings
and about — i.e. the majority of the app's screen real estate besides the
title bar and the form panel. 1,045 lines — a **god-file**, ratcheted in
`tests/test_structure_law.py`, awaiting the REWORK rather than a split now.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH,LOGS`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media`.
- [B4 Graph](B4_Graph.md) — `from B4_Graph import Graph`.
- [C1 Controller](C1_Controller.md) — `from C1_Controller import
  Controller,GodMode`.
- [C2 Manage DB](C2_ManageDB.md) — `from C2_ManageDB import ManageDB`.
- [C3 Select DB](C3_SelectDB.md) — `from C3_SelectDB import SelectDB`.

### Used by
- [D4 Window](D4_Window.md), [E Start](E_Start.md).

## Responsibility breakdown (1,045 lines, by tab/section) — see [flow](../__flow/D3_MainPanel.md) for the zone diagram

| Lines (approx.) | Section |
|---|---|
| 1–96 | `initializeMP` — orchestration: right-panel frame, search bar, 8-tab Notebook wiring (Pacijenti, Slike, Katalog, Grafikon, Logs *hidden*, Session *hidden*, Settings, About) |
| 98–233 | Search-bar subsystem — per-column filter checkbuttons (`Roundbutton_Create`), the shared `filter_maintable_switch` (reused by the Graph tab too), static chrome (`SearchBar_StaticPart`), Add/Remove row icons, dynamic search-criteria row generator (`SearchBar_DynamicPart`) |
| 235–270 | Pacijenti (patient list) tab — column-visibility checkbuttons + Treeview bound to `MainTablePacijenti` |
| 272–322 | Shared column-visibility helper (`Checkbutton_Create`) — reused by both the Pacijenti tab and the Settings tab |
| 324–431 | Slike (images) tab — button bar, input row, Treeview bound to `SlikeTable`; right side: canvas image viewer (`Media.Slike_Viewer`) |
| 433–523 | Katalog tab — two side-by-side CRUD panels: MKB-10 (bound to `MKBTable`) and Zaposleni/staff (bound to `ZaposleniTable`); generic entry-form builder driven by the `Katalog_Entry` config dict |
| 525–560 | Shared "GodMode" free-query panel (`free_query_panel`) — DB selector + query Entry + Free Query button + Upload LOGS button; hidden by default, reused by both Logs and Session tabs — see Security note |
| 562–609 | Logs tab — Treeview bound to `LogsTable` + free-query panel + Full Query/Full Error text panels |
| 611–667 | Session tab — Treeview bound to `SessionTable` + free-query panel + paged PC-info report panel |
| 669–776 | Graph/Chart tab — Y-axis combobox, two expandable rows of X-axis comboboxes, bar/pie/stacked radio choice, embedded matplotlib canvas |
| 779–790 | Shared resize helper (`adapt_frame_size`) — used by the Settings tab's scroll area |
| 793–965 | Settings tab — Theme/Title image pickers, default-column picker, System settings (`tb.Meter` gauges), Restore/Save buttons |
| 967–1046 | About tab — static credits/description page, support email + GitHub link, MUVS logo |

## Config-like data (defined inline in this file — candidates for moving into
[A1 Variables](A1_Variables.md))

- `SYSTEM` (inside `SettingsTab_Create.System()`): numeric setting ranges
  `{name: (min, max, unit, step)}`.
- `Values` (same scope): Fonts/Language option lists.
- `TEXT` (inside `AboutTab_Create.Left_Panel()`): role → developer credits.

## GUI layout

`Window_Frame` → row 0: search bar (Add/Remove | "SEARCH BY" | N dynamic
rows | filter checkbuttons | SEARCH/SHOW ALL); row 9: the 8-tab `Notebook`
(see breakdown table above for each tab's zone tree). Every data tab pairs a
Treeview with the [A1 Variables](A1_Variables.md) column-definition table of
the same domain (Pacijenti↔`MainTablePacijenti`, Slike↔`SlikeTable`,
Katalog↔`MKBTable`/`ZaposleniTable`, Logs↔`LogsTable`,
Session↔`SessionTable`).

## Security note

The "GodMode" free-query panel (line ~525) executes arbitrary SQL against
RHMH/LOGS from a text `Entry`, gated only by hidden Notebook tabs and the
secret key sequence bound in [D4 Window](D4_Window.md) — see
[REWORK-BRIEF.md](../REWORK-BRIEF.md) → Security Observations.

## Architecture notes

- Confirmed god-file: 8+ unrelated tab-building responsibilities in one
  class (`MainPanel`, all `@staticmethod`s).
- Near-identical Treeview+scrollbar+bind boilerplate repeats across
  `PacijentiTab_Create`, `SlikeTab_Create`, `KatalogTab_Create`,
  `LogsTab_Create`, `SessionTab_Create` (Rule #5 candidate).
- Heavy reliance on `Controller` as shared global mutable state — nearly
  every builder writes into `Controller.Table_Names`, `Controller.Buttons`,
  `Controller.*_FormVariables`, etc. instead of returning structured
  objects.
- GUI/data-layer mixing: widget builders call `RHMH.get_distinct(...)`
  directly and reference `RHMH.*`/`LOGS.*` column lists as implicit schema
  oracles.
- `SlikeEditor_Create` is a dead/unimplemented stub (`pass`) — an abandoned
  planned feature.
