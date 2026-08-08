# B2 SQLite

**Script:** [B2 SQLite (script)](../B2_SQLite.py) ·
**Flow:** [diagram](../__flow/B2_SQLite.md)

## Purpose

Generic SQLite access layer: connection lifecycle, a dynamic
SELECT/WHERE/JOIN query builder, parameterized CRUD helpers, and
distinct-value lookups that feed dropdowns/filters. One class, `Database`,
instantiated **twice** — `RHMH` (the clinical database) and `LOGS` (the
audit/session database) — both sharing the exact same class and, because the
shared state is on class attributes rather than instance attributes, some of
its caches (`PatientQuery`, `LoggingQuery`, `LastQuery`) too (see
Architecture notes below).

**No `CREATE TABLE` statement exists anywhere in this file.** The schema is
introspected at runtime via `PRAGMA table_info(<table>)`; the authoritative
DDL (types, constraints, foreign keys, defaults) lives outside the 24 files
this documentation session reviewed. The table/column names below are
reconstructed from how queries reference them, not from a schema
declaration — flagged as an open question in
[REWORK-BRIEF.md](../REWORK-BRIEF.md) / [OPEN-QUESTIONS.md](../OPEN-QUESTIONS.md).

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *` (uses
  `RHMH_dict['path']`, `LOGS_dict['path']`).

### Used by
- [A2 Decorators](A2_Decorators.md), [B4 Graph](B4_Graph.md),
  [C1 Controller](C1_Controller.md), [C2 Manage DB](C2_ManageDB.md),
  [C3 Select DB](C3_SelectDB.md), [D2 Form Panel](D2_FormPanel.md),
  [D3 Main Panel](D3_MainPanel.md), [D4 Window](D4_Window.md),
  [E Start](E_Start.md).

## Classes

### Database
- Class attrs (shared across `RHMH` and `LOGS` — see Architecture notes):
  `PatientQuery` (last patient SELECT string, reused by the "filter within
  results" step), `LoggingQuery` (pretty-printed SQL for the audit log/UI),
  `LastQuery` (per-table cache: `pacijent`, `slike`, `mkb10`, `zaposleni`,
  `logs`, `session` — powers `refresh_tables()` re-running the last query
  instead of rebuilding it).
- `__init__(database)`: stores the db file path and a `threading.Lock` for
  serialized access.
- `start_LOGS_db()`: loads column lists for `logs`, `session` via PRAGMA.
- `start_RHMH_db()`: loads column lists for `pacijent`, `slike` (minus its
  last column, the image BLOB), `mkb10`, `zaposleni`; plus distinct-value
  caches: `pol`, `opis_slike`/`format_slike`, `dg_kategorija` (from
  `kategorija`), `dr_funkcija` (from `funkcija`).
- `format_sql(query)`: pretty-prints SQL via `sqlparse`.
- `connect()` / `close_connection()`: open/close the sqlite3 connection and
  cursor for one call.
- `show_columns(table)`: `PRAGMA table_info(table)` → column names.
- `creating_where_part(column, values: dict)`: builds one WHERE fragment per
  comparator — `EQUAL` (IN-list or `=`), `LIKE`/`NOT LIKE` (OR'd/AND'd
  wildcard), `BETWEEN` (OR'd ranges), `GREATER`/`LESS` (single bound).
- `execute_selectquery(query, columns=False)`: runs raw SQL, optionally
  returning column names alongside rows.
- `execute_select(log, table, *args, **kwargs)`: plain
  `SELECT cols FROM table [WHERE ...]`; tracks `PatientQuery`/`LastQuery`
  when `table == 'pacijent'`.
- `execute_join_select(table, *args, **kwargs)`: the core read-path query
  builder — see [flow](../__flow/B2_SQLite.md) for the algorithm.
- `execute_filter_select(columns: dict)`: string-splices extra
  `IS [NOT] NULL` conditions into the **cached** `PatientQuery` by locating
  the literal substrings `'WHERE'`/`'GROUP BY'` — depends on call order (a
  prior call must have set `PatientQuery`); flagged as fragile in
  REWORK-BRIEF.md.
- `get_patient_data(ID)`: single-patient mega-query — same
  GROUP_CONCAT/CASE join pattern as `execute_join_select`, plus a synthetic
  `Slike` column concatenating `Naziv`/`Veličina`/`width`/`height` (split
  back into a list in Python).
- `execute_Update(table, id: tuple, **kwargs)`: parameterized
  `UPDATE ... SET col=? WHERE id_col=?`, commits.
- `execute_Insert(table, **kwargs)`: parameterized INSERT (skips falsy
  values), commits, returns `last_insert_rowid()`.
- `execute_Delete(table, ids: list)`: `DELETE FROM table WHERE ...` — values
  are **inlined via f-string, not parameterized** (unlike Update/Insert);
  runs `PRAGMA foreign_keys=ON` first.
- `get_imageBlob(id)`: `SELECT blob_data FROM slike WHERE id_slike = {id}`.
- `get_distinct_mkb(mkb=None, IDS=None)`: distinct MKB code prefixes
  (catalog drill-down), optional prefix + patient-ID filter.
- `get_distinct_zaposleni(funkcija=None, IDS=None)`: distinct staff names
  from `operacija` ⋈ `zaposleni`, optional role + patient-ID filter.
- `get_distinct_date(datetype, datewhere, IDS=None)`: sorted distinct
  `strftime(datetype, datewhere)` values from `pacijent`.
- `get_distinct(table, *args)`: generic distinct-value query over arbitrary
  columns.
- `execute_Insert_Many(from_DB, to_DB, table, columns)` *(static)*: copies
  rows for given columns between two `Database` instances via
  `INSERT OR IGNORE` — the merge mechanism used when reconciling downloaded
  snapshots (see `GodMode.JoiningLogs()` in
  [C1 Controller](C1_Controller.md)).
- `Vaccum_DB()`: runs `VACUUM`.

### Module-level instances
`RHMH = Database(RHMH_dict['path'])`, `LOGS = Database(LOGS_dict['path'])` —
the two live database handles every other module imports.

## Tables referenced (inferred from queries — no literal DDL in this file)

| Table | Columns seen in queries |
|-------|--------------------------|
| `pacijent` | `id_pacijent`, `Pol`, `Datum Prijema`, `Datum Otpusta`, `Datum Operacije`, `Starost`, + full PRAGMA-loaded set |
| `slike` | `id_slike`, `id_pacijent`, `blob_data` (last column), `Naziv`, `Veličina`, `width`, `height`, `Opis`, `Format` |
| `mkb10` | `id_dijagnoza`, `` `MKB - šifra` `` (backtick-quoted — contains a space) |
| `zaposleni` | `id_zaposleni`, `Zaposleni` |
| `dijagnoza` (join: pacijent ↔ mkb10) | `id_pacijent`, `id_dijagnoza`, `id_kategorija` |
| `kategorija` | `id_kategorija`, `Kategorija` |
| `operacija` (join: pacijent ↔ zaposleni via funkcija) | `id_pacijent`, `id_zaposleni`, `id_funkcija` |
| `funkcija` | `id_funkcija`, `Funkcija` |
| `logs`, `session` | PRAGMA-loaded only, not individually referenced here |

## Architecture notes

- **Shared class-level caches**: `PatientQuery`/`LoggingQuery`/`LastQuery`
  are class attributes, so `RHMH` and `LOGS` — both instances of the same
  `Database` class — technically share one copy unless each instance sets
  its own; worth re-verifying during the rework whether this is intentional.
- **Lock hazard**: several methods manually `.acquire()`/`.release()` a
  `threading.Lock` interleaved with nested calls into
  `self.execute_selectquery` (which acquires the same lock) — a
  release-before-nested-call / re-acquire-after pattern. An exception
  between release and re-acquire risks an inconsistent lock state.
- **SQL injection surface**: only `execute_Update`/`execute_Insert` use `?`
  parameter binding; `execute_Delete`, `execute_select`,
  `execute_join_select`, `get_patient_data` and the `get_distinct_*` helpers
  interpolate values via f-strings. Values are internally sourced (UI
  selections, cached IDs), not raw free text — except `GodMode.FreeQuery_Execute()`
  in [C1 Controller](C1_Controller.md), which executes a user-typed raw SQL
  string directly. See REWORK-BRIEF.md → Security Observations.
- **Duplicated JOIN SQL**: the `dijagnoza`/`mkb10`/`kategorija` and
  `operacija`/`funkcija`/`zaposleni` LEFT JOIN blocks are repeated verbatim
  in `execute_join_select`, `get_patient_data`, and a third time in
  [B4 Graph](B4_Graph.md)'s `Graph_makeQuery` — a No Duplicate Code
  (rules/CODE.md) candidate for the rework.
