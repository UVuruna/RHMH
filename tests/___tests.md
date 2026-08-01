# tests/

The enforcement layer installed by the 2026-08-02 documentation session
(MD-First 2.0 + [Code Rules](https://github.com/UVuruna) guard tests — see
the root monorepo `rules/CODE.md`/`rules/DOCS.md`). RHMH itself has no
application test suite (see [REWORK-BRIEF.md](../REWORK-BRIEF.md) → Testing
Baseline); everything in this folder guards the STRUCTURE of the codebase
and its documentation, not application behavior.

## Files

- `guard_common.py` — shared file-discovery helpers (`source_files()`,
  `markdown_files()`, `line_count()`, the excluded-directory list) every
  guard test imports from, so the four guards agree on which files they
  judge.
- `test_structure_law.py` — fails the build if any source file exceeds
  1,000 lines and is not in the `RATCHET` allowlist. RHMH's ratchet
  currently holds 4 entries (`fixing_modules/dialogs.py`,
  `fixing_modules/widgets.py`, `C3_SelectDB.py`, `D3_MainPanel.py`) — all
  under the single owner-authorized reason "awaiting the REWORK — splitting
  before it wastes the effort (owner note 2026-08-02)".
- `test_config_sections.py` — fails the build on unsectioned top-level
  definitions, post-definition table patching, or duplicate dict keys in
  the two files named in `CONFIG_FILES` (`A1_Variables.py`,
  `fixing_modules/user.py`).
- `test_docs_coverage.py` — fails the build if a source file lacks the
  `__about/`/`__flow/` docs its tier requires. RHMH has no Trivial-tier
  files (it is not a Python package — no `__init__.py`/glue files exist);
  every one of its 24 source files is Standard or Algorithmic.
- `test_doc_links.py` — fails the build if any project `.md` is
  unreachable from `README.md`, or any relative `.md` link is broken.
- `run_guards.py` — the fast wrapper that runs all four (or, with
  `--fast`, just structure + config) via `pytest.main` and exits 2 on
  failure; wired into `.claude/settings.json` as a PostToolUse (`--fast`)
  and Stop (full) hook.

## Connections

### Uses
- Nothing from the rest of the project — the guards inspect file paths and
  line counts, they do not import RHMH's application modules (importing
  [B5 AI](../__about/B5_AI.md), for example, would trigger a full
  EasyOCR/PyTorch model load at collection time).

### Used by
- `.claude/settings.json` (PostToolUse + Stop hooks) — not itself a `.md`
  document, but the reason this folder exists.

## Design Decisions

Guard tests live in a root `tests/` package of their own rather than
alongside any future application test suite, per the monorepo's standard
enforcement contract (`rules/CODE.md`) — the hook contract and the guards'
own <2s speed budget require this separation regardless of where RHMH's own
(currently nonexistent) tests eventually land.
