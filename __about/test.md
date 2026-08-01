# test

**Script:** [test (script)](../test.py)

## Purpose

A standalone, manually-run maintenance script — **not** part of the
application's import chain (not referenced by `E_Start.py` or any other
project module) and **not** a pytest test despite the filename. It wipes
every row from every table in `LOGS.db` (except `sqlite_sequence`) and then
runs `VACUUM`. Both actions execute unconditionally at **module level** the
moment this file is run (not behind an `if __name__=='__main__':` guard) —
running it deletes real data in whichever `LOGS.db` is in the current
working directory. This documentation session never executed this file
(Rule: never execute application logic against a real DB).

## Connections

### Uses
- `sqlite3` (stdlib) only — no project-internal imports.

### Used by
- None (entry point / not yet wired — a manual maintenance utility the
  owner runs by hand when needed).

## Functions

### `obrisi_sve_podatke(baza)`
("delete all data") Connects to the given SQLite file, lists every table via
`sqlite_master`, and `DELETE FROM`s every one except `sqlite_sequence`
(which stores AUTO_INCREMENT counters). Called unconditionally at import
time with the literal argument `"LOGS.db"`.

### `optimizuj_bazu(baza)`
("optimize the database") Connects to the given SQLite file and runs
`VACUUM`. Also called unconditionally at import time with `"LOGS.db"`.

## Naming note

This file is unrelated to the guard tests in `tests/` (which use pytest's
`test_*.py` discovery convention with `assert`-based test functions) despite
sharing the word "test" — this is a plain maintenance script that happens to
be named `test.py`. Flagged for a rename in the rework (see
[OPEN-QUESTIONS.md](../OPEN-QUESTIONS.md)) to avoid confusion with the new
`tests/` guard suite.
