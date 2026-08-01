# E Start

**Script:** [E Start (script)](../E_Start.py) ·
**Flow:** [diagram](../__flow/E_Start.md)

## Purpose

The application entry point. Imports every project module, builds the root
`tb.Window`, applies the ttkbootstrap theme and derives `ThemeColors`,
configures global Treeview/Notebook styling and default fonts, decorates
every method of the app's 14 major classes with
[A2 Decorators](A2_Decorators.md)' `method_efficency`/`error_catcher`, then
hands off to `GUI.initialize(root)` ([D4 Window](D4_Window.md)) and enters
`root.mainloop()`.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) (`*`), [A2 Decorators](A2_Decorators.md)
  (`method_efficency`, `error_catcher`), [B1 Google Drive](B1_GoogleDrive.md),
  [B2 SQLite](B2_SQLite.md), [B3 Media](B3_Media.md) (`Media`,
  `Loading_Splash`), [B4 Graph](B4_Graph.md), [B5 AI](B5_AI.md),
  [C1 Controller](C1_Controller.md) (`Controller`, `GodMode`),
  [C2 Manage DB](C2_ManageDB.md), [C3 Select DB](C3_SelectDB.md),
  [D1 Top Panel](D1_TopPanel.md), [D2 Form Panel](D2_FormPanel.md),
  [D3 Main Panel](D3_MainPanel.md), [D4 Window](D4_Window.md).

### Used by
- None (entry point — run directly as `python E_Start.py`, or as the
  frozen `.exe` when `sys.frozen` is set by PyInstaller).

## Functions

### `start()`
See [flow](../__flow/E_Start.md) for the full boot sequence. In short:
builds and withdraws the root window, applies the theme and populates
`ThemeColors` from every `Colors.label_iter()` entry, configures
`TNotebook.Tab`/`Treeview`/`Treeview.Heading` styles and default fonts, then
`Classes_Decorating([...])` wraps every method of `GoogleDrive`, `Database`,
`Media`, `Graph`, `AI`, `Controller`, `GodMode`, `ManageDB`, `SelectDB`,
`TopPanel`, `FormPanel`, `MainPanel`, `GUI` with
`method_efficency()(error_catcher()(method))` via `inspect.getmembers` +
`setattr` — this is the mechanism that gives every one of those classes'
methods perf telemetry and audit-logged error visibility without each
method opting in individually. Finally calls `GUI.initialize(root)`, closes
the PyInstaller splash if frozen, and enters `root.mainloop()`.

### Module-level guard
`if __name__=='__main__':` — enables `multiprocessing.freeze_support()`
(required for a frozen/PyInstaller build that also uses
`multiprocessing.Process`, see [C2 Manage DB](C2_ManageDB.md)'s `Add_Image`),
records the "Loading Modules" startup-timing metric into
`UserSession['GUI']`, then calls `start()`.
