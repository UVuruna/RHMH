# A3 Load Splash

**Script:** [A3 Load Splash (script)](../A3_LoadSplash.py) ·
**Flow:** [diagram](../__flow/A3_LoadSplash.md)

## Purpose

A standalone, self-runnable animated-GIF splash-screen widget
(`Loading_Splash`): preloads 32 numbered frames (`0.gif`…`31.gif`) from a
folder across 32 parallel threads, then cycles them on a Tk `after()` timer
to animate.

**This file is not imported anywhere in the active application** (verified:
no other project file references `A3_LoadSplash` or `LoadSplash`). It is an
earlier, decoupled version of the same idea now living, slightly evolved
(integrated with `App.get_window_center()` and `ThemeColors` instead of a
plain hex color), as the `Loading_Splash` class defined directly inside
[B3 Media](B3_Media.md) — which IS the class `E_Start.py` actually
imports and uses (`from B3_Media import Media,Loading_Splash`). The two
class bodies are otherwise near-identical. See REWORK-BRIEF.md → "Orphaned
& Duplicate Files" — this is flagged, not fixed, per this session's
zero-behavior-change scope; the file was kept and documented as-is, not
deleted (Guideline #3 — ask before deleting).

The file also carries its own `if __name__=='__main__':` demo block that
opens a themed root window and self-tests the splash against the
`Slike/gif_MUVS` frame set for 5 seconds — this is how it is actually
exercised, standalone, not from the app.

## Connections

### Uses
- Third-party only: `ttkbootstrap`, `tkinter`, `PIL`, `pathlib`, `itertools`,
  `threading`. No project-internal imports.

### Used by
- None (entry point / not yet wired — and, per the finding above, not
  expected to be; the app uses `B3_Media.Loading_Splash` instead).

## Classes

### Loading_Splash
Animated GIF splash/loading overlay.
- `__init__(folder, color='#ffffff', dimension=850, fps=12)`: spawns one raw
  `threading.Thread` per frame index (32 total) to preload `{i}.gif` from
  `folder`, resizing if `dimension != 850`; frames land in `self.images`
  under a lock.
- `load_image(i)`: loads and optionally resizes one frame, stores it as a
  `PhotoImage` under the lock.
- `create_splash(widget, alpha=1)`: builds a borderless, centered,
  color-keyed-transparent `Toplevel` (Windows) or reuses a given widget;
  starts the animation.
- `play()` / `stop()`: start/stop the `.after()`-driven animation loop;
  `stop()` cancels the pending callback and destroys the splash window.
- `_animate()`: advances to the next cached frame and reschedules itself.
