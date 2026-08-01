# RHMH

RHMH is a medical patient-management system built for a reconstructive-surgery hospital department. It handles patient records, medical imaging, the MKB-10 diagnosis catalog, staff data, and operational analytics, with AI-powered OCR for scanned documents and Google Drive backup. It works both online and offline.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Structure](#structure)
- [Run/Setup](#run-setup)
- [Documentation](#documentation)
- [Project Documents](#project-documents)

<a id="features"></a>

## Features

- Patient record management (personal data, visits, medical history)
- Medical imaging storage and viewing
- MKB-10 diagnosis catalog lookup and entry
- Staff/personnel data management
- Operational analytics and charts
- AI-assisted OCR for reading scanned/printed documents (EasyOCR + OpenCV)
- Google Drive backup and sync, with offline fallback to local SQLite

<a id="tech-stack"></a>

## Tech Stack

- **Language:** Python
- **GUI:** ttkbootstrap (Tkinter), customtkinter
- **Database:** SQLite
- **Cloud:** Google Drive API
- **AI/ML:** PyTorch, EasyOCR, OpenCV
- **Data & Charts:** Pandas, NumPy, Matplotlib
- **Imaging:** Pillow

<a id="structure"></a>

## Structure

The codebase is a FLAT set of layered, letter-prefixed modules at the
project root (not a Python package — no `__init__.py`, every module is
imported by bare name):

- `A*` — variables/config ([A1](__about/A1_Variables.md)), decorators
  ([A2](__about/A2_Decorators.md)), splash screen
  ([A3](__about/A3_LoadSplash.md) — not currently used, see its doc)
- `B*` — services: Google Drive ([B1](__about/B1_GoogleDrive.md)), SQLite
  ([B2](__about/B2_SQLite.md)), media ([B3](__about/B3_Media.md)), graphs
  ([B4](__about/B4_Graph.md)), AI/OCR ([B5](__about/B5_AI.md))
- `C*` — controllers: shared state + admin
  ([C1](__about/C1_Controller.md)), write-path ([C2](__about/C2_ManageDB.md)),
  read-path ([C3](__about/C3_SelectDB.md) — god-file, ratcheted)
- `D*` — GUI panels: title bar ([D1](__about/D1_TopPanel.md)), patient form
  ([D2](__about/D2_FormPanel.md)), main window
  ([D3](__about/D3_MainPanel.md) — god-file, ratcheted), bootstrap
  ([D4](__about/D4_Window.md))
- [E_Start.py](__about/E_Start.md) — application entry point
- [test.py](__about/test.md) — a standalone manual DB-maintenance script
  (not a pytest test, despite the name)
- [fixing_modules (folder)](fixing_modules/___fixing_modules.md) — turns
  out to hold **vendored third-party library code**, not original RHMH
  logic — see its folder doc and
  [REWORK-BRIEF.md](REWORK-BRIEF.md) for the full finding

<a id="run-setup"></a>

## Run/Setup

Entry point: `E_Start.py`. Requires the Python packages listed under Tech Stack (no `requirements.txt` currently checked in). Google Drive access requires `www_credentials.json` (gitignored) and produces a local `www_token.pickle` on first authentication.

<a id="documentation"></a>

## Documentation

Documentation follows **MD-First 2.0**: every code file has an `__about/`
doc (what it does, its connections) and, where a diagram genuinely explains
the logic better than prose, a `__flow/` doc (Mermaid diagram + pseudocode).
Start below and follow the links — from this page every `.md` file in the
project is reachable.

### Module docs (root)

| Module | About | Flow |
|--------|-------|------|
| A1 Variables (central config) | [about](__about/A1_Variables.md) | [flow](__flow/A1_Variables.md) |
| A2 Decorators | [about](__about/A2_Decorators.md) | — |
| A3 Load Splash (unused) | [about](__about/A3_LoadSplash.md) | [flow](__flow/A3_LoadSplash.md) |
| B1 Google Drive | [about](__about/B1_GoogleDrive.md) | — |
| B2 SQLite | [about](__about/B2_SQLite.md) | [flow](__flow/B2_SQLite.md) |
| B3 Media | [about](__about/B3_Media.md) | — |
| B4 Graph | [about](__about/B4_Graph.md) | [flow](__flow/B4_Graph.md) |
| B5 AI (OCR) | [about](__about/B5_AI.md) | [flow](__flow/B5_AI.md) |
| C1 Controller | [about](__about/C1_Controller.md) | — |
| C2 Manage DB | [about](__about/C2_ManageDB.md) | — |
| C3 Select DB (god-file) | [about](__about/C3_SelectDB.md) | [flow](__flow/C3_SelectDB.md) |
| D1 Top Panel | [about](__about/D1_TopPanel.md) | — |
| D2 Form Panel | [about](__about/D2_FormPanel.md) | — |
| D3 Main Panel (god-file) | [about](__about/D3_MainPanel.md) | [flow](__flow/D3_MainPanel.md) |
| D4 Window | [about](__about/D4_Window.md) | — |
| E Start (entry point) | [about](__about/E_Start.md) | [flow](__flow/E_Start.md) |
| test (manual DB script) | [about](__about/test.md) | — |

### Other folders

| Folder | Entry point |
|--------|-------------|
| `fixing_modules/` — vendored/patched third-party GUI library code | [fixing_modules (folder)](fixing_modules/___fixing_modules.md) |
| `tests/` — the four structural guard tests + runner | [tests (folder)](tests/___tests.md) |

<a id="project-documents"></a>

## Project Documents

| Document | Description |
|----------|-------------|
| [REWORK-BRIEF.md](REWORK-BRIEF.md) | Functional map of the entire app as it exists today, written for the future rework session — every feature, its owning module, architectural problems, DB schema summary, and open questions |
| [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) | Dilemmas this documentation session could not resolve alone |
| [CLAUDE.md](CLAUDE.md) | Project facts and laws for AI agent sessions |
