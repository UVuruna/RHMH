# window

**Script:** [window (script)](../window.py)

## Purpose

A vendored copy of `ttkbootstrap`'s own `window.py` — wraps `tkinter.Tk`/
`tkinter.Toplevel` as `Window`/`Toplevel` with a consolidated startup API
(theme, geometry, HDPI, icon, alpha, centering), plus module-level global
input-widget class bindings (cursor behavior, Ctrl-A select-all, Enter-to-
invoke). The file even retains ttkbootstrap's own demo block
(`if __name__=='__main__':`, using the stock `"superhero"` theme name — not
one of `user.py`'s custom `USER_THEMES` — confirming this demo was never
adapted for RHMH). Not imported anywhere in the app; the real `tb.Window`
the app instantiates comes from the installed `ttkbootstrap` package via
`import ttkbootstrap as tb` in
[A1 Variables](../../__about/A1_Variables.md). See
[REWORK-BRIEF.md](../../REWORK-BRIEF.md) → "Vendored & Patched Third-Party
Code".

## Connections

### Uses
- `tkinter`, `ttkbootstrap.constants`, `ttkbootstrap.publisher.Publisher`,
  `ttkbootstrap.style.Style`, `ttkbootstrap.icons.Icon`,
  `ttkbootstrap.utility` (all third-party). No project-internal imports.

### Used by
- None — confirmed zero references anywhere in the app.

## Classes

### Window(tkinter.Tk)
Top-level application window wrapper.
- `__init__(title, themename, iconphoto, size, position, minsize, maxsize,
  resizable, hdpi, scaling, transient, overrideredirect, alpha)`: enables
  HDPI awareness, sets the icon (default or user path, with print-and-
  fallback on error), applies title/geometry/min/max/resizable/transient/
  overrideredirect/alpha, calls `apply_class_bindings`/`apply_all_bindings`,
  builds `Style(themename)`.
- `style` (property): returns the `Style` instance.
- `place_window_center()` (alias `position_center`): centers on screen via
  `winfo_screenheight/width`.
- `revert_iconphoto()`: re-applies the stored icon.

### Toplevel(tkinter.Toplevel)
Secondary/child window wrapper.
- `__init__(title, iconphoto, size, position, minsize, maxsize, resizable,
  transient, overrideredirect, windowtype, topmost, toolwindow, alpha,
  windowposition, **kwargs)`: similar keyword wiring; adds `windowtype`
  (X11), `topmost`, `toolwindow` (win32), `iconify`; shares the singleton
  `Style()` rather than owning one.
- `style` (property): returns the shared `Style()` singleton.
- `place_window_center()` (alias `position_center`): centers relative to a
  stored `windowposition` (e.g. the parent's center) rather than the
  screen.

## Functions

- `get_default_root(what=None)`: returns/creates the default `tkinter.Tk`
  root; raises `RuntimeError` if default-root support is disabled or (with
  `what`) if called too early.
- `apply_class_bindings(window)`: binds class-level `<Configure>` (cursor
  fix) and `<Control-a>`/`<Control-A>` (select-all) on Entry/Spinbox/
  Combobox/Text classes; unbinds the default space-key toggle on `TButton`;
  binds Return/KP_Enter on `TButton` to invoke the focused button.
- `apply_all_bindings(window)`: binds `<Map>` globally to `on_map_child`;
  binds `<Destroy>` globally to unsubscribe the widget from `Publisher`.
- `on_disabled_readonly_state(event)`: sets the cursor to `'arrow'` when an
  entry-like widget is disabled/readonly, restores ibeam/default otherwise;
  swallows all exceptions (pre-existing upstream behavior, not RHMH-
  authored).
- `on_map_child(event)`: re-emits `<<MapChild>>` on a widget's parent when
  the widget is mapped (skips root; swallows exceptions for untracked
  widget types).
- `on_select_all(event)`: selects all text in a Text/Entry-like widget,
  returns `'break'`.
