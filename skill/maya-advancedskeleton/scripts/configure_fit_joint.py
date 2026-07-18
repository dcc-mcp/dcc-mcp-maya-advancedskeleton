"""Configure one FitSkeleton joint through safe label and attribute contracts."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from dcc_mcp_core.skills_helper import (
    run_main,
    skill_entry,
    skill_error_from_exception,
    skill_success,
)

from _common import (
    add_joint_attributes,
    maya_modules,
    set_joint_label,
    validate_attribute_configs,
    validate_label,
    validate_maya_name,
)


@skill_entry
def main(
    joint: str,
    label: Optional[str] = None,
    attributes: Optional[List[Mapping[str, Any]]] = None,
    **_params: Any,
) -> Dict[str, Any]:
    try:
        joint = validate_maya_name(joint, "joint")
        attributes = attributes or []
        validate_attribute_configs(attributes)
        cmds, _ = maya_modules()
        if not cmds.objExists(joint) or cmds.nodeType(joint) != "joint":
            raise ValueError("joint does not exist: {}".format(joint))
        if label is not None:
            set_joint_label(joint, validate_label(label))
        configured = add_joint_attributes(joint, attributes)
        return skill_success(
            "Configured AdvancedSkeleton fit joint '{}'".format(joint),
            prompt="Call build_advancedskeleton to build or rebuild after FitSkeleton changes.",
            joint=joint,
            label=label,
            attributes=configured,
        )
    except Exception as exc:
        return skill_error_from_exception(
            exc,
            message="Failed to configure AdvancedSkeleton fit joint",
            prompt="Use an existing FitSkeleton joint and a supported label/attribute name.",
        )


if __name__ == "__main__":
    run_main(main)
