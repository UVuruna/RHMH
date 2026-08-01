# D4 Window

**Script:** [D4 Window (script)](../D4_Window.py)

## Purpose

The application's top-level bootstrap: starts both databases, spawns
background init threads, builds the top/form/main panels in order, wires
every root-window binding (keyboard shortcuts, right-click menu, close
handler), and configures window chrome (title/icon). `GUI.initialize(root)`
is the single function [E Start](E_Start.md) calls to bring up the whole
UI.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [A2 Decorators](A2_Decorators.md) — `from A2_Decorators import
  spam_stopper,PC`.
- [B1 Google Drive](B1_GoogleDrive.md) — `from B1_GoogleDrive import
  GoogleDrive` — imported but **no reference found** in this file's body;
  see OPEN-QUESTIONS.md.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH,LOGS`.
- [B5 AI](B5_AI.md) — `from B5_AI import AI`.
- [C1 Controller](C1_Controller.md) — `from C1_Controller import
  Controller,GodMode`.
- [C2 Manage DB](C2_ManageDB.md) — `from C2_ManageDB import ManageDB`.
- [C3 Select DB](C3_SelectDB.md) — `from C3_SelectDB import SelectDB`.
- [D1 Top Panel](D1_TopPanel.md), [D2 Form Panel](D2_FormPanel.md),
  [D3 Main Panel](D3_MainPanel.md) — builds them in this order.

### Used by
- [E Start](E_Start.md) — `from D4_Window import GUI`, the last import and
  the class whose `initialize()` boots the whole GUI.

## Classes

### GUI
All `@staticmethod`s.
- `initialize(root)`: starts `LOGS`/`RHMH` databases, spawns 3 background
  threads (loading GIF, PC info gathering, `Controller.starting_application`),
  preloads MKB/Zaposleni validation lists via direct DB selects, calls
  `TopPanel.initializeTP` → `FormPanel.initializeFP` → `MainPanel.initializeMP`
  in order, centers the window, wraps every button with the spam-stopper,
  builds the right-click `Menu`, binds platform-specific shortcuts (macOS
  vs. Windows/Linux: right-click, Select-All, Save), binds Enter/Space,
  binds the secret GodMode key sequence, binds `WM_DELETE_WINDOW`, sets
  title/icon, configures root grid weights, deiconifies.
- `show_bind(event, showall)`: Enter/Space handler — routes to
  `SelectDB.showall_data()`/`search_data()` unless keyboard focus is inside
  a Text/Entry/DateEntry widget.
- `get_PC_info()`: background thread — gathers CPU/GPU/RAM/OS info into
  `UserSession['PC']`, then calls `AI.initialize()`.
- `Buttons_SpamStopper()`: wraps every button command registered in
  `Controller.Buttons` (including list-valued entries, skipping
  `Checkbutton`s) with `spam_stopper`.
- `EXIT()`: close handler — Save/Exit confirmation dialog; Save path
  uploads the RHMH DB + local logs to Drive and shows a warning on failure;
  Exit path uploads local logs then destroys the window.
- `show_form_frame()` / `show_title_frame()`: menu-driven visibility
  toggles for the form panel / title frame.
- `do_popup(event)`: shows/releases the right-click context `Menu`.
- `RootMenu_Create()`: builds the `Menu` — Show Title / Show Form
  checkbuttons; Export Selection / Export Table; Clear Form; Empty Table;
  Settings (jumps to tab 6) / About (tab 7); New User Authorization; Upload
  to Drive.

## Security note

The secret "GodMode" activation binding is a literal Unicode-escaped
string spelling `MUV13` bound directly as a Tk key-sequence — an obfuscated
but trivially decodable hardcoded credential. See
[REWORK-BRIEF.md](../REWORK-BRIEF.md) → Security Observations.

## Architecture notes

- Initialization order is implicit and thread-interleaved: DB start → 3
  background threads spawned (no visible join) → panel builders run
  synchronously on the main thread, some reading data those threads may
  still be populating (e.g. `UserSession['PC']`, written by `get_PC_info()`
  on a background thread) — a rework should verify there is no race between
  `MainPanel`/`FormPanel` reads and these threads' writes.
- Tight coupling to `Controller`/`FormPanel`/`MainPanel` module-level class
  attributes throughout, same shared-mutable-namespace pattern seen across
  the D-panels.
