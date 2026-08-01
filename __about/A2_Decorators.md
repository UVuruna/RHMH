# A2 Decorators

**Script:** [A2 Decorators (script)](../A2_Decorators.py)

## Purpose

Defines the three decorators applied, at startup, to **every method of every
major class in the app** (see `Classes_Decorating` in
[E Start](E_Start.md)), plus a small `PC` helper class that gathers
system/hardware info shown in the About tab and used to size the OCR batch.

This is the app's only error-visibility and perf-telemetry mechanism —
`error_catcher` is the reason an uncaught exception anywhere in a decorated
method still gets logged instead of crashing silently, and
`method_efficency` is the reason `UserSession` accumulates per-method timing
stats. Because decoration is applied automatically to every method of the
14 classes listed in `E_Start.start()`, individual `__about/` docs for those
classes do not repeat "wrapped in error_catcher/method_efficency" per method
— it is assumed unless a doc says otherwise (raw `threading.Thread` targets,
like the ones in `B3_Media.Loading_Splash`, are the one place this
protection does NOT reach, since a thread's `target=` callable is called
directly by the `threading` module, not through the decorated class
attribute).

## Connections

### Uses
- [A1 Variables (folder entry)](../__about/A1_Variables.md) — `from
  A1_Variables import *`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH,LOGS` (used by
  `error_catcher` to write the audit-log row).

### Used by
- [D4 Window](D4_Window.md) — imports `spam_stopper` and `PC` directly.
- [E Start](E_Start.md) — imports `method_efficency` and `error_catcher` and
  applies both to every method of every major class via `inspect.getmembers`
  + `setattr`.

## Functions

### `spam_stopper(button, root)`
Decorator factory. After the wrapped function runs, disables `button` and
re-enables it after `BUTTON_LOCK` ms via `root.after(...)` — the app-wide
double-click/spam guard. Applied to every registered button command in
`GUI.Buttons_SpamStopper()` ([D4 Window](D4_Window.md)), not via
`Classes_Decorating`.

### `method_efficency()`
Decorator factory. Times each call with both `perf_counter_ns` (wall clock)
and `process_time_ns` (CPU time), then accumulates count+total-time per
`Class.Method` into `UserSession[Class][Method]` under `'Processing Time'`
and `'Total Time'`. This is the source of the per-method performance stats
surfaced elsewhere in the app.

### `error_catcher()`
Decorator factory. Runs the wrapped function in a `try/except Exception`;
on failure, prints the exception + traceback to stdout, inserts a full
audit row (timestamp, user email, method qualname, the last SQL query
string, error message, full traceback) into the `LOGS.logs` table via
`LOGS.execute_Insert`, then **re-raises** — so the exception still
propagates to any enclosing `try/except`, it is just guaranteed to be logged
first (Rule #1's "errors MUST be visible" is satisfied here at the framework
level, not per call site).

## Classes

### PC
Static-only system-info gathering helper (no instances).
- `get_available_fonts()`: sorted list of installed font family names via
  matplotlib's `findSystemFonts`/`FontProperties` — powers the Font combobox
  in Settings.
- `get_cpu_info()`: processor name, physical/logical core counts, max
  frequency, via `cpuinfo`/`psutil` (noted in-code as ~1.5s, slow — always
  called from a background thread).
- `get_gpu_info()`: Windows path via `GPUtil`; macOS path shells out to
  `system_profiler SPDisplaysDataType` and regex-parses chipset/VRAM; no
  Linux branch.
- `get_ram_info()`: total RAM via `psutil.virtual_memory()`.
