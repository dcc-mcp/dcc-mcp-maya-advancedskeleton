"""Create a custom AdvancedSkeleton FitSkeleton from ordered joint specs."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from dcc_mcp_core.skills_helper import (
    run_main,
    skill_entry,
    skill_error_from_exception,
    skill_success,
)

from _common import (
    add_joint_attributes,
    maya_modules,
    scene_summary,
    set_joint_label,
    source_advancedskeleton,
    validate_joint_specs,
)


@skill_entry
def main(
    joints: List[Mapping[str, Any]], replace_existing: bool = False, **_params: Any
) -> Dict[str, Any]:
    try:
        specs = validate_joint_specs(joints)
        cmds, mel = maya_modules()
        source_advancedskeleton(open_ui=False)
        if cmds.objExists("Group"):
            raise RuntimeError(
                "An AdvancedSkeleton rig already exists; edit FitSkeleton and rebuild it instead"
            )
        if cmds.objExists("FitSkeleton"):
            if not replace_existing:
                raise RuntimeError(
                    "FitSkeleton already exists; set replace_existing=true to replace it"
                )
            cmds.delete("FitSkeleton")
            if cmds.objExists("FitSkeletonVisualizers"):
                cmds.delete("FitSkeletonVisualizers")

        created = []
        try:
            cmds.createNode("transform", name="FitSkeleton")
            mel.eval("asEnsureFitSkeletonAttributes;")
            for spec in specs:
                parent = spec["parent"] or "FitSkeleton"
                joint = cmds.createNode("joint", name=spec["name"], parent=parent)
                cmds.xform(joint, worldSpace=True, translation=spec["position"])
                set_joint_label(joint, spec["label"])
                created.append(joint)
            for spec in specs:
                add_joint_attributes(spec["name"], spec["attributes"])
        except Exception:
            if cmds.objExists("FitSkeleton"):
                cmds.delete("FitSkeleton")
            raise

        cmds.select("FitSkeleton", replace=True)
        return skill_success(
            "Created custom AdvancedSkeleton FitSkeleton with {} joints".format(
                len(created)
            ),
            prompt="Review joint placement, then call build_advancedskeleton.",
            created_joints=created,
            scene=scene_summary(),
        )
    except Exception as exc:
        return skill_error_from_exception(
            exc,
            message="Failed to create custom AdvancedSkeleton FitSkeleton",
            prompt="Keep joints ordered parent-first and include one joint labelled Root.",
        )


if __name__ == "__main__":
    run_main(main)
