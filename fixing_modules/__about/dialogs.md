# dialogs

**Script:** [dialogs (script)](../dialogs.py) ·
**Flow:** [diagram](../__flow/dialogs.md)

## Purpose

A near-verbatim vendored copy of `ttkbootstrap`'s own
`ttkbootstrap/dialogs/dialogs.py`. Provides generic, domain-agnostic Tkinter
dialog building blocks (message boxes, single-value input prompts, a
calendar date picker, a font chooser) plus the two static-method facade
classes ttkbootstrap exposes for app code to call: `Messagebox` and
`Querybox`. **Zero references to patients, images, MKB-10 diagnoses, staff,
logs, or sessions anywhere in the file.** 1,881 lines — the single largest
file in the project, and a **god-file**, ratcheted in
`tests/test_structure_law.py`, awaiting the REWORK rather than a split now.
Not imported anywhere in the app; the `Messagebox`/`Querybox` calls used
throughout [C1 Controller](../../__about/C1_Controller.md),
[C2 Manage DB](../../__about/C2_ManageDB.md) and others come from the
installed `ttkbootstrap` package via
[A1 Variables](../../__about/A1_Variables.md)'s
`from ttkbootstrap.dialogs.dialogs import Messagebox`. See
[REWORK-BRIEF.md](../../REWORK-BRIEF.md) → "Vendored & Patched Third-Party
Code".

## Connections

### Uses
- `calendar`, `textwrap`, `locale`, `datetime`, `tkinter.font`,
  `tkinter.BaseWidget`, `ttkbootstrap` (all third-party/stdlib). No
  project-internal imports.

### Used by
- None directly — confirmed zero references anywhere in the app.

## Classes

### Dialog(BaseWidget)
Base class implementing the template-method lifecycle shared by the file's
other modal dialogs.
- `__init__`: stores parent/title/alert flag.
- `_locate()`: positions the Toplevel relative to its parent.
- `show(position=None)`: builds, positions, `grab_set()`, `wait_window()` —
  the modal loop.
- `create_body(master)` / `create_buttonbox(master)`: both
  `raise NotImplementedError` — override hooks.
- `build()`: constructs the `ttk.Toplevel`, binds `<Escape>` to destroy,
  calls the two create_* hooks.
- `result` (property).

### MessageDialog(Dialog)
Generic modal message box with configurable message, icon and button set —
the backing implementation for every `Messagebox` static method.
- `__init__`, `create_body()` (icon + word-wrapped message),
  `create_buttonbox()` (right-to-left button row, Return/KP_Enter →
  default button), `on_button_press()` (records the result, invokes
  `command`, destroys), `show()`.

### QueryDialog(Dialog)
Generic single-`Entry` input dialog with optional datatype coercion and
min/max range validation — backs `Querybox.get_string/get_integer/get_float`.
- `create_body()`, `create_buttonbox()` (Submit/Cancel),
  `on_submit()` (reads, `validate()`, `apply()`), `on_cancel()`,
  `validate()` (int/float/complex coercion + min/max check, error via
  `Messagebox.ok` on failure), `apply()` (no-op override hook).

### DatePickerDialog
Standalone calendar popup — does **not** subclass `Dialog`, manages its own
Toplevel lifecycle directly. Backs `Querybox.get_date` — see
[flow](../__flow/dialogs.md) for the navigation state machine.
- `__init__` (locale setup, own Toplevel + `grab_set()`/`wait_window()`),
  `_setup_calendar()`, `_update_widget_bootstyle()`, `_draw_calendar()`
  (month grid of Radiobuttons), `_draw_titlebar()` (prev/next-month
  chevrons, right-click = prev/next-year, click title = reset),
  `_set_title()`, `_current_month_days()`, `_header_columns()` (localized
  weekday header honoring `firstweekday`), `_on_date_selected()`,
  `_selection_callback` (decorator redrawing the grid after navigation),
  `on_next_month`/`on_next_year`/`on_prev_month`/`on_prev_year`/
  `on_reset_date`, `_set_window_position()`, static
  `_nextmonth()`/`_prevmonth()`.

### FontDialog(Dialog)
Full font chooser (family, size, weight, slant, underline/overstrike, live
preview) — backs `Querybox.get_font`.
- `__init__` (seeds from `TkDefaultFont`, `trace_add` callbacks, enumerates
  `font.families()` excluding `@`-prefixed/emoji fonts), `create_body()`,
  `create_buttonbox()` (OK/Cancel), `_font_families_selector()` (scrollable
  Treeview), `_font_size_selector()` (scrollable Treeview, sizes
  `[8..12, 13,15,...,29, 36, 48, 72]`), `_font_options_selectors()`
  (weight/slant radiobuttons, effects checkbuttons), `_font_preview()`
  (Text-widget preview), `_on_select_font_family()`/`_on_select_font_size()`,
  `_on_submit()`/`_on_cancel()`, `_update_font_preview()` (rebuilds the
  `font.Font`, wrapped in a bare `except: pass` — pre-existing upstream
  behavior, not RHMH-authored).

### Messagebox
Static-method-only facade, no instance state.
- `show_info`, `show_warning`, `show_error`, `show_question` (returns
  result), `ok`, `okcancel` (returns result), `yesno` (returns result),
  `yesnocancel` (returns result), `retrycancel` (returns result).

### Querybox
Static-method-only facade.
- `get_color()` (lazily imports `ColorChooserDialog`), `get_date()` (wraps
  `DatePickerDialog`), `get_string()`/`get_integer()`/`get_float()` (wrap
  `QueryDialog`), `get_font()` (wraps `FontDialog`).

## Architecture notes

- Internally well-factored (inherited from upstream, not an RHMH
  contribution): `MessageDialog`/`QueryDialog` reuse `Dialog`'s template
  methods; `Messagebox`/`Querybox` are thin single-purpose facades.
- If/when this file is split, upstream's own module layout is the natural
  seam: `Dialog` (base) / `MessageDialog`+`QueryDialog` (template-method
  dialogs) / `DatePickerDialog` (self-contained) / `FontDialog`
  (self-contained) / `Messagebox` (facade) / `Querybox` (facade) — six
  files, zero regrouping analysis needed.
- No patient/medical validation logic anywhere — the only validation is
  `QueryDialog.validate()`'s generic numeric coercion/range check.
