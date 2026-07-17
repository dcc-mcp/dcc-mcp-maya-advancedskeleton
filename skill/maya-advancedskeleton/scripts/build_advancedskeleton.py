"""Build or rebuild AdvancedSkeleton from the current FitSkeleton."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict

from dcc_mcp_core.skills_helper import (
    run_main,
    skill_entry,
    skill_error_from_exception,
    skill_success,
)

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _common import maya_modules, scene_summary, source_advancedskeleton  # noqa: E402


@skill_entry
def main(
    keep_all: bool = True, set_units_to_centimeters: bool = True, **_params: Any
) -> Dict[str, Any]:
    try:
        cmds, mel = maya_modules()
        if not cmds.objExists("FitSkeleton"):
            raise RuntimeError("FitSkeleton does not exist")
        source_advancedskeleton(open_ui=True)
        operation = "rebuild" if cmds.objExists("Group") else "build"
        previous_unit = cmds.currentUnit(query=True, linear=True)
        if previous_unit not in {"cm", "centimeter"}:
            if not set_units_to_centimeters:
                raise RuntimeError(
                    "AdvancedSkeleton requires centimeters; set set_units_to_centimeters=true"
                )
            cmds.currentUnit(linear="cm")
        if cmds.control("asKeepAllCheckBox", exists=True):
            cmds.checkBox("asKeepAllCheckBox", edit=True, value=keep_all)
        mel.eval("asReBuildAdvancedSkeleton;")
        if not cmds.objExists("Group"):
            raise RuntimeError("AdvancedSkeleton completed without creating Group")
        return skill_success(
            "AdvancedSkeleton {} completed".format(operation),
            prompt="Inspect the generated controls and deformation hierarchy in Maya.",
            operation=operation,
            previous_linear_unit=previous_unit,
            current_linear_unit=cmds.currentUnit(query=True, linear=True),
            scene=scene_summary(),
        )
    except Exception as exc:
        return skill_error_from_exception(
            exc,
            message="AdvancedSkeleton build/rebuild failed",
            prompt="Call inspect_advancedskeleton and verify the FitSkeleton labels, names, and package state.",
        )


if __name__ == "__main__":
    run_main(main)
