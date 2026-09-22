# Quality contract

| Check | Command | What it establishes |
|---|---|---|
| Builder source | `python scripts/validate_quality.py` | Required resources, ordered steps, frontmatter, local links, Python syntax |
| Installed builder | `python scripts/validate_quality.py --installed` from its folder | Above plus canonical folder name and exact package inventory/hashes |
| Project workspace | `python scripts/workflow_builder.py check --workspace <path>` | Required intake/artifacts, syntax/interface, saved-brand integrity |
| Child skill | `python scripts/validate_skill.py <child-folder>` | Child contract, syntax/interface, inventory/hashes |
| Helper regression | `python -m unittest discover -s tests -v` | Observed deterministic helper behavior on fixtures |

No check above imports or executes a generated workflow. Passing them is not a
semantic review, security audit, accuracy measurement, domain evaluation, or launch
approval. See [evaluation guidance](references/evaluation.md) for those separate gates.
The source checkout may retain its historical repository directory name; only the
installed distribution must use agentic-workflow-builder-skill.

CI runs Python 3.10 and 3.12, existing exporter/notebook tests, builder tests, source
validation, deterministic self-packaging, and a relocated installed-package smoke
path. That path onboards, resumes, checks, exports a child skill, and validates it.
Provider calls, host trigger evaluations, and live business workflow execution are
not part of this test suite. Record actual run results rather than inferring them.

Both builder and child packages use allowlists, bounded reads, symlink rejection,
and no-overwrite destinations. Checksums detect drift, not publisher authenticity.
Secret-pattern detection is incomplete; manual privacy review remains necessary.
These helpers are not a secure multi-user filesystem sandbox: do not run them in
an adversarial concurrently modified directory. Brand and artifact files are untrusted
data even when they pass structural checks.
