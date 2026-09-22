# Onboarding

## Choose your entry point

New to the lesson: run `python scripts/build_skill_notebook.py`, open the generated
`build_ai_workflows_in_6_steps.ipynb`, and follow all six steps. You need Python
3.10+, a notebook host, and one approved provider key for Steps 1–5.

Already completed Steps 1–5: open `create_workflow_skill.ipynb` or use the CLI in
README.md. Confirm `decomposition.md`, `workflow.mmd`, and `workflow.py` exist in
the same output directory. A fresh kernel works; earlier variables are not needed.

Trying the packaging step offline: use `examples/workflow` as the input directory.
No credential is needed. This is synthetic test data, not an evaluated AI workflow.

## Before export

Choose a lowercase, hyphen-separated skill name (1–64 characters), a clear title,
and a task-specific description (up to 1,024 characters). Review the workflow's
input/output contract and ensure Step 5 defines
`run_workflow(source_path, target_dashboard_path, ai=None)`.

Choose the downstream output identity. Use an explicit brand profile or place
`brand-profile.json` alongside the workflow artifacts. No profile means the
CompleteTech starter; `--unbranded` disables that fallback. See BRANDING.md.

## First successful action

Export the synthetic example using the command in README.md, then validate the
resulting folder. Success means the folder/ZIP are structurally valid, not that a
production workflow has been executed or proven correct.

Read the exported ONBOARDING.md and review checklist before copying the skill into
an agent's skill directory. Installation, dependencies, AI calls, and execution
need separate user approval. Use a new export destination for reruns; existing
packages are intentionally not overwritten.

## Troubleshooting

Missing artifact: complete Steps 3–5, or point `--outputs` at their actual directory.
Syntax/signature error: review and repair Step 5's generated Python; do not execute
it merely to diagnose packaging. Invalid branding: repair the supplied profile;
the exporter will not silently replace it. Hash mismatch: the exported files have
changed; inspect them and rebuild from reviewed sources rather than bypassing checks.

Run `python -m unittest discover -s tests -v` for the offline exporter tests.
