# B4 Graph

**Script:** [B4 Graph (script)](../B4_Graph.py) ·
**Flow:** [diagram](../__flow/B4_Graph.md)

## Purpose

The analytics/chart layer: matplotlib chart drawing (bar / pie / grouped /
stacked) for the Graph tab, its own dynamic SQL query builder that turns a
UI axis-grouping choice (year/month/weekday/day, trauma/gender, MKB
category, staff role, age bracket) into one aggregate SQL query, and a
chart-margin/legend settings dialog. Three responsibilities in one class —
see Architecture notes.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.
- [B2 SQLite](B2_SQLite.md) — `from B2_SQLite import RHMH`.
- [B3 Media](B3_Media.md) — `from B3_Media import Media`; **no call site
  found** in this file during review — see OPEN-QUESTIONS.md.
- [C1 Controller](C1_Controller.md) — `Controller.DEFAULT['Graph']`,
  `Controller.toplevel_buttons`.

### Used by
- [C3 Select DB](C3_SelectDB.md), [D3 Main Panel](D3_MainPanel.md),
  [E Start](E_Start.md).

## Classes

### Graph
Static-only chart builder + query builder + settings dialog.
- `Settings` (class attr): bootstrapped from `SETTINGS['Graph']` (margin %
  → ratio conversion). Materialized once at **import time** — a
  `Settings.json` change requires a restart to take effect.
- `Checkbuttons`, `figure`/`plot`/`legend` (class attrs): singleton chart
  state — only one chart can exist app-wide at a time.
- `DateTypes`: label → strftime-code map (Year/Month/Weekday/Day).
- `Y_options`: Y-metric label → (SQL expression or `1`, date column) —
  e.g. hospitalization-days via a `julianday` date difference.
- `X_options`: X-axis label → `''` or an explicit `[labels, SQL condition]`
  pair (Trauma/Pol binary groupings).
- `SQL_date_num`: weekday-number→name and month-number→name lookup tables
  (Serbian).
- `initialize(width, height, X, Y, title, X_label, Y_label, X2=None)`:
  stashes chart data into class attrs before drawing.
- `create_figure_plot()`: builds a themed Figure+Axes (colors from
  `ThemeColors`, custom font, rotated x-tick labels).
- `save_and_open_graph_figure(event)`: saves the current figure to a fixed
  temp PNG, opens it with the OS default viewer.
- `create_1D_bar(colors=0, values=0)`: single-series bar chart, optional
  viridis coloring and value labels.
- `create_1D_pie()`: pie chart, viridis coloring, % autotext.
- `create_2D_bar(values=0, width=0.1)`: clustered/grouped bar chart.
- `create_2D_stackedbar(values=1, width=0.6)`: stacked bar variant.
- `Graph_DistinctMKB(mkb=None, IDS=None)`: wraps
  `RHMH.get_distinct_mkb`, converts to LIKE-condition strings.
- `Graph_DistinctZaposleni(funkcija=None, IDS=None)`: wraps
  `RHMH.get_distinct_zaposleni`, converts to equality-condition strings.
- `Graph_DistinctDate(datetype, column, IDS=None)`: wraps
  `RHMH.get_distinct_date`, converts to `strftime(...)="..."` conditions.
- `Graph_StarostGroups(jump)`: generates fixed-step age-bracket `BETWEEN`
  conditions from 0 to 80 plus an open-ended 80+ bracket.
- `Graph_makeQuery(Y, X1, X2, Filter)`: the core query builder — see
  [flow](../__flow/B4_Graph.md).
  - nested `get_Xgroups(X, datewhere)`: per-X-type dispatcher (MKB
    category/individual, staff/role, age, Trauma/Pol binary, generic date
    bucket) → `(select-conditions, extra-where, join-table-name)`.
- `Graph_SettingUp(PARENT)`: modal chart-margin/legend/label settings
  dialog (4 `tb.Meter` margin gauges + 4 checkbuttons); Run / Save-default /
  Restore-default persist to `Settings.json`.
  - nested `create_meter(...)`, `run_command()`, `savedefault_command()`,
    `restoredefault_command()`.

## Architecture notes

- **Third occurrence of the JOIN duplication**: `Graph_makeQuery` repeats
  the same `dijagnoza/mkb10/kategorija` and `operacija/funkcija/zaposleni`
  LEFT JOIN blocks found (twice) in [B2 SQLite](B2_SQLite.md) — see
  REWORK-BRIEF.md.
- **Three responsibilities in one class** (query building, matplotlib
  rendering, settings-dialog GUI) — a Rule #20 cohesion smell; natural split
  points: query builder / chart renderer / settings dialog.
- **Duplicated settings-persistence pattern**: `Graph_SettingUp`'s
  save/restore-to-`Settings.json` logic and its nested `create_meter`
  helper are near-duplicates of [B5 AI](B5_AI.md)'s
  `ImageReader_SettingUp` — a Rule #5 candidate.
- SQL in `Graph_makeQuery` is built via f-string interpolation, not
  parameterized — same structural caveat as [B2 SQLite](B2_SQLite.md).
