# C2 Manage DB

**Script:** [C2 Manage DB (script)](../C2_ManageDB.py)

## Purpose

The write-path controller: Create/Update/Delete for patients, diagnoses,
operations/staff-assignments, images/media, MKB-10 catalog entries and
staff records, plus media import (file/video metadata) and OCR-assisted
auto-fill of the patient form from a scanned document, plus patient-form
field validation. Five largely independent responsibilities living in one
class — see Architecture notes and
[REWORK-BRIEF.md](../REWORK-BRIEF.md).

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B1 Google Drive](B1_GoogleDrive.md) — `from B1_GoogleDrive import
  GoogleDrive`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media`.
- [B5 AI](B5_AI.md) — `from B5_AI import AI`.
- [C1 Controller](C1_Controller.md) — subclasses `Controller`.
- [C3 Select DB](C3_SelectDB.md) — calls `SelectDB.refresh_tables`,
  `fill_PatientForm`, `Show_Image_FullScreen` directly (C2 → C3; C3 never
  imports C2).

### Used by
- [D2 Form Panel](D2_FormPanel.md), [D3 Main Panel](D3_MainPanel.md),
  [D4 Window](D4_Window.md), [E Start](E_Start.md).

## Classes

### ManageDB(Controller)
Grouped by feature (804 lines, 5 distinct responsibilities — see
Architecture notes):
- **Export/download**: `export_table(method)` (generic active-tab
  Treeview→Excel exporter), `Download_SelectedImages()` (threaded bulk
  Google Drive blob download with progress UI).
- **Create**: `Add_Patient()` (multi-table insert across
  `pacijent`/`dijagnoza`/`operacija`, resolving FK ids via extra SELECTs;
  computes age from birth/admission year), `Add_Image()` (file dialog for
  image/video, extracts size/dimensions/duration via Pillow/moviepy, inserts
  a placeholder row, uploads the BLOB to Drive, updates the row with the
  real name + Drive id — contains a `multiprocessing` guard inside
  `if __name__=='__main__':`, which is always `False` when imported, so the
  guarded `Process(...)` likely never actually spawns in production; flagged,
  not fixed), `Add_MKB()`, `Add_Zaposleni()` (simple catalog inserts + cache
  refresh).
- **Update**: `Update_Patient()` (diffs the form against the DB, per column,
  across `pacijent`/`dijagnoza`/`operacija`; multi-value fields use a
  set-difference to compute per-value INSERT/DELETE; confirm dialog shows
  the diff; relies on catching `UnboundLocalError` as the "no changes made"
  control-flow path — a No Error Masking (rules/CODE.md)-adjacent smell,
  flagged not fixed), `Edit_Image()` (description edit + filename patch),
  `Update_MKB()`, `Update_Zaposleni()` (near-duplicate diff-and-confirm
  bodies, parameterized only by table/column names — a No Duplicate Code
  (rules/CODE.md) candidate).
- **Delete**: `Delete_Patient()` (fetch-for-logging then delete, cascades
  via FK), `Delete_Image()` (DB delete then Drive-trash delete — asymmetric
  failure: the DB row is gone even if the Drive delete fails),
  `Delete_MKB()`, `Delete_Zaposleni()` (catch `sqlite3.IntegrityError` for
  still-referenced rows).
- **OCR/AI autofill**: `Image_Read(result_queue)` (polls a queue for parsed
  OCR data, fills matching form widgets, Retry/Ok confirm),
  `Fill_FromImage(firsttry)` (orchestrates: validates the image is an
  "Operaciona" type, downloads the blob, opens the AI reader settings
  dialog, spawns fullscreen-preview + OCR-reader threads — see
  [B5 AI](B5_AI.md)).
- **Validation**: `Validation_Method(event, form)` (resets/re-checks
  `Controller.Valid_Default`/`Valid_Alternative` flags, date-field checks),
  `validate_notblank`, `validate_godiste`, `validate_dijagnoza`,
  `validate_zaposleni`, `validate_zaposleni_Text` (Entry/Text
  `validatecommand` callbacks that mutate the shared `Controller.Valid_*`
  flags and, for the Text variant, directly repaint border colors).

## Database interactions

Tables touched: `pacijent`, `dijagnoza`, `operacija`, `mkb10`, `kategorija`,
`zaposleni`, `funkcija`, `slike` — all CRUD via `RHMH.execute_Insert/
execute_Update/execute_Delete/execute_selectquery/execute_select`. Every
multi-value diagnosis/operation entry triggers a separate FK-resolving
SELECT then a separate INSERT/DELETE (N+1 pattern) in `Add_Patient` and
`Update_Patient`. FK-lookup SELECTs use raw f-string SQL, same pattern
flagged in [B2 SQLite](B2_SQLite.md) and [C1 Controller](C1_Controller.md).
Every mutating method calls `Controller.LoggingData(...)` → an audit row in
LOGS `logs`. No GodMode/role checks here — write-blocking is purely the
offline-mode check via `@Controller.block_manageDB()`.

## Architecture notes

- God-class at the responsibility level: export utility, bulk media
  download, CRUD×4 entity types, OCR/AI autofill orchestration, and field
  validation are five separate domains in one class.
- `Add_MKB`/`Update_MKB`/`Delete_MKB` vs `Add_Zaposleni`/`Update_Zaposleni`/
  `Delete_Zaposleni` are near-identical bodies — a strong shared-base
  candidate.
- Business logic (diffing, FK resolution) is directly interleaved with GUI
  confirm/report dialogs — no separation of compute vs. persist vs.
  display.
