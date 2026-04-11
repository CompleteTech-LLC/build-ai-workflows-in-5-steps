# Build scripts

Regenerable source-of-truth for the shipped artifacts in this repo.
You do **not** need these to run the lesson — they are development-time
tools for maintainers and contributors.

## `build_notebook.py`

Regenerates `build_ai_workflows_in_5_steps.ipynb` from the Python cell
definitions at the top of the script.

```bash
python scripts/build_notebook.py
```

Run this after editing any cell content, adding a cell, or reordering
sections. The output is a clean notebook with no execution outputs —
students will produce their own outputs when they Run All.

Why Python-as-source instead of editing the `.ipynb` directly:

- Version control diffs stay readable (Python >> raw notebook JSON).
- Cells can be reordered and re-cut without hand-JSON surgery.
- No escape-hell for triple-quoted markdown blocks.

## `generate_assets.py`

Regenerates the two synthetic example assets shipped in `assets/`:

- `assets/source_financial_pack.pdf` — a fictional restaurant P&L for
  *"Sample Bistro & Co."* (the lesson's default input document)
- `assets/target_dashboard.png` — a dark-themed Tax Readiness &
  Financial Health Scorecard (the lesson's default target image)

```bash
python scripts/generate_assets.py
```

Run this if you want to tune the fake data, add teaching moments, or
rebrand the example. Deterministic via `random.seed(1337)` — re-running
produces byte-identical output unless you change the code. On completion
the script also runs a smoke check to verify every teaching moment in
the lesson is still preserved in the pypdf extraction.

## Dev-only dependencies

The build scripts need a few libraries the notebook itself does not:

```bash
pip install reportlab matplotlib pillow pypdf
```

Students running the notebook do **not** need to install these.
`reportlab` and `matplotlib` are only used at build time, and `pillow`
is used once to optimize the logo image.

## Philosophy

Both scripts treat their outputs as first-class artifacts that ship in
the repo — not temporary files. We keep the scripts here for three
reasons:

1. **Transparency.** You can see exactly how every asset in this repo
   was built.
2. **Reproducibility.** Any contributor can regenerate the artifacts
   deterministically.
3. **Diff-friendly editing.** A one-line text change in the lesson is
   a one-line change to `build_notebook.py` — not a hand-edit of a
   minified JSON file.

If you want to contribute a tweak: edit the script, run it, and commit
both the script change and the regenerated artifact in the same commit.
