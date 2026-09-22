#!/usr/bin/env python3
"""Validate the workflow-BUILDER skill, not a generated workflow or its quality."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
if __package__:
    from .validate_skill import clean_text, no_symlinks, safe_relative
else:
    from validate_skill import clean_text, no_symlinks, safe_relative

NAME = "agentic-workflow-builder-skill"
VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[1]
# Explicit inventory: never glob a user's workspace into a published skill.
FILES = (
    "SKILL.md", "README.md", "ONBOARDING.md", "LICENSE", "BRANDING.md",
    "BRAND_ASSETS.md", "QUALITY.md", "CLAW_HUB_PUBLISHING.md",
    "agents/openai.yaml", "assets/brand-profile.json", "assets/completetech_logo.jpg",
    "assets/diagrams/workflow.mmd", "templates/workflow-intake.json",
    "references/six-step-method.md", "references/onboarding.md",
    "references/skill-library-handoff.md", "references/use-case-decision-table.md",
    "references/evaluation.md", "references/sources.md",
    "examples/builder/intake.json", "examples/builder/goal.md",
    "examples/builder/source-intake.md", "examples/builder/evaluation-plan.md",
    "examples/workflow/decomposition.md", "examples/workflow/workflow.mmd",
    "examples/workflow/workflow.py", "scripts/workflow_builder.py",
    "scripts/create_workflow_skill.py", "scripts/validate_skill.py",
    "scripts/validate_quality.py", "scripts/package_builder_skill.py",
)


def frontmatter(text: str) -> dict:
    parts = text.split("---\n", 2)
    if len(parts) != 3 or parts[0] or not parts[2].strip():
        raise ValueError("SKILL.md requires frontmatter and instructions")
    result = {}
    for line in parts[1].splitlines():
        key, sep, value = line.partition(": ")
        if not sep or key in result:
            raise ValueError("Invalid frontmatter")
        result[key] = json.loads(value)
    if result.get("name") != NAME or not isinstance(result.get("description"), str):
        raise ValueError("Incorrect builder skill metadata")
    if not 1 <= len(result["description"].strip()) <= 1024:
        raise ValueError("Description must be 1..1024 characters")
    if not isinstance(result.get("metadata"), dict) or result["metadata"].get("version") != VERSION:
        raise ValueError("Missing builder version")
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in result["metadata"].items()):
        raise ValueError("Metadata must map strings to strings")
    if not 1 <= len(result.get("compatibility", "")) <= 500:
        raise ValueError("Invalid compatibility text")
    if len(text.splitlines()) > 500:
        raise ValueError("Move long instructions into references")
    return result


def validate(root: Path = ROOT, installed: bool = False) -> dict:
    root = Path(root).absolute()
    no_symlinks(root)
    inventory, links = {}, 0
    for relative in FILES:
        if not safe_relative(relative):
            raise ValueError("Unsafe distribution path")
        p = root / relative
        no_symlinks(p)
        if not p.is_file() or p.stat().st_size > 2 * 1024 * 1024:
            raise ValueError(f"Missing or oversized skill resource: {relative}")
        data = p.read_bytes()
        inventory[relative] = hashlib.sha256(data).hexdigest()
        if relative.endswith(".jpg"):
            if not data.startswith(b"\xff\xd8\xff"):
                raise ValueError("Expected the existing JPEG logo")
            continue
        text = clean_text(data, relative)
        if relative.endswith(".py"):
            ast.parse(text, filename=relative)
        if relative.endswith(".json"):
            json.loads(text)
        if relative.endswith(".md"):
            targets = re.findall(r"\]\(([^)]+)\)", text) + re.findall(r'<img[^>]+src="([^"]+)"', text)
            for target in targets:
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0]
                resolved = (p.parent / target).resolve()
                if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                    raise ValueError(f"Broken or escaping local link in {relative}: {target}")
                if resolved.relative_to(root.resolve()).as_posix() not in FILES:
                    raise ValueError(f"Linked file is absent from distribution: {target}")
                links += 1
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    frontmatter(skill)
    if re.findall(r"^## Step ([1-6])\b", skill, re.MULTILINE) != list("123456"):
        raise ValueError("SKILL.md must contain all six ordered steps")
    for section in ("Onboarding", "Runtime Permissions", "Network Boundary", "Handoff"):
        if f"## {section}" not in skill:
            raise ValueError(f"Missing operating section: {section}")
    if installed:
        if root.name != NAME:
            raise ValueError("Installed directory must match the skill name")
        manifest_path = root / "builder-package.json"
        no_symlinks(manifest_path)
        if not manifest_path.is_file() or manifest_path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Missing or oversized builder package manifest")
        manifest = json.loads(clean_text(manifest_path.read_bytes(), "builder-package.json"))
        if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1
                or manifest.get("name") != NAME or manifest.get("version") != VERSION
                or manifest.get("files") != inventory):
            raise ValueError("Builder inventory or metadata changed")
        actual = set()
        for p in root.rglob("*"):
            no_symlinks(p)
            if p.is_file():
                actual.add(p.relative_to(root).as_posix())
            elif not p.is_dir():
                raise ValueError("Non-regular installed resource")
        if actual != set(FILES) | {"builder-package.json"}:
            raise ValueError("Installed package contains missing or unlisted files")
    return {"name": NAME, "version": VERSION, "files": inventory,
            "local_links_checked": links, "validation": "structure-only",
            "workflow_executed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--installed", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, args.installed), indent=2))
        return 0
    except (OSError, ValueError, SyntaxError, TypeError) as exc:
        parser.exit(2, f"Builder skill validation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
