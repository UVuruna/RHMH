# D2 Form Panel

**Script:** [D2 Form Panel (script)](../D2_FormPanel.py)

## Purpose

Builds the patient data-entry form panel: two interchangeable forms
sharing one frame — "Default" (demographics/admission/diagnosis) and
"Alternative" (surgical staff + linked images) — swappable via a toggle
icon, with per-field validation wiring and the CRUD action-button row(s).

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media`.
- [C1 Controller](C1_Controller.md) — `from C1_Controller import
  Controller`.
- [C2 Manage DB](C2_ManageDB.md) — `from C2_ManageDB import ManageDB`
  (button command targets).
- [C3 Select DB](C3_SelectDB.md) — `from C3_SelectDB import SelectDB`.

### Used by
- [D4 Window](D4_Window.md), [E Start](E_Start.md).

## Classes

### FormPanel
All `@staticmethod`s; state lives on `Controller.*`, not on `FormPanel`
itself except a few class attrs (`Form_Frame`, `form_visible`,
`DefaultForm`, `AlternativeForm`, `valid_*` validator handles).
- `initializeFP(root)`: builds `Form_Frame`, constructs both sub-forms,
  measures/harmonizes their widths via `update_idletasks()`, shows Default
  by default.
- `Form_TopLabel(formname)`: title bar — swap icon (left), title label
  (center), hide icon (right).
- `Images_MiniTable_Create(frame)`: the embedded mini Treeview of a
  patient's images (inside the Alternative form's "Slike" field);
  double-click opens the full-screen viewer, selection fills the Opis
  field.
- `FormPatient_Create(parent, form_id)`: the main field-generation loop —
  reads `form_groups`/`form_entry`, resolves each field's backing table by
  membership test (`RHMH.pacijent`/`dg_kategorija`/`dr_funkcija`/`slike`),
  creates the widget per declared type (`Validate` Entry, `Combobox`,
  `StringVar` Entry, `Text`, `DateEntry`, `Info` label, `Slike` mini-table),
  wires per-field validators.
- `FormPatient_Buttons(parent, split, form_id)`: builds the action-button
  row(s) from `form_buttons`; the Default form gets only the first 3
  buttons, the Alternative form gets all 5 across two rows.
- `remove_form_frame(event)`: hides `Form_Frame`, flips `form_visible`.
- `swap_forms(event)`: toggles which of Default/Alternative is gridded.

## Config-like data (class attrs on FormPanel — candidates for centralizing
into [A1 Variables](A1_Variables.md))

- `form_buttons`: `(label, bootstyle)` → unbound `ManageDB` method
  reference (Add/Update/Delete Patient, Fill Form From Image, Clear Form).
- `form_groups`: per-form section boundaries.
- `form_entry`: the full field-definition table per form — label text,
  widget kind, width, and (for Combobox) allowed values. The largest and
  most important table in this file.

## GUI layout

`Form_Frame` (ridge border) → row 0: title bar (swap | title | hide); row 1:
`DefaultForm` and `AlternativeForm` overlaid in the same grid cell, only one
visible at a time. Each form: a 2-column `label | widget` grid with
group-header rows inserted at computed offsets, plus trailing button row(s).
The Alternative form embeds one Treeview (`Images_MiniTable_Create`,
`show='tree'`, no headers) mirroring the [SlikeTable](A1_Variables.md)
schema.
