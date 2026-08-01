# user

**Script:** [user (script)](../user.py)

## Purpose

Despite its name, this file defines **no user, role, permission, or
authentication logic**. It is a static table of 7 custom ttkbootstrap color
themes (`USER_THEMES`: Fruit, Flower, Night, Sea, Sunset, Moon, Sunrise —
the exact set the app's `Theme_Names` in
[A1 Variables](../../__about/A1_Variables.md) and the `Theme` field in
`Settings.json`/`Default.json` select from). It is a **patched copy** of the
installed `ttkbootstrap` package's own `ttkbootstrap/themes/user.py` — the
mechanism ttkbootstrap itself provides for registering custom themes
(`ttkbootstrap/style.py` does `from ttkbootstrap.themes.user import
USER_THEMES` and merges it into `STANDARD_THEMES`). Verified byte-for-byte:
this repo's copy and the file actually installed in this machine's
`site-packages/ttkbootstrap/themes/user.py` contain the identical 7 theme
definitions — confirming the owner's real workflow is to hand-edit this
file and then copy it into the installed package location so ttkbootstrap
picks it up at runtime. See
[REWORK-BRIEF.md](../../REWORK-BRIEF.md) → "Vendored & Patched Third-Party
Code" for the full finding, including the same pattern found in `widgets.py`
and `dialogs.py`.

If real RHMH user/role/authentication logic exists anywhere, its location is
still unknown as of this documentation session (`GodMode` in
[C1 Controller](../../__about/C1_Controller.md) is a hardcoded-password
admin unlock, not a user/role system) — see
[OPEN-QUESTIONS.md](../../OPEN-QUESTIONS.md).

## Connections

### Uses
- None — pure data, no imports.

### Used by
- No project file imports this module directly (confirmed: zero references
  to `fixing_modules.user` or bare `user` anywhere in the app). Its content
  reaches the running app only through the manually-patched copy at
  `site-packages/ttkbootstrap/themes/user.py`, outside this repository's
  import graph entirely.

## Module-level data

- **`USER_THEMES`** — dict of 7 theme names, each `{"type": "light"|"dark",
  "colors": {15 color keys: primary, secondary, success, info, warning,
  danger, light, dark, bg, fg, selectbg, selectfg, border, inputfg,
  inputbg, active}}`.
