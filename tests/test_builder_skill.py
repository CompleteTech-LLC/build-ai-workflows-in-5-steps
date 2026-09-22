"""Builder onboarding, distribution integrity, and relocated installation tests."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
from scripts import workflow_builder as builder
from scripts.package_builder_skill import package
from scripts.validate_quality import FILES, NAME, ROOT, frontmatter, validate


class IntakeTests(unittest.TestCase):
    def blank(self):
        return json.loads((ROOT / "templates/workflow-intake.json").read_text())

    def test_blank_template_is_a_valid_incomplete_draft(self):
        self.assertEqual(builder.validate_intake(self.blank()), self.blank())

    def test_unknown_fields_and_wrong_root_fail(self):
        for value in ([], None, {**self.blank(), "api_key": "do-not-store"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.validate_intake(value)

    def test_wrong_field_types_fail(self):
        for key, value in (("name", 123), ("owner", []), ("source_refs", "file"),
                           ("success_criteria", [None]), ("constraints", ["a\nb"]),
                           ("network_policy", "allow-all")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                builder.validate_intake({**self.blank(), key: value})

    def test_unsafe_metadata_fails(self):
        for name in ("../outside", "BadName", "bad--name", "a" * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder.validate_intake({**self.blank(), "name": name})
        with self.assertRaises(ValueError):
            builder.validate_intake({**self.blank(), "description": "x" * 1025})

    def test_secret_is_not_echoed(self):
        token = "sk-" + "x" * 32
        with self.assertRaises(ValueError) as error:
            builder.validate_intake({**self.blank(), "outcome": token})
        self.assertNotIn(token, str(error.exception))


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.workspace = self.base / "project"
        self.intake = ROOT / "examples/builder/intake.json"

    def init(self, **kwargs):
        return builder.initialize(self.workspace, self.intake, **kwargs)

    def complete(self):
        for name in ("goal.md", "source-intake.md", "evaluation-plan.md"):
            shutil.copyfile(ROOT / "examples/builder" / name, self.workspace / name)
        for name in ("decomposition.md", "workflow.mmd", "workflow.py"):
            shutil.copyfile(ROOT / "examples/workflow" / name, self.workspace / name)

    def test_draft_initialization_reports_missing_facts(self):
        result = builder.initialize(self.workspace, unbranded=True)
        self.assertIn("owner", result["missing_facts"])
        self.assertIn("source_refs", result["missing_facts"])
        self.assertFalse(result["ready_to_package"])
        self.assertFalse((self.workspace / "workflow.py").exists())

    def test_resume_preserves_existing_facts_and_brand(self):
        first = self.init()
        before = (self.workspace / builder.STATE).read_bytes()
        result = builder.inspect(self.workspace)
        self.assertEqual(result, first)
        self.assertEqual((self.workspace / builder.STATE).read_bytes(), before)
        self.assertEqual(result["brand_mode"], "completetech-starter")
        self.assertEqual((self.workspace / "assets/logo.jpg").read_bytes(),
                         (ROOT / "assets/completetech_logo.jpg").read_bytes())

    def test_init_never_overwrites(self):
        self.init()
        before = (self.workspace / builder.STATE).read_bytes()
        with self.assertRaises(FileExistsError):
            self.init()
        self.assertEqual((self.workspace / builder.STATE).read_bytes(), before)

    def test_missing_intake_blocks_export_even_with_artifacts(self):
        builder.initialize(self.workspace, unbranded=True)
        self.complete()
        with self.assertRaises(ValueError):
            builder.export(self.workspace, self.base / "child")
        self.assertFalse((self.base / "child").exists())

    def test_missing_artifact_blocks_export(self):
        self.init(unbranded=True)
        self.complete()
        (self.workspace / "evaluation-plan.md").unlink()
        with self.assertRaises(ValueError):
            builder.export(self.workspace, self.base / "child")

    def test_complete_workspace_check_is_not_execution(self):
        self.init(unbranded=True)
        self.complete()
        result = builder.inspect(self.workspace, require_complete=True)
        self.assertTrue(result["ready_to_package"])
        self.assertFalse(result["workflow_executed"])
        self.assertEqual(len(result["artifact_sha256"]), 6)

    def test_custom_brand_is_snapshotted_without_starter_identity(self):
        profile = self.base / "brand.json"
        custom = {"schema_version": 1, "version": "2", "name": "Customer Ltd",
                  "colors": {"accent": "#123456"}, "voice": "Plain"}
        profile.write_text(json.dumps(custom))
        self.init(brand_profile=profile)
        profile.unlink()  # Resume/export uses the snapshot, not the original file.
        self.complete()
        output = builder.export(self.workspace, self.base / "child")
        brand = json.loads((Path(output["directory"]) / "assets/brand-profile.json").read_text())
        self.assertEqual(brand["name"], "Customer Ltd")
        self.assertEqual(brand["voice"], "Plain")
        self.assertEqual(output["onboarding_brand_origin"], "custom")
        self.assertNotIn("logo", brand)

    def test_unbranded_export_does_not_restore_starter(self):
        self.init(unbranded=True)
        self.complete()
        result = builder.export(self.workspace, self.base / "child")
        self.assertEqual(result["branding"], "unbranded")
        self.assertFalse(list((Path(result["directory"]) / "assets").glob("logo.*")))

    def test_brand_drift_and_unsafe_snapshot_paths_fail(self):
        self.init()
        path = self.workspace / "brand-profile.json"
        original = path.read_bytes()
        path.write_text("changed")
        with self.assertRaises(ValueError):
            builder.inspect(self.workspace)
        path.write_bytes(original)
        state_path = self.workspace / builder.STATE
        state = json.loads(state_path.read_text())
        state["brand_snapshot"]["../outside"] = "0" * 64
        state_path.write_text(json.dumps(state))
        with self.assertRaises(ValueError):
            builder.inspect(self.workspace)

    def test_source_references_are_not_automatically_read(self):
        self.init(unbranded=True)
        # The example names a source that does not exist; onboarding still only records it.
        state_path = self.workspace / builder.STATE
        state = json.loads(state_path.read_text())
        state["intake"]["source_refs"] = ["/does/not/exist/source.txt"]
        state_path.write_text(json.dumps(state))
        self.assertEqual(builder.inspect(self.workspace)["missing_facts"], [])

    def test_generated_code_is_not_executed_during_check_or_export(self):
        self.init(unbranded=True)
        self.complete()
        sentinel = self.base / "must-not-exist"
        (self.workspace / "workflow.py").write_text(
            f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('bad')\n"
            "def run_workflow(source_path, target_dashboard_path, ai=None):\n    return {}\n")
        builder.inspect(self.workspace, require_complete=True)
        builder.export(self.workspace, self.base / "child")
        self.assertFalse(sentinel.exists())

    @unittest.skipIf(sys.platform == "win32", "Symlink creation can require elevation")
    def test_symlinked_workspace_is_rejected(self):
        actual = self.base / "actual"
        actual.mkdir()
        self.workspace.symlink_to(actual, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.init()


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def run_cli(self, *args, cwd=None):
        result = subprocess.run([sys.executable, "-B", *map(str, args)],
                                cwd=cwd or self.base, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_source_quality_and_ordered_steps(self):
        report = validate(ROOT)
        self.assertEqual(report["name"], NAME)
        self.assertGreater(report["local_links_checked"], 10)
        self.assertFalse(report["workflow_executed"])

    def test_frontmatter_invalid_types_and_long_description_fail(self):
        text = (ROOT / "SKILL.md").read_text()
        with self.assertRaises(ValueError):
            frontmatter(text.replace(f'name: "{NAME}"', 'name: "wrong"'))
        parts = text.split("---\n", 2)
        lines = parts[1].splitlines()
        lines = ['description: ' + json.dumps("x" * 1025) if l.startswith("description:") else l for l in lines]
        with self.assertRaises(ValueError):
            frontmatter("---\n" + "\n".join(lines) + "\n---\n" + parts[2])

    def test_deterministic_package_and_no_overwrite(self):
        a = package(self.base / "a")
        b = package(self.base / "b")
        self.assertEqual(Path(a["archive"]).read_bytes(), Path(b["archive"]).read_bytes())
        with self.assertRaises(FileExistsError):
            package(self.base / "a")

    def test_installed_integrity_rejects_changes_and_extra_files(self):
        root = Path(package(self.base / "build")["directory"])
        validate(root, installed=True)
        path = root / "examples/builder/goal.md"
        original = path.read_bytes()
        path.write_bytes(original + b"\nchanged\n")
        with self.assertRaises(ValueError):
            validate(root, installed=True)
        path.write_bytes(original)
        (root / "extra.txt").write_text("unlisted")
        with self.assertRaises(ValueError):
            validate(root, installed=True)

    def test_allowlist_excludes_private_workspaces_and_notebooks(self):
        root = Path(package(self.base / "build")["directory"])
        (root / ".env").write_text("PRIVATE_DO_NOT_COPY")
        (root / "outputs").mkdir()
        (root / "outputs/private.txt").write_text("PRIVATE_DO_NOT_COPY")
        (root / "notebook.ipynb").write_text("PRIVATE_DO_NOT_COPY")
        repacked = package(self.base / "new", root=root)
        with zipfile.ZipFile(repacked["archive"]) as z:
            self.assertEqual(len(z.namelist()), len(FILES) + 1)
            self.assertFalse(any(b"PRIVATE_DO_NOT_COPY" in z.read(n) for n in z.namelist()))

    def test_missing_resource_or_broken_link_fails(self):
        root = Path(package(self.base / "build")["directory"])
        readme = root / "README.md"
        readme.write_text(readme.read_text() + "\n[missing](not-here.md)\n")
        with self.assertRaises(ValueError):
            validate(root)

    def test_relocated_installed_skill_can_onboard_resume_check_and_export(self):
        archive = Path(package(self.base / "build")["archive"])
        relocated = self.base / "unrelated-host" / ".agents" / "skills"
        relocated.mkdir(parents=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(relocated)  # Archive just created from the fixed local allowlist.
        skill = relocated / NAME
        self.run_cli(skill / "scripts/validate_quality.py", "--installed")
        cli = skill / "scripts/workflow_builder.py"
        workspace = self.base / "different-project" / "workflow"
        self.run_cli(cli, "init", "--workspace", workspace,
                     "--intake", skill / "examples/builder/intake.json")
        status = self.run_cli(cli, "status", "--workspace", workspace)
        self.assertEqual(status["missing_facts"], [])
        for name in ("goal.md", "source-intake.md", "evaluation-plan.md"):
            shutil.copyfile(skill / "examples/builder" / name, workspace / name)
        for name in ("decomposition.md", "workflow.mmd", "workflow.py"):
            shutil.copyfile(skill / "examples/workflow" / name, workspace / name)
        check = self.run_cli(cli, "check", "--workspace", workspace)
        self.assertTrue(check["ready_to_package"])
        result = self.run_cli(cli, "export", "--workspace", workspace,
                              "--destination", self.base / "children")
        child = Path(result["directory"])
        self.assertTrue(Path(result["archive"]).is_file())
        self.run_cli(child / "scripts/validate_skill.py", child)
        self.run_cli(skill / "scripts/validate_quality.py", "--installed")
        self.assertFalse(result["workflow_executed"])


if __name__ == "__main__":
    unittest.main()
