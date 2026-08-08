# B5 AI

**Script:** [B5 AI (script)](../B5_AI.py) ·
**Flow:** [diagram](../__flow/B5_AI.md)

## Purpose

The OCR pipeline: reads scanned "Operaciona Lista" (surgery record) forms
via EasyOCR, and rule-based-parses the raw OCR text to extract the operation
date, MKB-10 diagnosis codes, and doctor names by role — this is the engine
behind "Fill Form From Image" in [C2 Manage DB](C2_ManageDB.md). Also owns
the OCR settings dialog (reader type, zoom, VRAM/batch-size, which fields to
extract).

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media`; **no call site
  found** in this file during review — see OPEN-QUESTIONS.md.
- [C1 Controller](C1_Controller.md) — `Controller.DEFAULT['Reader']`,
  `Controller.toplevel_buttons`.

### Used by
- [C2 Manage DB](C2_ManageDB.md), [D4 Window](D4_Window.md),
  [E Start](E_Start.md).

## Classes

### AI
Static-only OCR pipeline. **The class body executes heavy work at import
time**: OS-conditional device selection (macOS → MPS else CPU; else CUDA
else CPU), sets the PyTorch global default tensor type/device, and
constructs `easyocr.Reader(['rs_latin','en'], gpu=...)` — the OCR model
loads unconditionally the moment this module is imported, not lazily. A
real startup-latency and testability concern for the rework (importing this
module for any reason, including to unit-test `mkb_fix`, pays the full
model-load cost and requires a working torch/easyocr install).
- `OperacionaChoice`: dict of `BooleanVar` widgets, one per extractable
  field.
- `Settings`: bootstrapped from `SETTINGS['Reader']` at import time (Zoom %
  → ratio, deep-copied `Entry` sub-dict) — same "requires restart to pick up
  a Settings.json change" gotcha as [B4 Graph](B4_Graph.md).
- `initialize()`: sets `Settings['Max VRAM']` via `get_gpu_vram()`.
- `get_gpu_vram()`: 3-tier fallback —
  `UserSession['PC']['GPU']['VRAM']` → `UserSession['PC']['RAM']` →
  hardcoded `4096` MB.
- `is_date(date_string)`: fuzzy `%d.%m.%Y` parser — strips spaces/dashes/
  underscores, trims trailing punctuation/non-digits, returns the
  reformatted string or `False` (documented sentinel, not an error mask).
- `mkb_find(detection, result, i)`: extracts an MKB code token from the
  current OCR line (4th whitespace-split token), or — on `IndexError` —
  from the next/previous line (validated by a nested
  `last_next_row_check`: under 6 chars AND more than 1 digit character);
  returns `(code, line_offset)`.
- `mkb_fix(mkb)`: normalizes OCR-misread MKB/ICD-10 codes — leading-digit →
  letter-prefix correction (5/8→S, 2→Z, 0→D, else X), `O`→`0`, `?`→`1`,
  strips stray `,`/`.`, reinserts a period before the last digit for 4-char
  codes.
- `ImageReader_SettingUp(PARENT)`: modal OCR settings dialog — reader-type
  combobox, Zoom meter (70–230%), VRAM/batch-size meter, one checkbox per
  extractable field; Run / Save-default / Restore-default.
  - nested `create_meter(...)` (near-duplicate of
    [B4 Graph](B4_Graph.md)'s own `create_meter`), `run_command()`,
    `savedefault_command()`, `restoredefault_command()`.
- `Operaciona_Reader(image)`: dispatches to line-mode or paragraph-mode
  `readtext()` (`mag_ratio=Zoom`, `batch_size=VRAM`) based on the chosen
  reader type; hands the result to the matching parser.
- `Operacion_ParagraphReader(result)`: **stub** — `print(result)` only,
  paragraph-mode parsing is unimplemented.
- `Operaciona_LineReader(result)`: the main parsing algorithm — see
  [flow](../__flow/B5_AI.md).
  - nested `extend_variable(i, variable, searchlist, image_text)`: greedily
    appends subsequent OCR lines to a field until a stop-prefix line is hit.

## AI/OCR pipeline summary

- **Library**: EasyOCR (`easyocr.Reader`) on PyTorch, Serbian-Latin +
  English (`['rs_latin','en']`). No OpenCV use in this file — `cv2` in
  [B3 Media](B3_Media.md) is for video thumbnails only, unrelated to OCR.
- **Preprocessing**: essentially none — only EasyOCR's own `mag_ratio`
  (Zoom, user-tunable 70–230%) and `batch_size` (labeled "VRAM" in the UI).
- **Inference**: `readtext(image, detail=0, mag_ratio=Zoom,
  batch_size=VRAM[, paragraph=True])` — Line mode (flat text list, fully
  implemented) or Paragraph mode (grouped; downstream parsing unimplemented).
- **Postprocessing**: entirely rule-based string matching tuned to one
  fixed hospital form layout (`DoctorsImage_dict`, defined inside
  `Operaciona_LineReader`, maps role-name prefixes — Operator/Asistent/
  Anesteziolog/Anestetičar/Instrumentarka/Gostujući Specijalizant — to
  extraction rules, including special-casing for "still in training"
  filtering and multi-name lines).
- No explicit model file management here — EasyOCR handles its own
  model download/cache.

## Architecture notes

- Import-time model load (see above) is the single biggest rework-relevant
  finding in this file.
- `Operaciona_LineReader` is one ~85-line method interleaving three
  concerns (date / MKB / doctors) in a single pass — a rework candidate to
  split per-field, especially since paragraph-mode needs equivalent logic
  built from scratch and should not join the same monolith.
- `DoctorsImage_dict`, the MKB-letter-fix table, and assorted magic
  thresholds are hardcoded domain knowledge about one physical form
  template — a form-layout change requires a code edit, not a config edit
  (No Hardcoded Values (rules/CODE.md) candidate for the rework).
