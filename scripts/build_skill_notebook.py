#!/usr/bin/env python3
"""Build the Step 6 continuation and, optionally, the combined six-step lesson."""
from __future__ import annotations

import argparse
import copy
import json
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cell(kind: str, text: str) -> dict:
    result = {"cell_type": kind, "metadata": {}, "source": text.strip().splitlines(keepends=True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def step_six_cells() -> list[dict]:
    return [cell("markdown", """
# Step 6 of 6 — Package the Workflow as a Skill

<img src="assets/completetech_logo.jpg" alt="CompleteTech LLC" width="180"/>

Turn the workflow you designed into a reusable **Agent Skill**, not another chat
transcript. This deterministic step makes **no AI calls**, adds **no model-token
cost**, and never imports or executes your generated workflow.

Complete Steps 1–5 in `build_ai_workflows_in_5_steps.ipynb` first, or use the combined
six-step lesson. You need `outputs/decomposition.md`, `outputs/workflow.mmd`, and
`outputs/workflow.py`. A fresh kernel is fine: Step 6 reads those saved artifacts.
Run this notebook from the repository root.

For an offline packaging demonstration, set SOURCE_OUTPUTS to
`Path("examples/workflow")`. That synthetic fixture is NOT the financial workflow.

## What the skill contains

A scoped SKILL.md; unchanged workflow code, decomposition and diagram; onboarding;
an approval/review checklist; Codex UI metadata; a versioned brand profile; a
SHA-256 file inventory; a standalone validator; and a portable single-folder ZIP.
Raw source documents, target images, API keys, chat histories, and provider SDKs
are not copied. Derived references may still contain private material: review them.
"""), cell("code", '''
from pathlib import Path

# Describe THIS workflow specifically so an agent knows when to use the skill.
SKILL_NAME = "financial-scorecard-workflow"
SKILL_TITLE = "Financial Scorecard Workflow"
SKILL_DESCRIPTION = (
    "Prepare a draft financial scorecard from a source financial pack and a target "
    "dashboard image. Use for the reviewed scorecard workflow, not tax advice or filing."
)
SOURCE_OUTPUTS = Path("outputs")
DESTINATION = Path("outputs/skills")

# Explicit profile > SOURCE_OUTPUTS/brand-profile.json > CompleteTech starter.
# Custom identity is never merged with CompleteTech's identity. Invalid profiles fail.
BRAND_PROFILE = None  # Or Path("path/to/customer/brand-profile.json")
UNBRANDED = False     # True disables output branding; do not also set BRAND_PROFILE.
'''), cell("markdown", """
## Export — packaging is not approval to execute

Review the name, description, and source artifacts before running the next cell.
The generated package remains **unreviewed**, even after validation succeeds.
Existing skill directories and ZIPs are never overwritten. For another export,
choose a new DESTINATION or SKILL_NAME; archive prior work yourself deliberately.
"""), cell("code", '''
import json
from scripts.create_workflow_skill import build_skill

skill_result = build_skill(
    SOURCE_OUTPUTS, DESTINATION,
    name=SKILL_NAME, title=SKILL_TITLE, description=SKILL_DESCRIPTION,
    brand_profile=BRAND_PROFILE, unbranded=UNBRANDED,
)
print(json.dumps(skill_result, indent=2))
print("Review ONBOARDING.md and references/review-checklist.md before installation.")
'''), cell("markdown", """
## Verify, review, then reuse

The next cell validates structure, file hashes, Python syntax, and the expected
`run_workflow(source_path, target_dashboard_path, ai=None)` signature. It **does not**
validate the workflow's domain logic or execute its code.

Read every generated artifact. Test synthetic success and failure cases in an
isolated environment only after explicit execution approval. Bring your own
approved `ai.ask(...)` adapter when the captured workflow needs judgment.

After review, manually copy the skill folder into `.agents/skills/` for Codex or
`.claude/skills/` for Claude Code. Installation and publishing are never automatic.
The CompleteTech logo/palette is a starter, not a replacement for customer identity.
Brand metadata is passed downstream; the exporter does not rewrite arbitrary Python
renderers to apply colors or logos.

See [the full Step 6 guide](docs/step-6-create-a-skill.md) and
[branding contract](BRANDING.md). Format references:
[Agent Skills](https://agentskills.io/specification),
[Codex](https://developers.openai.com/codex/skills/),
[Claude Code](https://code.claude.com/docs/en/skills).
"""), cell("code", '''
from scripts.validate_skill import validate_skill
print(json.dumps(validate_skill(Path(skill_result["directory"])), indent=2))
''')]


def notebook(cells: list[dict], metadata: dict | None = None) -> dict:
    cells = copy.deepcopy(cells)
    for index, item in enumerate(cells):
        item["id"] = f"lesson-{index:03d}"
        if item["cell_type"] == "code":
            item["execution_count"], item["outputs"] = None, []
    return {"cells": cells, "metadata": metadata or {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"}}, "nbformat": 4, "nbformat_minor": 5}


def combined_notebook(base: dict) -> dict:
    """Insert Step 6 before the original recap without changing Steps 1-5 code."""
    cells = copy.deepcopy(base["cells"])
    recaps = [i for i, c in enumerate(cells) if c["cell_type"] == "markdown"
              and "# What you built" in "".join(c["source"])]
    if len(recaps) != 1:
        raise ValueError("Expected one lesson recap; review upstream layout before rebuilding")
    for item in cells:
        if item["cell_type"] != "markdown":
            continue
        text = "".join(item["source"])
        text = text.replace("Build AI Workflows in 5 Steps", "Build AI Workflows in 6 Steps")
        text = re.sub(r"(# Step [1-5]) of 5", r"\1 of 6", text)
        if "## What you will learn" in text:
            text = text.replace("## How to use this notebook", "5. **Skill Packaging** — export the completed workflow as a reusable, branded Agent Skill (Step 6)\n\n## How to use this notebook")
        if "# What you built" in text:
            text = text.replace("## Your next move", "The sixth step also created a reviewable skill directory and ZIP under `outputs/skills/`.\nRead its ONBOARDING.md before installing or executing generated code.\n\n## Your next move")
            text = text.replace("**Run the crystallized code.** Import", "**Review before running the crystallized code.** Obtain execution approval and inspect all top-level effects before you import")
        item["source"] = text.splitlines(keepends=True)
    cells[recaps[0]:recaps[0]] = step_six_cells()
    return notebook(cells, copy.deepcopy(base.get("metadata", {})))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {path.name}: {len(value['cells'])} cells (unexecuted)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capstone-only", action="store_true", help="Do not regenerate the original or combined lesson")
    args = parser.parse_args()
    write(ROOT / "create_workflow_skill.ipynb", notebook(step_six_cells()))
    if not args.capstone_only:
        # This runs the trusted notebook BUILDER, not notebook cells or model code.
        source = runpy.run_path(str(ROOT / "scripts/build_notebook.py"))
        write(ROOT / "build_ai_workflows_in_6_steps.ipynb", combined_notebook(source["notebook"]))


if __name__ == "__main__":
    main()
