# B3 Media

**Script:** [B3 Media (script)](../B3_Media.py)

## Purpose

Image/video utilities for the GUI: the animated GIF splash/loading widget
actually used by the app (a second, evolved copy of
[A3 Load Splash](A3_LoadSplash.md)'s class — see that doc), a zoomable/
pannable full-screen image/video viewer, video-thumbnail generation, opening
media in the OS default app, and small image/color helpers (resize,
darken).

## Connections

### Uses
- [A1 Variables](A1_Variables.md) — `from A1_Variables import *` (uses
  `App`, `ThemeColors`, `IMAGES`).

### Used by
- [C1 Controller](C1_Controller.md), [C2 Manage DB](C2_ManageDB.md),
  [C3 Select DB](C3_SelectDB.md), [D1 Top Panel](D1_TopPanel.md),
  [D2 Form Panel](D2_FormPanel.md), [D3 Main Panel](D3_MainPanel.md),
  [E Start](E_Start.md) — `Media` and `Loading_Splash` both imported via
  `from B3_Media import Media,Loading_Splash`.
- Imported but with no visible call site in this session's review:
  [B4 Graph](B4_Graph.md) and [B5 AI](B5_AI.md) both `import Media` — worth
  a repo-wide grep before treating as dead (see OPEN-QUESTIONS.md).

## Classes

### Loading_Splash
Animated GIF splash/loading overlay — the version actually wired into the
app (E_Start starts it during boot). See
[A3 Load Splash](A3_LoadSplash.md) for the near-duplicate standalone
version. Same threaded-preload/animate design; this copy additionally
centers the splash via `App.get_window_center()` and reads its transparent
key color from `ThemeColors['bg']` instead of a plain hex default.
- `__init__(folder, dimension=850, fps=12)`, `load_image(i)`,
  `create_splash(widget, alpha=1)`, `play()`, `stop()` (contains a leftover
  debug `print('odradio stop')`), `_animate()` — same responsibilities as
  the A3 version.

### Media
Static-only image/video utility bag (class attrs hold shared viewer state —
e.g. `Slike_Viewer`, `Image_Active`, `Image_Scale` — effectively one global
media-viewer instance app-wide).
- `ProgressBar_DownloadUpload(title, titletxt, width)`: builds a Drive
  up/download progress `Toplevel` (title, scrollable log Text, `Floodgauge`,
  looping "Web" GIF); returns `(text_widget, bar, gif)` for the caller to
  drive.
- `label_ImageLoad(images_list)`: batch-loads `(path, width, height)` tuples
  into resized `PhotoImage`s.
- `hover_label_button(event, img)`: swaps a Label's image on hover.
- `image_to_blob(file_path)`: reads raw bytes for DB BLOB storage.
- `get_image(image_blob_data)`: opens a PIL Image from in-memory blob bytes.
- `resize_image(image, max_width, max_height, savescale=False)`:
  aspect-preserving fit-to-bounds resize; optionally stashes the scale ratio
  into `Media.Image_Scale`.
- `create_video_thumbnail(video_data)`: writes bytes to a temp file, grabs
  the first frame via OpenCV, converts BGR→RGB, overlays a centered
  play-button icon, returns `(thumbnail, temp_path)`.
- `play_video(event, video_data)`: opens a video with the OS default player
  (`os.startfile`/`open`/`xdg-open`).
- `open_image(event, image_data)`: writes bytes to a **fixed** temp path
  (`temporary/temp_image.png`) and opens it with the OS default viewer —
  every call overwrites the same file, no cleanup, not safe for concurrent
  opens.
- `make_cropped_part()`: computes the currently-visible viewport of a
  zoomed/scrolled canvas from xview/yview fractions × zoomed dimensions,
  crops from `Image_Active`, exports via `open_image`.
- `zoom(event)`: mouse-wheel zoom handler — scales `Image_Scale` by `1.18`
  per wheel notch, clamps 33px–6000px, re-renders centered, updates the
  scrollregion.
- `move_from(event)` / `move_to(event)`: canvas drag-pan via
  `scan_mark`/`scan_dragto`.
- `ajdust_About_logo(event)`: resizes the About-dialog logo to fill its
  canvas on `<Configure>`.
- `darken_color(hex_color, factor=0.75)`: manual hex→RGB→scale→hex darkening
  (duplicates functionality Pillow/`colorsys` already provide).

## Architecture notes

- Same class-as-namespace/singleton pattern as
  [B1 Google Drive](B1_GoogleDrive.md) — all state on class attributes, so
  there is effectively one media-viewer state app-wide, not one per window.
- `Loading_Splash` is **not** one of the 14 classes `E_Start.start()` passes
  to `Classes_Decorating` — unlike `Media`, its methods are never wrapped by
  `error_catcher`/`method_efficency` at all. Combined with `load_image`
  running on a raw `threading.Thread` target (whose uncaught exceptions the
  `threading` module only prints to stderr), a missing `{i}.gif` frame fails
  silently from the app's own logging perspective — a real No Error Masking
  (rules/CODE.md) gap, flagged for the rework, not fixed here
  (zero-behavior-change scope).
