#!/usr/bin/env python3
"""Onboard, inspect, and export six-step workflow projects without executing them."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
if __package__:
    from .validate_skill import NAME, check_workflow, clean_text, no_symlinks
else:
    from validate_skill import NAME, check_workflow, clean_text, no_symlinks

ROOT = Path(__file__).resolve().parents[1]
STATE = "workflow-builder.json"
TEXT_FIELDS = ("name", "title", "description", "outcome", "owner", "target_ref")
LIST_FIELDS = ("source_refs", "success_criteria", "excluded_uses", "constraints")
FIELDS = set(TEXT_FIELDS + LIST_FIELDS + ("network_policy",))
ARTIFACTS = ("goal.md", "source-intake.md", "decomposition.md", "workflow.mmd",
             "workflow.py", "evaluation-plan.md")


def exporter():
    """Import the trusted packager, never a project's generated workflow module."""
    if __package__:
        from . import create_workflow_skill
    else:
        import create_workflow_skill
    return create_workflow_skill


def read(path: Path) -> bytes:
    no_symlinks(path)
    if not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError(f"Expected a regular file of at most 2 MiB: {path.name}")
    data = path.read_bytes()
    clean_text(data, path.name)
    return data


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_intake(value: object) -> dict:
    """Validate types; blank facts remain unanswered rather than being invented."""
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("Intake must have exactly the fields in templates/workflow-intake.json")
    clean_text(encoded(value), "intake")
    for key in TEXT_FIELDS:
        v = value[key]
        limit = 64 if key == "name" else 120 if key == "title" else 1024
        if (not isinstance(v, str) or len(v) > limit
                or any(ord(c) < 32 or ord(c) == 127 for c in v)):
            raise ValueError(f"Invalid single-line intake field: {key}")
    if value["name"] and not NAME.fullmatch(value["name"]):
        raise ValueError("Workflow name must be a lowercase hyphenated slug")
    for key in LIST_FIELDS:
        if (not isinstance(value[key], list) or len(value[key]) > 100
                or any(not isinstance(v, str) or not v.strip() or len(v) > 2000
                       or any(ord(c) < 32 or ord(c) == 127 for c in v) for v in value[key])):
            raise ValueError(f"Invalid list of single-line facts: {key}")
    if value["network_policy"] not in {"none", "approval-required"}:
        raise ValueError("network_policy must be none or approval-required; it is not authorization")
    return value


def initialize(workspace: Path, intake_path: Path | None = None,
               brand_profile: Path | None = None, unbranded: bool = False) -> dict:
    workspace = Path(workspace).absolute()
    no_symlinks(workspace)
    if workspace.exists():
        raise FileExistsError("Workspace exists; use status to resume without overwriting onboarding")
    intake = validate_intake(json.loads(read(intake_path or ROOT / "templates/workflow-intake.json")))
    brand, logos, origin = exporter().load_brand(workspace, brand_profile, unbranded)
    brand["selection_origin"] = origin
    payload = {"brand-profile.json": encoded(brand), **logos}
    state = {"schema_version": 1, "intake": intake, "brand_mode": origin,
             "brand_snapshot": {p: digest(b) for p, b in payload.items()},
             "execution_approved": False, "publication_approved": False}
    payload[STATE] = encoded(state)
    payload["WORKSPACE.md"] = (
        "# Workflow design workspace\n\n"
        "Resume with workflow_builder.py status --workspace <this directory>.\n"
        "Fill missing intake facts in workflow-builder.json from verified user input.\n"
        "Do not put credentials or raw source contents in configuration.\n"
        "Author goal.md, source-intake.md, decomposition.md, workflow.mmd, workflow.py,\n"
        "and evaluation-plan.md using the skill's six-step guide.\n"
        "The helper never reads source_refs or executes generated code.\n"
        "Approval flags are informational, not permission grants.\n"
        "Brand snapshots are immutable: use a new workspace for a changed brand.\n"
    ).encode()
    workspace.parent.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(mode=0o700)
    try:
        for relative, data in payload.items():
            path = workspace / relative
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with path.open("xb") as f:
                f.write(data)
            path.chmod(0o600)
    except Exception:
        shutil.rmtree(workspace)
        raise
    return inspect(workspace)


