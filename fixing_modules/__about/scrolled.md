# scrolled

**Script:** [scrolled (script)](../scrolled.py) ·
**Flow:** [diagram](../__flow/scrolled.md)

## Purpose

A vendored copy of `ttkbootstrap`'s own `scrolled.py` (its docstrings still
say `from ttkbootstrap.scrolled import ScrolledText` as the canonical import
path). Provides `ScrolledText` (a Text widget with optional autohiding
vertical/horizontal scrollbars) and `ScrolledFrame` (a content Frame inside
a fixed-size clipping container, with a vertical scrollbar and recursive
mouse-wheel binding). `A1_Variables.py` already imports these exact classes
straight from the installed `ttkbootstrap` package
(`from ttkbootstrap.scrolled import ScrolledFrame,ScrolledText`) — this
local copy shows no RHMH-specific modification and is not imported by the
app. See [REWORK-BRIEF.md](../../REWORK-BRIEF.md) → "Vendored & Patched
Third-Party Code".

## Connections

### Uses
- `ttkbootstrap`, `tkinter` (third-party only). No project-internal
  imports.

### Used by
- None — confirmed zero references anywhere in the app (the real
  `ScrolledFrame`/`ScrolledText` the app uses come directly from the
  installed `ttkbootstrap` package, imported in
  [A1 Variables](../../__about/A1_Variables.md)).

## Classes

### ScrolledText(ttk.Frame)
Text widget with optional autohiding v/h scrollbars.
- `__init__(...)`: builds the inner `ttk.Text`, delegates all Text methods
  onto self (except geometry managers), builds v/h `Scrollbar`s placed via
  `place()`, wires scroll commands, binds `<Configure>`.
- `_on_configure()`: repositions the horizontal scrollbar's relative width
  so it doesn't overlap the vertical one.
- `text` / `hbar` / `vbar` (properties): expose the inner Text widget and
  scrollbar instances.
- `hide_scrollbars()` / `show_scrollbars()`: lower/lift the scrollbars
  behind/above the text.
- `autohide_scrollbar()`: binds Enter/Leave to show/hide the scrollbars.

### ScrolledFrame(ttk.Frame)
Content Frame inside a fixed-size clipping container, with a vertical
scrollbar and mouse-wheel support — see [flow](../__flow/scrolled.md) for
the scroll-position math.
- `__init__(...)`: builds `self.container` (a `propagate(0)` clipping
  frame), places the content frame inside it, builds `vscroll`, delegates
  pack/grid/place calls to the container (renaming the content frame's own
  methods to `content_*`), binds Enter/Leave/Map events.
- `yview(*args)`: dispatches "moveto"/"scroll"/no-args (mimics the classic
  Tk scrollbar protocol).
- `yview_moveto(fraction)`: repositions the content via `place(rely=...)`,
  clamps the fraction, updates the scrollbar thumb.
- `yview_scroll(number, what)`: converts wheel/click "units" to a fraction
  delta, calls `yview_moveto`.
- `_add_scroll_binding(parent)` / `_del_scroll_binding(parent)`: recursively
  (un)bind mouse-wheel events on the frame and all descendants (X11
  Button-4/5 vs. win32/aqua MouseWheel).
- `enable_scrolling()` / `disable_scrolling()`: entry points for the
  recursive (un)binding above.
- `hide_scrollbars()` / `show_scrollbars()`: pack_forget/pack the
  scrollbar.
- `autohide_scrollbar()`: toggles the `autohide` flag.
- `_measures()`: computes `base` (inner/outer height ratio) and `thumb`
  (scrollbar thumb fraction).
- `_on_map_child(event)`: re-runs `yview()` when a child is mapped (updates
  the scroll range on new content).
- `_on_enter(event)` / `_on_leave(event)`: enable/disable scrolling,
  optionally show/hide scrollbars.
- `_on_configure(event)` / `_on_map(event)`: re-run `yview()`.
- `_on_mousewheel(event)`: platform-specific delta calculation (win32:
  `event.delta/120`; aqua: `event.delta`; X11: fixed ±10 via Button-4/5),
  calls `yview_scroll`.

## GUI layout

`ScrolledText` = Text widget (`side=LEFT, fill=BOTH, expand=YES`) with a
vertical scrollbar `place()`d at `relx=1.0` and an optional horizontal
scrollbar at `rely=1.0`. `ScrolledFrame` = a clipping container Frame with
the real content Frame `place()`d inside it, and a `Scrollbar` packed
`side=RIGHT, fill=Y`.
