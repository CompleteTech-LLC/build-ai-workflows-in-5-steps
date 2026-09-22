# Workflow Builder Onboarding

## 1. Choose a route

New workflow: use this skill's six-step process. Existing design: inspect artifacts
and resume at the first missing or invalid stage. Completed Step 3–5 outputs: the
standalone create_workflow_skill.py exporter still works; use the builder path to
add explicit onboarding, goal/source notes, and evaluation planning. Notebook
learner: the original lesson remains in the repository, separate from the installed
skill. Do not force notebooks or a new provider key on someone using an agent host.

## 2. Disclose the local workspace

State where files will be written before first initialization. Onboarding retains
verified intake facts, source references (not source contents), constraints, and a
brand profile/logo snapshot in that directory. Subsequent design artifacts are
written there. Nothing is stored globally, transmitted by the helpers, scanned from
accounts, or scheduled. Agent-host prompt processing is governed by the host.
Keep the workspace out of public repositories; brand and source references may be
identifying even without raw customer documents.

## 3. Reuse known facts, then fill gaps

Inspect the current request, supplied files, previous handoff, and existing
workflow-builder.json first. Use [the interview guide](references/onboarding.md).
Ask only missing questions. Capture facts in the exact fields of
[workflow-intake.json](templates/workflow-intake.json); do not add credential fields.
The agent can fill the JSON from chat answers so the user need not edit JSON.

Minimum packaging facts: workflow name/title/description, desired outcome, owner,
source references, target reference, and success criteria. Constraints and exclusions
can be empty only when genuinely absent; clarify consequential omissions. A target
may be a written specification instead of an image. Record host, repetition cadence,
cost/latency limits, and data-retention requirements in constraints when relevant.

## 4. Choose branding once

Use `--brand-profile /approved/brand/brand-profile.json` for customer branding.
Without an explicit profile, the CompleteTech starter is used and disclosed, as
requested for this toolkit. `--unbranded` is the explicit opt-out. Invalid profiles
never fall back. See [BRANDING.md](BRANDING.md) for required fields and local logo rules.
The profile and selected asset are copied into the new workspace with hashes.
Later exports use that snapshot, not a silently changed global default.

## 5. Initialize or resume

Use an absolute SKILL_DIR pointing to the directory containing SKILL.md.

```bash
python "$SKILL_DIR/scripts/workflow_builder.py" template
python "$SKILL_DIR/scripts/workflow_builder.py" init \
  --workspace /approved/project/workflow --intake /approved/project/intake.json
python "$SKILL_DIR/scripts/workflow_builder.py" status --workspace /approved/project/workflow
```

No intake argument creates a draft with explicit missing facts. Initialization
creates no generated Python or fictional results. Repeating init refuses overwrite;
status reads saved facts without re-questioning the user. Edit unanswered intake
fields in workflow-builder.json using verified answers. Unknown schema versions,
unsafe types, possible secrets, invalid slugs, and changed brand snapshots fail.
For a new brand/version, choose a new workspace and deliberately reuse reviewed
facts. Never delete the existing workspace to make a command pass.

## 6. First useful result

After onboarding, author goal.md and source-intake.md from actual evidence, then
follow [SKILL.md](SKILL.md). Draft-only work may continue with unresolved facts;
export is blocked until required facts and artifacts are present. Run check before
export. Its output reports structural readiness, not semantic completeness or safety.

## 7. Review, installation, and removal

Review code before import. Obtain execution permission and test in isolation before
using live inputs. Install the builder by manually copying the packaged folder to
one supported host location. Install its generated child skill only after separate
review. This workflow does not change host configuration or install dependencies.

To remove an installation, manually remove only the known installed skill folder.
Retained project workspaces are separate; archive or delete only the selected ones
when requested. No scheduler, daemon, hidden profile, or service must be removed.
