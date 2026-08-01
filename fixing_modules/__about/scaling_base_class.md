# scaling_base_class

**Script:** [scaling_base_class (script)](../scaling_base_class.py) ·
**Flow:** [diagram](../__flow/scaling_base_class.md)

## Purpose

A **byte-for-byte, unmodified vendored copy** of `customtkinter`'s internal
`CTkScalingBaseClass` (verified: zero-line diff against the currently
installed `customtkinter` package's
`windows/widgets/scaling/scaling_base_class.py`). Provides DPI/widget/
window scale-factor tracking and unit conversion (widget sizes, window
geometry strings, fonts, layout kwargs) for customtkinter widget/window
subclasses. Unlike `widgets.py`/`dialogs.py`/`user.py` (which carry real,
hand-verified patches or custom content — see
[REWORK-BRIEF.md](../../REWORK-BRIEF.md)), this file shows **no
modification at all** from upstream, and its own relative imports
(`from .scaling_tracker import ScalingTracker`, `from ..font import
CTkFont`) point at sibling modules that do not exist anywhere in this
project — so this file **cannot successfully import from its current
location**. It is very likely an accidental/orphaned copy rather than an
intentional patch backup. Flagged, not deleted, per this session's
zero-behavior-change scope (Guideline #3 — ask before deleting; see
[OPEN-QUESTIONS.md](../../OPEN-QUESTIONS.md)).

## Connections

### Uses
- `customtkinter`-internal relative imports only: `.scaling_tracker`
  (`ScalingTracker`), `..font` (`CTkFont`) — both unresolvable from this
  location. No project-internal imports.

### Used by
- None — confirmed zero references anywhere in the app.

## Classes

### CTkScalingBaseClass
Base class managing scaling state/callbacks for a widget or a window.
- `__init__(scaling_type)`: registers with `ScalingTracker` (widget or
  window mode), caches the initial scale factor, activates high-DPI
  awareness for window mode.
- `destroy()`: unregisters from `ScalingTracker`.
- `_set_scaling(new_widget_scaling, new_window_scaling)`: callback invoked
  on a global scale change; override point for subclasses.
- `_get_widget_scaling()` / `_get_window_scaling()`: accessors for the
  current scale factors.
- `_apply_widget_scaling(value)` / `_reverse_widget_scaling(value)`: scale a
  widget-space value up/down.
- `_apply_window_scaling(value)` / `_reverse_window_scaling(value)`: scale a
  window-space (geometry) value up/down.
- `_apply_font_scaling(font)`: scales a tuple-font or `CTkFont`'s point
  size.
- `_apply_argument_scaling(kwargs)`: scales `padx`/`pady`/`x`/`y` kwargs for
  layout calls.
- `_parse_geometry_string(geometry_string)` *(static)*: regex-parses a Tk
  `"WxH+X+Y"` geometry string into `(width, height, x, y)`, tolerating
  partial forms — see [flow](../__flow/scaling_base_class.md).
- `_apply_geometry_scaling(geometry_string)` /
  `_reverse_geometry_scaling(scaled_geometry_string)`: rebuild a
  scaled/unscaled geometry string from the parsed components.
