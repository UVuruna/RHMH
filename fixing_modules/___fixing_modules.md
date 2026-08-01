# fixing_modules/

A folder of 7 files that, despite its name and its place in every prior
undocumented history of this project, turns out to hold **vendored copies
of third-party library internals** (ttkbootstrap, customtkinter, torch) —
**not** original RHMH application code, and **not imported by any other
file in this project**. This is the single largest architectural finding
from the 2026-08-02 documentation session; the full writeup is in
[REWORK-BRIEF.md](../REWORK-BRIEF.md) → "Vendored & Patched Third-Party
Code".

Two files carry a real, verified purpose: `widgets.py` and `user.py` are
hand-patched copies that the owner applies directly to the *installed*
`ttkbootstrap` package (this machine's `site-packages/ttkbootstrap/` was
found to already carry the identical patches), so the app's normal
`import ttkbootstrap as tb` picks them up. The other five files
(`dialogs.py`, `scrolled.py`, `window.py`, `scaling_base_class.py`,
`_ufuncs.py`) show no RHMH-specific modification and, in two cases
(`scaling_base_class.py`, `_ufuncs.py`), have relative imports that cannot
even resolve from this location — they read as accidental or abandoned
copies. None of this was fixed or deleted in this session (zero-behavior-
change, docs-only scope; deletions need the owner's decision — see
[OPEN-QUESTIONS.md](../OPEN-QUESTIONS.md)).

## Files

| File | Tier | One line |
|------|------|----------|
| `user.py` | Standard | patched copy of `ttkbootstrap/themes/user.py` — the app's 7 custom color themes — [about](__about/user.md) |
| `scaling_base_class.py` | Algorithmic | byte-identical copy of `customtkinter`'s DPI-scaling base class; unresolvable imports, unused — [about](__about/scaling_base_class.md) · [flow](__flow/scaling_base_class.md) |
| `_ufuncs.py` | Standard | copy of PyTorch's internal numpy-compat ufuncs; unrelated to a GUI app, unresolvable imports, unused — [about](__about/_ufuncs.md) |
| `scrolled.py` | Algorithmic | copy of `ttkbootstrap`'s `ScrolledText`/`ScrolledFrame`; the app imports the real ones instead — [about](__about/scrolled.md) · [flow](__flow/scrolled.md) |
| `window.py` | Standard | copy of `ttkbootstrap`'s `Window`/`Toplevel` wrapper; the app imports the real one instead — [about](__about/window.md) |
| `widgets.py` | Algorithmic — **god-file (ratcheted)** | patched copy of `ttkbootstrap`'s `DateEntry`/`Floodgauge`/`Meter` (the `Meter.amountmin` patch is real and live) — [about](__about/widgets.md) · [flow](__flow/widgets.md) |
| `dialogs.py` | Algorithmic — **god-file (ratcheted)** | copy of `ttkbootstrap`'s dialog library (`Messagebox`/`Querybox` and their backing classes) — [about](__about/dialogs.md) · [flow](__flow/dialogs.md) |

## Connections

### Uses
- Third-party packages only (`ttkbootstrap`, `customtkinter`, `torch`,
  `tkinter`, `PIL`) — no project-internal imports anywhere in this folder.

### Used by
- None of the 17 root-level project files import anything from
  `fixing_modules/` (verified by grep across the whole project). `user.py`
  and `widgets.py`'s content reaches the running app only indirectly,
  through a manually-patched copy of the installed `ttkbootstrap` package
  outside this repository's own import graph — see
  [REWORK-BRIEF.md](../REWORK-BRIEF.md).

## Design Decisions

This folder was **not** renamed, restructured, or pruned in the 2026-08-02
documentation session — the task was to document the codebase as it exists,
not to fix it, and the folder is heading into a full REWORK regardless
(the two oversized files are already ratcheted for that reason). The
finding that most of its contents are non-RHMH vendored code is recorded
here and in REWORK-BRIEF.md precisely so the rework session does not have
to re-discover it.
