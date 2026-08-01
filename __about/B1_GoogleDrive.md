# B1 Google Drive

**Script:** [B1 Google Drive (script)](../B1_GoogleDrive.py)

## Purpose

Thin static wrapper around the Google Drive API v3: OAuth authentication and
token lifecycle, file upload/download (both to-disk and in-memory BLOB
variants), rename/delete/trash, folder permission grants, and a
log-file-by-name-prefix finder. This is the app's only network/cloud
touchpoint — every Drive interaction elsewhere in the app goes through this
class.

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *`.

### Used by
- [C1 Controller](C1_Controller.md), [C2 Manage DB](C2_ManageDB.md),
  [C3 Select DB](C3_SelectDB.md), [D4 Window](D4_Window.md),
  [E Start](E_Start.md).

## Classes

### GoogleDrive
Static-only (no instances; `creds`/`connection` are class attributes —
effectively one process-wide Drive session, not one per caller).
- `SCOPES` (class attr): 5 OAuth scope URLs — `drive`, `drive.file`,
  `admin.directory.user`, `userinfo.email`, `openid`.
- `setup_connection()`: authenticates, builds the `drive v3` service object.
- `create_new_token()`: forces a fresh interactive OAuth consent flow,
  pickles the new token to `www_token.pickle`.
- `authenticate_google_drive()`: loads the pickled token if present;
  refreshes it if expired and a refresh token exists (drops the pickle file
  on refresh failure); otherwise runs the interactive flow; persists
  credentials either way.
- `get_UserEmail()`: queries the `oauth2 v2` userinfo endpoint for the
  authenticated account's email.
- `get_FileInfo(file_id)`: fetches name/size/mimeType, plus width/height for
  image files.
- `download_File(file_id, destination)`: chunked download to a `_progress`
  temp file, then an atomic rename over `destination`.
- `download_BLOB(file_id)`: chunked download into an in-memory `BytesIO`,
  returns raw bytes (used to pull images/DB snapshots without touching disk
  first).
- `upload_NewFile_asFile(...)` / `upload_NewFile_asBLOB(...)`: create a new
  Drive file from a local path or from in-memory bytes; return the new file
  id.
- `upload_UpdateFile(file_id, path, mime)`: replaces the content of an
  existing Drive file.
- `upload_UpdateFile_changeName(file_id, new_name)`: renames an existing
  file.
- `delete_file(file_id)`: permanent delete.
- `delete_trash(file_id)`: sets `trashed: True` (soft delete).
- `find_logs(folder_id)`: lists a folder's files, returns `{name: id}` for
  names starting with `"LOG - "` — this is how
  `GodMode.JoiningLogs()` ([C1 Controller](C1_Controller.md)) discovers every
  user's remote per-user log database.
- `add_permission_to_folder(folder_id, user_email)`: grants `writer` role on
  a folder to an email — used by `create_new_user()`
  ([C1 Controller](C1_Controller.md)) when onboarding a new account.

## Credential & token files

Reads `www_credentials.json` (OAuth client secret, gitignored, read-only)
and reads/writes `www_token.pickle` (cached user token, gitignored — deleted
and re-created on a failed refresh). Neither file's contents are reproduced
here or anywhere in the docs (Rule against secrets in documentation); both
are absent from git via `.gitignore`.
