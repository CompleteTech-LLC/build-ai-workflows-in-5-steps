# Agentic Workflow Builder Skill

<p align="center"><img src="assets/completetech_logo.jpg" alt="CompleteTech LLC" width="240"/></p>

**Turn an outcome and source materials into a reusable workflow skill in six steps.**
Part of the CompleteTech LLC skills library. Skill key:
`agentic-workflow-builder-skill`. Version: **1.0.0**. Python helpers: **3.10+**.

This repository is now a skill itself, not just a notebook or a skill exporter.
It guides an agent through onboarding, goal/source priming, decomposition, Mermaid
design, deterministic Python creation, evaluation planning, and child-skill export.
The original five-step notebook and Step 6 continuation remain available in the
repository for teaching; the installable skill does not depend on them.

## Two different skills

| Item | Job |
|---|---|
| This builder skill | Help design a workflow and create its reusable skill package. |
| The generated child skill | Apply that captured domain workflow to new inputs. |

The builder uses the current agent host for reasoning. Its local helpers need no
provider API key, notebook host, or third-party Python package. Generated workflows
have separate runtime requirements and execution approvals.

## Install and start

From a repository checkout, build a clean, allowlisted distribution:

```bash
python scripts/validate_quality.py
python scripts/package_builder_skill.py --destination outputs/builder-distribution
```

Review the resulting `agentic-workflow-builder-skill` folder, then manually copy it
into the chosen host's skill directory. For project-scoped Codex use
`.agents/skills/agentic-workflow-builder-skill`; for Claude Code use
`.claude/skills/agentic-workflow-builder-skill`. Do not copy it into both locations
for the same host. The legacy repository name stays unchanged; the installed folder
matches the skill key. No automatic installation or publication is performed.

In Codex:

```text
$agentic-workflow-builder-skill
Help me turn my support-triage process into a reusable skill. Start with onboarding,
reuse what I have already provided, and keep customer-facing sends approval-gated.
```

In Claude Code, invoke `/agentic-workflow-builder-skill` with the same request.
Other hosts need their own documented installation/discovery procedure. Host-level
loading and trigger behavior are not established by the offline Python tests.

Start with [ONBOARDING.md](ONBOARDING.md), then [SKILL.md](SKILL.md).

## Onboarding and resume

The agent first reuses known facts, then asks only for missing outcome, source,
target, owner, success criteria, constraints, permissions, and branding. It writes
preferences and curated facts to an explicitly chosen local workspace; no global
configuration, account scan, scheduler, or source-file crawl is created.

```bash
# SKILL_DIR is the absolute path to this installed skill or repository checkout.
python "$SKILL_DIR/scripts/workflow_builder.py" template
python "$SKILL_DIR/scripts/workflow_builder.py" init \
  --workspace /approved/project/workflow --intake /approved/project/intake.json
python "$SKILL_DIR/scripts/workflow_builder.py" status --workspace /approved/project/workflow
```

Omitting `--intake` creates an incomplete draft from the blank template. The helper
reports unanswered facts; it does not invent them. Existing workspaces are never
overwritten. Status/resume uses the saved facts, and export refuses incomplete intake.

## The six stages

| Stage | Durable artifact |
|---|---|
| 1. Prime the goal | `goal.md` |
| 2. Inspect authorized sources | `source-intake.md` |
| 3. Decompose the transformation | `decomposition.md` |
| 4. Visualize branches and approvals | `workflow.mmd` |
| 5. Crystallize and plan evaluation | `workflow.py`, `evaluation-plan.md` |
| 6. Package the workflow | Child skill folder and ZIP |

The agent authors these artifacts from evidence using
[the method guide](references/six-step-method.md). The helper is not a model runner
and does not implement arbitrary business logic on its own.

```bash
python "$SKILL_DIR/scripts/workflow_builder.py" check --workspace /approved/project/workflow
python "$SKILL_DIR/scripts/workflow_builder.py" export \
  --workspace /approved/project/workflow --destination /approved/project/skill-exports
```

Child packages retain the decomposition, diagram, and code unchanged, adding
SKILL.md, onboarding, runtime requirements, input examples, brand metadata/assets,
UI metadata, a review checklist, hashes, and a ZIP. Private goal/source/evaluation
working notes and workspace configuration are not copied. Essential curated facts
must be included in the decomposition. The standalone Step 6 exporter remains
available for already-completed three-artifact workflows.

## Branding

Explicit customer profile wins; otherwise the CompleteTech logo and palette are
a starter example. `--brand-profile` supplies a profile; `--unbranded` opts out.
Onboarding records and snapshots the choice. Invalid profiles fail rather than
silently replacing customer identity. A changed brand snapshot requires new branding
onboarding. See [BRANDING.md](BRANDING.md) and [BRAND_ASSETS.md](BRAND_ASSETS.md).

Identity, palette, logo, tagline, and other profile fields travel to the child skill.
This does not automatically rewrite a generated renderer to apply colors or logos.
CompleteTech is the toolkit author, not an invented customer or output owner.

## Library alignment and boundaries

Like the discovery, delivery, contract, orchestrator, and ledger examples, this skill
separates purpose, onboarding, permissions, references, examples, quality checks,
branding, and downstream handoff. See [the routing table](references/use-case-decision-table.md)
and [handoff contract](references/skill-library-handoff.md). It does not generate
commercial approval, legal agreements, invoices, public proof, or security signoff.

## Quality and examples

```bash
python -m unittest discover -s tests -v
python scripts/validate_quality.py
python scripts/package_builder_skill.py --destination outputs/builder-release
python outputs/builder-release/agentic-workflow-builder-skill/scripts/validate_quality.py --installed
```

A [synthetic intake](examples/builder/intake.json) and
[small source workflow](examples/workflow/workflow.py) support the offline tests.
The installed-package smoke test starts from an extracted ZIP in another directory,
onboards, resumes, checks, and exports a child skill without an API key or source
repository dependencies. The test does not execute the generated domain workflow.

**Passing structural checks is not domain validation or approval to run code.**
See [QUALITY.md](QUALITY.md) and [evaluation guidance](references/evaluation.md).

## Optional notebooks

In the repository checkout only, `python scripts/build_skill_notebook.py` generates
`build_ai_workflows_in_6_steps.ipynb`. The original
`build_ai_workflows_in_5_steps.ipynb` and `create_workflow_skill.ipynb` are retained.
These lesson/provider tools are intentionally excluded from the minimal installed
builder distribution. Historical model/pricing examples are not current guarantees.

## Distribution, network, and license

The explicit distribution inventory excludes .env files, user outputs, chat history,
raw customer sources, notebook SDKs, and development caches. See
[CLAW_HUB_PUBLISHING.md](CLAW_HUB_PUBLISHING.md) for the manual registry handoff.

The bundled onboarding/check/export helpers are offline. The agent host itself may
process prompts remotely according to its own policy. No automatic generated-code
execution, dependency install, network call, background service, or registry publish
occurs. Read code and approve those actions separately when needed.

Code and documentation: MIT, [LICENSE](LICENSE). Brand rights are separate.
Method and teaching integration: © 2026 CompleteTech LLC.
External formats and repository exemplars are attributed in [sources](references/sources.md).
