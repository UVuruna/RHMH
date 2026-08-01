# A1 Variables

**Script:** [A1 Variables (script)](../A1_Variables.py) ·
**Flow:** [diagram](../__flow/A1_Variables.md)

## Purpose

The project's single central config module. Every other project file starts
with `from A1_Variables import *`, which is how the whole app shares one
namespace of constants, paths, fonts, colors and — most importantly — the
column/widget-definition tables that drive every Treeview and every dynamic
form in the GUI (`MainTablePacijenti`, `SlikeTable`, `MKBTable`,
`ZaposleniTable`, `LogsTable`, `SessionTable`). It also loads `Settings.json`
at import time, builds the `IMAGES` asset-path table, and declares the Google
Drive file IDs the app syncs against (`RHMH_dict`, `LOGS_dict`,
`GD_LOGS_dict`, `DEFAULT_dict`).

This file is also every other module's **third-party import hub** in
practice — because everything does `from A1_Variables import *`, the heavy
third-party imports declared here (ttkbootstrap, customtkinter, torch,
easyocr, matplotlib, PIL, Google API client, …) become implicitly available
everywhere without a direct import. This is a real architectural coupling
point, not just config — see [REWORK-BRIEF.md](../REWORK-BRIEF.md).

Section banners (comments only, added by the 2026-08-02 documentation
session; zero behavior change) now mark each region: startup timer, imports,
app window reference, project paths & image table, settings load, derived
display constants, fonts/colors/spacing, one banner per column-definition
table, search signs & misc UI tables, Google Drive file IDs, MIME types.

## Connections

### Uses
- Third-party only: ttkbootstrap, customtkinter, sqlite3, sqlparse, torch,
  psutil, GPUtil, cpuinfo, easyocr, pandas, numpy, matplotlib, PIL,
  pillow_heif, cv2, Google API client libraries.

### Used by
- Every other project module — [B1 Google Drive](B1_GoogleDrive.md),
  [B2 SQLite](B2_SQLite.md), [B3 Media](B3_Media.md), [B4 Graph](B4_Graph.md),
  [B5 AI](B5_AI.md), [C1 Controller](C1_Controller.md),
  [C2 Manage DB](C2_ManageDB.md), [C3 Select DB](C3_SelectDB.md),
  [D1 Top Panel](D1_TopPanel.md), [D2 Form Panel](D2_FormPanel.md),
  [D3 Main Panel](D3_MainPanel.md), [D4 Window](D4_Window.md),
  [A2 Decorators](A2_Decorators.md), [E Start](E_Start.md) — all via
  `from A1_Variables import *`.
- NOT used by `A3_LoadSplash.py` (self-contained, and itself unused — see
  REWORK-BRIEF.md), `test.py`, or anything in `fixing_modules/`.

## Classes

### App
Holds the single live reference to the app's root `tb.Window` (`App.ROOT`,
set elsewhere at startup) and one helper.
- `get_window_center()`: returns the screen `(x, y)` of the root window's
  center, used to position popups/dialogs relative to the main window.

## Module-level data (the real content of this file)

- **`IMAGES`** — nested dict of every static image/icon path the GUI uses:
  app icon, title-image variants per theme, swap/hide/add/remove/left/right
  button icon pairs (dark/light), password-hint image, MUVS logo, comparison
  ("Signs") icons, and the 7 theme-preview thumbnails.
- **`SETTINGS`** — the live contents of `Settings.json`, loaded once at
  import time (not reloaded on change without an app restart).
- **Derived display constants** — `Theme_Names`, `Title_Names`, `LANGUAGE`,
  `FONT`, `F_SIZE`, `BUTTON_LOCK`, `WAIT`, `WIDTH`, `HEIGHT`, `TITLE_HEIGHT`,
  `THEME`, `TITLE_IMAGE`, `UserSession` (the runtime telemetry dict every
  decorated method writes into — see [A2 Decorators](A2_Decorators.md)).
- **Fonts / colors / spacing** — `font_verybig/big/medium/default` lambdas,
  `color_labeltext`/`color_titletext`/`color_highlight` (theme-conditional),
  padding and width constants.
- **`MainTablePacijenti` / `SlikeTable` / `MKBTable` / `ZaposleniTable` /
  `LogsTable` / `SessionTable`** — one dict per data domain, each entry
  describing a database column's checkbox grouping, Treeview header text,
  column width and text anchor. These tables are the single source of truth
  every Treeview in [D3 Main Panel](D3_MainPanel.md) and
  [C3 Select DB](C3_SelectDB.md) binds to.
- **`SIGNS`**, **`Image_buttons`**, **`Katalog_Entry`**, **`Slike_Editor`** —
  smaller UI-config tables (search comparator names, image-tab button
  labels, the MKB-10/staff catalog entry-form layout).
- **Google Drive IDs** — `GD_SLIKE`, `GD_MAIN`, `GD_LOGS`, `RHMH_dict`,
  `LOGS_dict`, `GD_LOGS_dict`, `DEFAULT_dict` — the Drive file IDs and local
  paths [B1 Google Drive](B1_GoogleDrive.md) syncs against. These are Drive
  object identifiers, not credentials.
- **`MIME`**, **`GIF_SIZE`** — misc constants.
