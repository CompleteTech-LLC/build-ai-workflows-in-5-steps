# Step 6 — From a completed workflow to a reusable skill

## Why a sixth step?

Step 5 produces Python, but a later agent still needs to know when to use it,
what inputs to request, which decisions need judgment, what approval gates remain,
and how the output should be branded. Step 6 preserves that operating contract.
It does not ask another model to re-derive the workflow or rewrite the artifacts.

## Entry points

`create_workflow_skill.ipynb` is the ready-to-open continuation. It reads saved
artifacts from a fresh kernel and needs no API key. Run
`python scripts/build_skill_notebook.py` to generate the combined six-step lesson;
the builder inserts Step 6 before the original recap without changing earlier code
cells. Repository and original five-step notebook names remain backward compatible.

For automation, use `scripts/create_workflow_skill.py --help`. Required options are
`--name`, `--title`, and `--description`. Optional inputs are `--outputs` (default
`outputs`), `--destination` (default `outputs/skills`), and either `--brand-profile`
or `--unbranded`. Export destinations must be new; no overwrite flag is provided.

## Contract and handoff

Input artifacts are `decomposition.md`, `workflow.mmd`, and `workflow.py`. The Python
must parse and define exactly one synchronous
`run_workflow(source_path, target_dashboard_path, ai=None)` function. The package
preserves those three files byte-for-byte and records their SHA-256 hashes.

The exporter adds a scoped SKILL.md, input examples, onboarding, requirements,
review checklist, branding metadata/assets, UI metadata, an inventory, and a
self-contained validator. References stay outside SKILL.md so hosts can load them
only when the workflow is relevant. The portable ZIP contains one named skill
folder, with deterministic ordering and timestamps.

The requirements file reflects Step 5's stdlib/pypdf constraint, not a dependency
resolver. Review generated imports, install/pin approved dependencies, and supply
your own compatible AI adapter. The packaging step cannot prove that model-generated
code honors the dependency contract or implements the decomposition correctly.

## Review boundary

Packaging performs no workflow imports, AI calls, dependency installs, registry
publication, or automatic skill installation. The validator performs syntax,
entrypoint, inventory, name, and hash checks. It does not execute the workflow.
A manifest saying unreviewed is deliberate, not a missing implementation detail.

Only three workflow artifacts and an explicitly selected logo/profile are copied.
Raw sources, target images, .env files, SDK clients, and chat history are excluded.
Secret patterns catch some common credentials; they are neither a complete scanner
nor a PII detector. Derived references can contain customer data and prompt
injection text. Review them before distribution. Read code before importing it,
because top-level Python statements execute on import.

## Acceptance checks before real use

Validate the package, then separately review code and dependencies. With explicit
execution approval, test a synthetic happy path against known expected output,
missing/malformed input, and an ambiguous branch without an AI adapter. Verify a
second independent input, permission boundaries, and host trigger/non-trigger
behavior. Record what actually passed; never treat packaging tests as domain evals.
For the financial lesson, qualified domain review is required before reliance.

## Installation

After review, manually copy the directory to `.agents/skills/` for a Codex project
or `.claude/skills/` for a Claude Code project. Codex UI metadata sets
`allow_implicit_invocation: false`; explicitly invoke the skill. That host-specific
flag is not a universal execution sandbox and other hosts may ignore it. Keep
execution and external-action approvals in the host's permissions system.

## References

- [Agent Skills format](https://agentskills.io/specification)
- [Codex skill discovery and UI metadata](https://developers.openai.com/codex/skills/)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Brand contract and CompleteTech source provenance](../BRANDING.md)
