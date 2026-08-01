# widgets

**Script:** [widgets (script)](../widgets.py) ·
**Flow:** [diagram](../__flow/widgets.md)

## Purpose

A near-verbatim vendored copy of `ttkbootstrap`'s own `widgets.py` — the
file's own header comment names the exact `site-packages\ttkbootstrap`
source path it was copied from. Implements three composite widgets:
`DateEntry`, `Floodgauge`, and `Meter`. **This is the one file in
`fixing_modules/` proven to carry a genuine, currently-active hand patch**:
6 lines marked `# dodato` (Serbian "added") give `Meter` a configurable
minimum value (`amountmin`) instead of always starting at 0. Verified
byte-for-byte: those same 6 lines are present in the `Meter` class of this
machine's **installed** `site-packages/ttkbootstrap/widgets.py` — proving
the owner's real workflow is "edit the copy in `fixing_modules/`, then
hand-apply the same patch to the installed package" (the app imports
`tb.Meter` etc. from the installed `ttkbootstrap` normally, never from this
file). 1,175 lines — a **god-file**, ratcheted in
`tests/test_structure_law.py`, awaiting the REWORK rather than a split now.
See [REWORK-BRIEF.md](../../REWORK-BRIEF.md) → "Vendored & Patched
Third-Party Code" for the full finding.

## Connections

### Uses
- `tkinter`, `tkinter.ttk`, `tkinter.font`, `datetime`, `math`,
  `ttkbootstrap`, `PIL` (all third-party). No project-internal imports —
  this file is fully independent of `A1_Variables`/`A2_Decorators`/the rest
  of the app.

### Used by
- None directly — confirmed zero references anywhere in the app; the
  `Meter`/`Floodgauge`/`DateEntry` instances the GUI actually creates (e.g.
  the Settings-tab and OCR-settings `tb.Meter` gauges in
  [D3 Main Panel](../../__about/D3_MainPanel.md),
  [B4 Graph](../../__about/B4_Graph.md), [B5 AI](../../__about/B5_AI.md))
  come from the installed `ttkbootstrap` package — which, per the finding
  above, carries the same `amountmin` patch this file documents.

## Module-level data

- `M = 3` — meter image supersampling/resolution multiplier.
- `TTK_WIDGETS` (18 `ttk.*` classes) / `TK_WIDGETS` (17 `tk.*` classes) —
  widget-type registry tuples, unreferenced within this file itself
  (presumably consumed by a theming module elsewhere in the real
  `ttkbootstrap` package).

## Classes

### DateEntry(ttk.Frame)
`Entry` + `Button` combo that opens a `Querybox.get_date` calendar popup;
the chosen date is written back into the entry as formatted text.
- `__init__`: builds entry+button, seeds starting text.
- `__getitem__`/`__setitem__`: dict-style attribute access.
- `_configure_set`/`_configure_get`: custom handling of `state`,
  `dateformat`, `firstweekday`, `startdate`, `bootstyle`, `width`.
- `configure`: public get/set dispatcher.
- `_on_date_ask`: button callback — parses the current entry text as a
  date, opens the popup, writes the result back, focuses the entry.

### Floodgauge(ttk.Progressbar)
Progress bar with an overlaid text label (optionally a `mask` format
string, e.g. `"{}% Storage Used"`) drawn via low-level Tcl style calls.
- `__init__`: sets up `IntVar`/`StringVar` for value/text, binds
  theme-change events, applies the mask.
- `_set_widget_text`: pushes formatted text into the ttk style engine.
- `_set_mask`/`_unset_mask`: add/remove a variable trace that redraws text
  on value change.
- `_on_theme_change`: reapplies text after a theme switch.
- `_configure_get`/`_configure_set`: custom get/set for `value`, `text`,
  `bootstyle`, `mask`, `font`, `variable`, `textvariable`.
- `__getitem__`/`__setitem__`, `configure`: same dispatch pattern as
  `DateEntry`.
- `textvariable`/`variable` (properties): getter/setter pairs.

### Meter(ttk.Frame)
The largest, most complex class — a radial/dial gauge rendered as a
PIL-drawn arc image (supersampled via `M=3` then downscaled with
`Image.BICUBIC`), supporting full/semi-circle layout, solid/striped
indicator, and optional mouse-drag interactivity. See
[flow](../__flow/widgets.md) for the drawing pipeline.
- `__init__`: large parameter surface (bootstyle, `arcrange`/`arcoffset`,
  `amountmin`/`amounttotal`/`amountused` — `amountmin` is the local patch —,
  `metersize`, `meterthickness`, text/subtext options, `stepsize`); sets up
  `IntVar`s and geometry, calls `_setup_widget`.
- `_setup_widget`: builds the Frame/Label sub-widget tree (indicator image
  label, left/center/right text labels, subtext label), binds theme-change
  events.
- `_set_widget_colors`: resolves ttk style colors for foreground/
  background/trough.
- `_set_meter_text`/`_set_subtext`/`_set_show_text`/`_set_text_left`/
  `_set_text_center`/`_set_text_right`: layout/pack management for the text
  labels.
- `_set_interactive_bind`: binds/unbinds `<Button-1>`/`<B1-Motion>` for
  drag interaction.
- `_set_arc_offset_range`: computes arc degrees for full vs. semi meter
  type.
- `_draw_meter`: composites the value arc onto a copy of the base trough
  image and updates the indicator's `PhotoImage`.
- `_draw_base_image`: draws the static high-res trough/background arc.
- `_draw_solid_meter`/`_draw_striped_meter`: draw the colored indicator as
  a solid band or striped wedges.
- `_meter_value`: computes the arc-degree position from `amountused`
  relative to `amountmin`/`amounttotal` — carries the local `# dodato`
  min-aware formula.
- `_on_theme_change`: redraws on theme switch.
- `_on_dial_interact`: mouse-drag callback converting cursor angle to a
  clamped, stepped value — also carries `# dodato` clamping additions.
- `_lookup_style_option`: raw Tcl `ttk::style lookup` wrapper.
- `_configure_get`/`_configure_set`: large custom configure dispatch
  covering ~20 meter-specific attributes.
- `__getitem__`/`__setitem__`, `configure`: same dispatch pattern.
- `step`: increments/decrements `amountused` by `delta`, reversing
  direction at min/max (ping-pong style).

## Architecture notes

- The RHMH-specific delta is tiny: only the 6 `# dodato` lines (parameter,
  instance var, and two clamp branches) differ from upstream — a minimal
  "split" would extract just this patch into a small subclass (e.g.
  `class MeterWithMin(ttkbootstrap.Meter)`) instead of carrying the full
  ~650-line vendored `Meter` class forward.
- If/when this file is split, the three classes have zero interdependency
  and map directly to `date_entry.py` / `floodgauge.py` / `meter.py` — no
  regrouping analysis needed.
