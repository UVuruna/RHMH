# RHMH

RHMH is a medical patient-management system built for a reconstructive-surgery hospital department. It handles patient records, medical imaging, the MKB-10 diagnosis catalog, staff data, and operational analytics, with AI-powered OCR for scanned documents and Google Drive backup. It works both online and offline.

## Features

- Patient record management (personal data, visits, medical history)
- Medical imaging storage and viewing
- MKB-10 diagnosis catalog lookup and entry
- Staff/personnel data management
- Operational analytics and charts
- AI-assisted OCR for reading scanned/printed documents (EasyOCR + OpenCV)
- Google Drive backup and sync, with offline fallback to local SQLite

## Tech Stack

- **Language:** Python
- **GUI:** ttkbootstrap (Tkinter), customtkinter
- **Database:** SQLite
- **Cloud:** Google Drive API
- **AI/ML:** PyTorch, EasyOCR, OpenCV
- **Data & Charts:** Pandas, NumPy, Matplotlib
- **Imaging:** Pillow

## Structure

The codebase is organized as layered, letter-prefixed modules:

- `A*` — variables/config, decorators, splash screen
- `B*` — services: Google Drive, SQLite, media, graphs, AI/OCR
- `C*` — controllers: app controller, DB management, DB selection
- `D*` — GUI panels and main window
- `E_Start.py` — application entry point

## Run/Setup

Entry point: `E_Start.py`. Requires the Python packages listed under Tech Stack (no `requirements.txt` currently checked in). Google Drive access requires `www_credentials.json` (gitignored) and produces a local `www_token.pickle` on first authentication.
