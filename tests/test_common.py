from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).parents[1] / "skill" / "maya-advancedskeleton" / "scripts"
COMMON_SPEC = importlib.util.spec_from_file_location(
    "_common_contract", SCRIPTS / "_common.py"
)
assert COMMON_SPEC is not None and COMMON_SPEC.loader is not None
_common = importlib.util.module_from_spec(COMMON_SPEC)
COMMON_SPEC.loader.exec_module(_common)


class CommonContractTests(unittest.TestCase):
    def test_entrypoints_load_through_runner_import_context(self):
        script_dir = str(SCRIPTS)
        entrypoints = sorted(SCRIPTS.glob("*.py"))
        entrypoints.remove(SCRIPTS / "_common.py")
        try:
            sys.path.insert(0, script_dir)
            for entrypoint in entrypoints:
                source = entrypoint.read_text(encoding="utf-8")
                self.assertNotIn("sys.path.insert", source)
                self.assertNotIn("sys.path.append", source)
                sys.modules.pop("_common", None)
                spec = importlib.util.spec_from_file_location(
                    "_entrypoint_{}".format(entrypoint.stem), entrypoint
                )
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        finally:
            sys.modules.pop("_common", None)
            while script_dir in sys.path:
                sys.path.remove(script_dir)

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
