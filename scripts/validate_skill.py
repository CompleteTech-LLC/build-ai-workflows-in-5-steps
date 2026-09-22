#!/usr/bin/env python3
"""Validate this lesson's exported skill contract, without importing workflow code."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
MAX_TEXT = 2 * 1024 * 1024
SECRET = re.compile(
    r"(?:sk-(?:ant-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{30,}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"(?i:(?:api[_-]?key|password|secret|access[_-]?token)\s*[=:]\s*"
    r"[\"'][^\"'\s]{12,}[\"']))"
)
REQUIRED = {
    "SKILL.md", "README.md", "ONBOARDING.md", "LICENSE",
    "scripts/workflow.py", "scripts/validate_skill.py",
    "references/decomposition.md", "references/workflow.mmd",
    "references/review-checklist.md", "assets/brand-profile.json",
    "agents/openai.yaml", "requirements.txt", "inputs.example.json",
}


def no_symlinks(path: Path) -> None:
    """Reject symlinks at the leaf and in existing ancestor components."""
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Symlinks are not supported for package inputs or outputs")


def clean_text(data: bytes, label: str) -> str:
    if not data or len(data) > MAX_TEXT:
        raise ValueError(f"{label}: expected 1..{MAX_TEXT} bytes")
    text = data.decode("utf-8")
    if "\x00" in text or SECRET.search(text):
        raise ValueError(f"{label}: possible credential or NUL byte; review locally")
    return text


def check_workflow(text: str) -> None:
    """Check syntax and the Step 5 entrypoint, never execute generated Python."""
    tree = ast.parse(text, filename="workflow.py")
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == "run_workflow"]
    if len(functions) != 1:
        raise ValueError("workflow.py must define exactly one synchronous run_workflow")
    args = functions[0].args
    if ([a.arg for a in args.args] != ["source_path", "target_dashboard_path", "ai"]
            or args.posonlyargs or args.kwonlyargs or args.vararg or args.kwarg
            or len(args.defaults) != 1 or not isinstance(args.defaults[0], ast.Constant)
            or args.defaults[0].value is not None):
        raise ValueError("Expected run_workflow(source_path, target_dashboard_path, ai=None)")


def safe_relative(value: str) -> bool:
    p = PurePosixPath(value)
    return bool(value) and not p.is_absolute() and all(
        part not in {".", ".."} for part in value.split("/")) and "\\" not in value and ":" not in value


def validate_skill(root: Path) -> dict:
    root = Path(root).absolute()
    no_symlinks(root)
    if not root.is_dir():
        raise ValueError("Skill directory is missing")
    manifest_path = root / "skill-package.json"
    no_symlinks(manifest_path)
    manifest = json.loads(clean_text(manifest_path.read_bytes(), "manifest"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported skill package schema")
    name = manifest.get("name", "")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64 or root.name != name:
        raise ValueError("Skill name must match its directory and use 1..64 lowercase slug characters")
    inventory = manifest.get("files")
    if not isinstance(inventory, dict) or not REQUIRED.issubset(inventory):
        raise ValueError("Package inventory is missing required files")
    actual = set()
    for p in root.rglob("*"):
        no_symlinks(p)
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
        elif not p.is_dir():
            raise ValueError("Package contains a non-regular file")
    if actual != set(inventory) | {"skill-package.json"}:
        raise ValueError("Package contains missing or unlisted files")
    for relative, expected in inventory.items():
        if not isinstance(relative, str) or not safe_relative(relative):
            raise ValueError("Unsafe inventory path")
        data = (root / relative).read_bytes()
        if not isinstance(expected, str) or hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Hash mismatch: {relative}")
        if Path(relative).suffix not in {".png", ".jpg", ".jpeg"}:
            clean_text(data, relative)
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    parts = skill.split("---\n", 2)
    if len(parts) != 3 or parts[0] or not parts[2].strip():
        raise ValueError("SKILL.md needs frontmatter and instructions")
    # The exporter uses a deliberate flat subset of YAML: JSON-quoted scalar values.
    metadata = {}
    for line in parts[1].splitlines():
        key, separator, value = line.partition(": ")
        if not separator or key in metadata:
            raise ValueError("Invalid or duplicate frontmatter field")
        metadata[key] = json.loads(value)
    description = metadata.get("description")
    if (metadata.get("name") != name or not isinstance(description, str)
            or not 1 <= len(description.strip()) <= 1024):
        raise ValueError("Invalid skill name or description")
    check_workflow((root / "scripts/workflow.py").read_text(encoding="utf-8"))
    return {"name": name, "files_checked": len(inventory), "syntax_checked": True,
            "workflow_executed": False, "review_status": "unreviewed"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_skill(args.skill), indent=2))
        return 0
    except (OSError, ValueError, SyntaxError, TypeError) as exc:
        parser.exit(2, f"Validation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
