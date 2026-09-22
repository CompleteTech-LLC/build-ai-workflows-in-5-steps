"""Offline exporter, privacy-boundary, integrity, and notebook regression tests."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts import create_workflow_skill as exporter
from scripts.build_skill_notebook import combined_notebook, notebook, step_six_cells
from scripts.validate_skill import check_workflow, validate_skill

ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.inputs = self.base / "inputs"
        self.inputs.mkdir()
        for name in exporter.ARTIFACTS:
            (self.inputs / name).write_bytes((ROOT / "examples/workflow" / name).read_bytes())
        self.destination = self.base / "exports"
        # Isolated asset fixture; tests never depend on external network or real art.
        self.repository = self.base / "repository"
        (self.repository / "assets").mkdir(parents=True)
        (self.repository / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
        profile = json.loads((ROOT / "assets/brand-profile.json").read_text())
        (self.repository / "assets/brand-profile.json").write_text(json.dumps(profile))
        (self.repository / "assets/completetech_logo.jpg").write_bytes(b"\xff\xd8\xfftest-logo-fixture")
        self.patch = patch.object(exporter, "ROOT", self.repository)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def build(self, **kwargs):
        options = dict(name="text-summary", title="Text Summary", description="Count words in a supplied text file. Use for text-summary tasks.")
        options.update(kwargs)
        return exporter.build_skill(self.inputs, self.destination, **options)

    def test_complete_package_and_unmodified_artifacts(self):
        result = self.build()
        root = Path(result["directory"])
        self.assertEqual(result["branding"], "completetech-starter")
        self.assertFalse(result["workflow_executed"])
        self.assertEqual(result["review_status"], "unreviewed")
        self.assertEqual(result["files_checked"], 14)
        for source, dest in exporter.ARTIFACTS.items():
            self.assertEqual((root / dest).read_bytes(), (self.inputs / source).read_bytes())
        with zipfile.ZipFile(result["archive"]) as z:
            self.assertTrue(all(n.startswith("text-summary/") for n in z.namelist()))
            self.assertEqual(z.read("text-summary/SKILL.md"), (root / "SKILL.md").read_bytes())
        validate_skill(root)

    def test_standalone_validator_needs_no_repository_or_dependencies(self):
        result = self.build()
        root = Path(result["directory"])
        run = subprocess.run([sys.executable, "scripts/validate_skill.py", "."],
                             cwd=root, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertFalse(json.loads(run.stdout)["workflow_executed"])

    def test_deterministic_archive(self):
        a = Path(self.build()["archive"]).read_bytes()
        self.destination = self.base / "second-export"
        b = Path(self.build()["archive"]).read_bytes()
        self.assertEqual(a, b)

    def test_no_generated_code_execution(self):
        sentinel = self.base / "must-not-exist"
        code = f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n"
        code += "def run_workflow(source_path, target_dashboard_path, ai=None):\n    return {}\n"
        (self.inputs / "workflow.py").write_text(code)
        self.build()
        self.assertFalse(sentinel.exists())

    def test_excludes_raw_inputs_and_environment(self):
        for name in (".env", "source.pdf", "target.png", "history.json", "other.py"):
            (self.inputs / name).write_text("PRIVATE DO NOT COPY")
        result = self.build()
        with zipfile.ZipFile(result["archive"]) as z:
            self.assertFalse(any(b"PRIVATE DO NOT COPY" in z.read(n) for n in z.namelist()))

    def test_custom_brand_preserved_without_starter_identity(self):
        brand = {"schema_version": 1, "version": "2.0", "name": "Customer Ltd",
                 "colors": {"accent": "#123456"}, "voice": "Plain and friendly"}
        (self.inputs / "brand-profile.json").write_text(json.dumps(brand))
        result = self.build()
        root = Path(result["directory"])
        self.assertEqual(result["branding"], "custom")
        self.assertEqual(json.loads((root / "assets/brand-profile.json").read_text()), brand)
        self.assertFalse(list((root / "assets").glob("logo.*")))
        self.assertNotIn("CompleteTech LLC", (root / "agents/openai.yaml").read_text())

    def test_explicit_brand_wins(self):
        (self.inputs / "brand-profile.json").write_text("malformed")
        profile = self.base / "brand.json"
        profile.write_text(json.dumps({"schema_version": 1, "version": "1", "name": "Explicit Brand", "colors": {"accent": "#AA1122"}}))
        result = self.build(brand_profile=profile)
        actual = json.loads((Path(result["directory"]) / "assets/brand-profile.json").read_text())
        self.assertEqual(actual["name"], "Explicit Brand")

    def test_unbranded_is_explicit(self):
        result = self.build(unbranded=True)
        root = Path(result["directory"])
        self.assertEqual(result["branding"], "unbranded")
        self.assertNotIn("brand_color", (root / "agents/openai.yaml").read_text())
        self.assertNotIn("Output brand:", (root / "README.md").read_text())

    def test_conflicting_brand_modes(self):
        with self.assertRaises(ValueError):
            self.build(unbranded=True, brand_profile=Path("anything.json"))

    def test_invalid_brand_never_falls_back(self):
        for value in ("{}", "not json", "[]", '{"schema_version":99}'):
            with self.subTest(value=value):
                (self.inputs / "brand-profile.json").write_text(value)
                with self.assertRaises((ValueError, TypeError)):
                    self.build()
                self.assertFalse(self.destination.exists())

    def test_missing_explicit_brand_fails(self):
        with self.assertRaises(ValueError):
            self.build(brand_profile=self.base / "missing.json")

    def test_bad_colors_rejected(self):
        brand = {"schema_version": 1, "version": "1", "name": "Brand", "colors": {"accent": "red"}}
        (self.inputs / "brand-profile.json").write_text(json.dumps(brand))
        with self.assertRaises(ValueError):
            self.build()

    def test_logo_traversal_absolute_remote_and_svg_rejected(self):
        for logo in ("../outside.png", "/tmp/logo.png", "https://example.com/logo.png", "logo.svg", "C:\\logo.png"):
            with self.subTest(logo=logo):
                profile = {"schema_version": 1, "version": "1", "name": "Brand", "colors": {"accent": "#123456"}, "logo": logo}
                (self.inputs / "brand-profile.json").write_text(json.dumps(profile))
                with self.assertRaises(ValueError):
                    self.build()

    def test_logo_missing_or_wrong_magic_rejected(self):
        (self.repository / "assets/completetech_logo.jpg").write_text("not a JPEG")
        with self.assertRaises(ValueError):
            self.build()
        (self.repository / "assets/completetech_logo.jpg").unlink()
        with self.assertRaises(ValueError):
            self.build()

    def test_missing_prerequisites(self):
        for name in exporter.ARTIFACTS:
            with self.subTest(name=name):
                path = self.inputs / name
                data = path.read_bytes()
                path.unlink()
                with self.assertRaises(ValueError):
                    self.build()
                path.write_bytes(data)
        self.assertFalse(self.destination.exists())

    def test_empty_and_oversized_input_rejected(self):
        path = self.inputs / "decomposition.md"
        for data in (b"", b"a" * (2 * 1024 * 1024 + 1)):
            path.write_bytes(data)
            with self.assertRaises(ValueError):
                self.build()

    def test_malformed_workflow_and_wrong_signature(self):
        for text in ("def :\n", "x = 1\n", "async def run_workflow(source_path, target_dashboard_path, ai=None): pass",
                     "def run_workflow(a,b): pass", "def run_workflow(source_path,target_dashboard_path,ai): pass",
                     "def run_workflow(source_path,target_dashboard_path,ai=None,extra=1): pass"):
            with self.subTest(text=text), self.assertRaises((ValueError, SyntaxError)):
                check_workflow(text)

    def test_unsafe_names_and_metadata_rejected(self):
        for name in ("../outside", "BadName", "bad--name", "-bad", "bad-", "a" * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.build(name=name)
        with self.assertRaises(ValueError):
            self.build(description="first\nname: injected")
        with self.assertRaises(ValueError):
            self.build(description="a" * 1025)

    def test_unicode_and_quoted_metadata(self):
        result = self.build(title='Café: "Review"', description='Use for résumé text: "count words".')
        validate_skill(Path(result["directory"]))

    def test_existing_output_is_not_overwritten(self):
        result = self.build()
        archive = Path(result["archive"])
        before = archive.read_bytes()
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(before, archive.read_bytes())

    def test_existing_archive_is_not_overwritten(self):
        self.destination.mkdir()
        archive = self.destination / "text-summary.zip"
        archive.write_bytes(b"KEEP")
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(archive.read_bytes(), b"KEEP")
        self.assertFalse((self.destination / "text-summary").exists())

    def test_credentials_rejected_without_echo(self):
        secret = "sk-" + "x" * 32
        (self.inputs / "decomposition.md").write_text("leaked " + secret)
        with self.assertRaises(ValueError) as context:
            self.build()
        self.assertNotIn(secret, str(context.exception))
        self.assertFalse(self.destination.exists())

    def test_tampering_and_unlisted_files_detected(self):
        result = self.build()
        root = Path(result["directory"])
        file = root / "references/decomposition.md"
        before = file.read_bytes()
        file.write_text("changed")
        with self.assertRaises(ValueError):
            validate_skill(root)
        file.write_bytes(before)
        (root / "extra.txt").write_text("unlisted")
        with self.assertRaises(ValueError):
            validate_skill(root)

    def test_manifest_traversal_detected(self):
        result = self.build()
        root = Path(result["directory"])
        path = root / "skill-package.json"
        manifest = json.loads(path.read_text())
        manifest["files"]["../outside"] = "0" * 64
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            validate_skill(root)

    @unittest.skipIf(sys.platform == "win32", "Symlink creation may require elevation")
    def test_input_output_and_dangling_brand_symlinks_rejected(self):
        target = self.inputs / "workflow.py"
        target.unlink()
        target.symlink_to(ROOT / "examples/workflow/workflow.py")
        with self.assertRaises(ValueError):
            self.build()
        target.unlink()
        target.write_bytes((ROOT / "examples/workflow/workflow.py").read_bytes())
        (self.inputs / "brand-profile.json").symlink_to(self.base / "missing")
        with self.assertRaises(ValueError):
            self.build()
        (self.inputs / "brand-profile.json").unlink()
        actual = self.base / "actual"
        actual.mkdir()
        self.destination.symlink_to(actual, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.build()


class NotebookTests(unittest.TestCase):
    def test_capstone_is_reproducible_and_unexecuted(self):
        expected = notebook(step_six_cells())
        actual = json.loads((ROOT / "create_workflow_skill.ipynb").read_text())
        self.assertEqual(actual, expected)
        self.assertEqual(len({c["id"] for c in actual["cells"]}), len(actual["cells"]))
        for c in actual["cells"]:
            if c["cell_type"] == "code":
                self.assertEqual(c["outputs"], [])
                self.assertIsNone(c["execution_count"])
                compile("".join(c["source"]), "notebook cell", "exec")

    def test_combined_inserts_before_recap_and_keeps_prior_code(self):
        original = {"cells": [
            {"cell_type": "markdown", "source": ["# Build AI Workflows in 5 Steps\n# Step 5 of 5\n"]},
            {"cell_type": "code", "source": ["print('unchanged')"], "outputs": [], "execution_count": None},
            {"cell_type": "markdown", "source": ["# What you built\n\n## Your next move"]}]}
        before = copy.deepcopy(original)
        result = combined_notebook(original)
        self.assertEqual(original, before)
        self.assertEqual(result["cells"][1]["source"], original["cells"][1]["source"])
        self.assertIn("Step 6 of 6", "".join(result["cells"][2]["source"]))
        self.assertIn("# What you built", "".join(result["cells"][-1]["source"]))
        self.assertNotIn("of 5", "".join(result["cells"][0]["source"]))

    def test_upstream_layout_drift_fails(self):
        with self.assertRaises(ValueError):
            combined_notebook({"cells": []})


if __name__ == "__main__":
    unittest.main()