def inspect(workspace: Path, require_complete: bool = False) -> dict:
    workspace = Path(workspace).absolute()
    no_symlinks(workspace)
    state = json.loads(read(workspace / STATE))
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        raise ValueError("Unsupported workspace state")
    intake = validate_intake(state.get("intake"))
    mode = state.get("brand_mode")
    if mode not in {"unbranded", "custom", "completetech-starter"}:
        raise ValueError("Invalid brand mode")
    snapshot = state.get("brand_snapshot")
    if not isinstance(snapshot, dict) or "brand-profile.json" not in snapshot:
        raise ValueError("Missing brand snapshot")
    permitted = {"brand-profile.json", "assets/logo.png", "assets/logo.jpg", "assets/logo.jpeg"}
    if not set(snapshot).issubset(permitted):
        raise ValueError("Unsafe brand snapshot path")
    for relative, expected in snapshot.items():
        path = workspace / relative
        no_symlinks(path)
        limit = 2 * 1024 * 1024 if relative.endswith(".json") else 10 * 1024 * 1024
        if not path.is_file() or path.stat().st_size > limit or digest(path.read_bytes()) != expected:
            raise ValueError("Brand snapshot changed or is missing; re-onboard branding in a new workspace")
    missing_facts = [k for k in TEXT_FIELDS if not intake[k].strip()]
    missing_facts += [k for k in ("source_refs", "success_criteria") if not intake[k]]
    present, missing = {}, []
    for name in ARTIFACTS:
        path = workspace / name
        no_symlinks(path)
        if not path.exists():
            missing.append(name)
        else:
            data = read(path)
            if name == "workflow.py":
                check_workflow(data.decode())
            present[name] = digest(data)
    if require_complete and (missing_facts or missing):
        raise ValueError("Not ready to export. Missing intake: " + ", ".join(missing_facts)
                         + "; missing artifacts: " + ", ".join(missing))
    return {"workspace": str(workspace), "intake": intake, "brand_mode": mode,
            "missing_facts": missing_facts, "missing_artifacts": missing,
            "artifact_sha256": present, "ready_to_package": not (missing_facts or missing),
            "workflow_executed": False, "domain_evaluation": "not_performed_by_helper"}


def export(workspace: Path, destination: Path) -> dict:
    report = inspect(workspace, require_complete=True)
    intake = report["intake"]
    unbranded = report["brand_mode"] == "unbranded"
    result = exporter().build_skill(Path(workspace), Path(destination), name=intake["name"],
        title=intake["title"], description=intake["description"], unbranded=unbranded,
        brand_profile=None if unbranded else Path(workspace) / "brand-profile.json")
    return {**result, "onboarding_brand_origin": report["brand_mode"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("template", help="Print blank intake JSON; no files are written")
    init = commands.add_parser("init", help="Create a new local onboarding workspace")
    init.add_argument("--workspace", type=Path, required=True)
    init.add_argument("--intake", type=Path)
    branding = init.add_mutually_exclusive_group()
    branding.add_argument("--brand-profile", type=Path)
    branding.add_argument("--unbranded", action="store_true")
    for command in ("status", "check", "export"):
        sub = commands.add_parser(command)
        sub.add_argument("--workspace", type=Path, required=True)
        if command == "export":
            sub.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "template":
            result = json.loads(read(ROOT / "templates/workflow-intake.json"))
        elif args.command == "init":
            result = initialize(args.workspace, args.intake, args.brand_profile, args.unbranded)
        elif args.command == "export":
            result = export(args.workspace, args.destination)
        else:
            result = inspect(args.workspace, require_complete=args.command == "check")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, SyntaxError, TypeError, KeyError) as exc:
        parser.exit(2, f"Workflow builder: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
