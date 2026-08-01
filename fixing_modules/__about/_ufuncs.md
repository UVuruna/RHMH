# _ufuncs

**Script:** [_ufuncs (script)](../_ufuncs.py)

## Purpose

A vendored copy of PyTorch's internal `torch._numpy._ufuncs` module —
implements NumPy-compatible elementwise binary/unary math ufuncs (add, sin,
matmul, divmod, modf, …) on top of `torch.Tensor`. **This file has no
connection to a GUI application or to patient/medical data of any kind.**
Its own relative imports (`from . import _binary_ufuncs_impl,
_dtypes_impl, _unary_ufuncs_impl, _util`, `from ._normalizations import
(...)`) point at sibling modules inside `torch/_numpy/` that do not exist in
this project, so — like `scaling_base_class.py` — this file **cannot
successfully import from its current location**. Of everything found in
`fixing_modules/`, this is the strongest candidate for an accidental
copy-paste artifact (e.g. an IDE "go to definition" saved to the wrong
folder) rather than intentional vendoring — there is no plausible reason a
medical patient-records app would need PyTorch's own numpy-compatibility
internals distinct from the `torch`/`easyocr` usage already covered in
[B5 AI](../../__about/B5_AI.md). Flagged, not deleted, per this session's
zero-behavior-change scope (Guideline #3 — ask before deleting; see
[OPEN-QUESTIONS.md](../../OPEN-QUESTIONS.md)).

## Connections

### Uses
- `torch` (third-party) plus unresolvable `torch/_numpy`-internal relative
  imports. No project-internal imports.

### Used by
- None — confirmed zero references anywhere in the app.

## Functions

- `_ufunc_postprocess(result, out, casting)`: casts/broadcasts a result into
  a caller-supplied `out` tensor if given.
- `deco_binary_ufunc(torch_func)`: decorator factory wrapping a binary torch
  op with NumPy-style dtype casting/broadcasting/`out=` handling.
- `matmul(x1, x2, ...)`: special-cased binary ufunc (`axes`/`axis`
  signature, no `where`).
- `ldexp(x1, x2, ...)`: special-cased binary ufunc (result dtype forced from
  the first argument; float16 restore quirk).
- `divmod(x1, x2, out1, out2, ...)`: two-output binary ufunc; validates
  conflicting `out`/`out1`/`out2` arguments.
- `modf(x, ...)`: fractional/integer part split, implemented via
  `divmod(x, 1)`.
- `deco_unary_ufunc(torch_func)`: decorator factory wrapping a unary torch
  op with NumPy-style dtype casting (promotes ints to float for `_fp_unary`
  ops).
- Two module-level `for` loops dynamically attach generated wrapped
  functions into the module namespace (`vars()[name] = ...`) for every
  entry in `_binary`/`_unary`.

## Module-level data

- `NEP50_FUNCS` (tuple), `_fp_unary` (list) — internal PyTorch/NumPy-
  promotion constants, not RHMH configuration.
