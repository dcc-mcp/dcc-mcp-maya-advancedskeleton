from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dcc_mcp_core._server.inprocess_executor import (
    clear_script_package,
    run_skill_script,
)

SCRIPTS = Path(__file__).parents[1] / "skill" / "maya-advancedskeleton" / "scripts"
COMMON_SPEC = importlib.util.spec_from_file_location(
    "_common_contract", SCRIPTS / "_common.py"
)
assert COMMON_SPEC is not None and COMMON_SPEC.loader is not None
_common = importlib.util.module_from_spec(COMMON_SPEC)
COMMON_SPEC.loader.exec_module(_common)


class CommonContractTests(unittest.TestCase):
    def test_entrypoints_load_through_runner_import_context(self):
        entrypoints = sorted(SCRIPTS.glob("*.py"))
        entrypoints.remove(SCRIPTS / "_common.py")
        before_path = list(sys.path)
        before_modules = set(sys.modules)
        with tempfile.TemporaryDirectory() as raw_dir:
            script_dir = Path(raw_dir)
            for source in SCRIPTS.glob("*.py"):
                shutil.copy2(source, script_dir / source.name)
            try:
                for entrypoint in entrypoints:
                    with self.subTest(entrypoint=entrypoint.name):
                        source = entrypoint.read_text(encoding="utf-8")
                        self.assertNotIn("sys.path.insert", source)
                        self.assertNotIn("sys.path.append", source)
                        probe = script_dir / f"_import_probe_{entrypoint.stem}.py"
                        probe.write_text(
                            f"from {entrypoint.stem} import main as entry_main\n"
                            "def main(): return callable(entry_main)\n",
                            encoding="utf-8",
                        )
                        self.assertIs(run_skill_script(str(probe), {}), True)
                        self.assertEqual(sys.path, before_path)
                        for module_name in ("_common", entrypoint.stem):
                            self.assertEqual(
                                module_name in sys.modules,
                                module_name in before_modules,
                            )
            finally:
                clear_script_package(script_dir)
        self.assertEqual(sys.path, before_path)

    def test_acceptance_arm_is_parent_first_and_root_labelled(self):
        specs = _common.validate_joint_specs(
            [
                {"name": "Root", "position": [0, 0, 0], "label": "Root"},
                {
                    "name": "Shoulder",
                    "parent": "Root",
                    "position": [0, 10, 0],
                    "label": "Shoulder",
                },
                {
                    "name": "Elbow",
                    "parent": "Shoulder",
                    "position": [5, 9, 0],
                    "label": "None",
                },
                {
                    "name": "Wrist",
                    "parent": "Elbow",
                    "position": [10, 10, 0],
                    "label": "Hand",
                },
            ]
        )
        self.assertEqual(
            [spec["name"] for spec in specs], ["Root", "Shoulder", "Elbow", "Wrist"]
        )

    def test_parent_must_precede_child(self):
        with self.assertRaisesRegex(ValueError, "must appear before"):
            _common.validate_joint_specs(
                [
                    {
                        "name": "Wrist",
                        "parent": "Elbow",
                        "position": [0, 0, 0],
                        "label": "Root",
                    }
                ]
            )

    def test_template_resolution_rejects_paths(self):
        with self.assertRaisesRegex(ValueError, "not a path"):
            _common.resolve_template("../biped.ma")

    def test_template_resolution_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as raw_dir:
            scripts = Path(raw_dir)
            (scripts / "AdvancedSkeleton.mel").touch()
            templates = scripts / "AdvancedSkeletonFiles" / "fitSkeletons"
            templates.mkdir(parents=True)
            expected = templates / "biped.ma"
            expected.touch()
            with patch.dict(os.environ, {"MAYA_SCRIPT_PATH": raw_dir}):
                self.assertEqual(_common.resolve_template("BIPED"), expected)

    def test_relationship_attribute_requires_target(self):
        with self.assertRaisesRegex(ValueError, "target"):
            _common.validate_attribute_configs([{"name": "follow"}])

    def test_attribute_value_keys_are_whitelisted(self):
        with self.assertRaisesRegex(ValueError, "unsupported value keys"):
            _common.validate_attribute_configs(
                [{"name": "twist/bendy", "values": {"arbitraryMel": "bad"}}]
            )


if __name__ == "__main__":
    unittest.main()
