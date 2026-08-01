# D1 Top Panel

**Script:** [D1 Top Panel (script)](../D1_TopPanel.py)

## Purpose

Builds the title bar: a resizable canvas showing the theme's title image
(and, for themes with an overlay label, a positioned text caption), plus the
"Connect" reconnect button shown when the app is offline.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *` (uses
  `TITLE_IMAGE`, `TITLE_HEIGHT`, `HEIGHT`, `ThemeColors`, `buttonX/Y`,
  `font_medium`).
- [B3 Media](B3_Media.md) — `from B3_Media import Media` (`Media.darken_color`
  for the button hover color).
- [C1 Controller](C1_Controller.md) — `from C1_Controller import Controller`
  (writes `Controller.Top_Frame`, `Controller.Reconnect_Button`,
  `Controller.Reconnect_window`; calls `Controller.lose_focus`,
  `Controller.starting_application`, reads `Controller.Connected`).

### Used by
- [D4 Window](D4_Window.md), [E Start](E_Start.md).

## Classes

### TopPanel
- Class attrs: `Top_Frame`, `title_image`, `txt_X`/`txt_Y`/`title_txt`.
- `initializeTP(root)`: resolves `TITLE_IMAGE` (a plain path, or a
  `(path, (text, x_frac, y_frac))` tuple depending on theme), builds the
  title `Canvas` (`Controller.Top_Frame`), binds `<Button-1>` to
  `Controller.lose_focus` and `<Configure>` to `adjust_title_window`, and
  builds the (initially placed, conditionally shown) "Connect" `CTkButton`
  wired to `Controller.starting_application`.
- `adjust_title_window(event)`: resizes the title image to the canvas's new
  width/height (LANCZOS), redraws it plus the optional title text; if
  `Controller.Connected` is `False`, also (re-)places the Reconnect button
  in the canvas via `create_window`.

## GUI layout

Single `Canvas` filling the title-bar row: full-bleed resized title image as
background, optional overlaid text label (theme-dependent position), and a
conditionally-visible "Connect" button anchored near the top-right when
offline.
