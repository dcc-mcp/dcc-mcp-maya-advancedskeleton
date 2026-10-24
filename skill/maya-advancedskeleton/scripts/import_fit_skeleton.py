"""Import an installed AdvancedSkeleton FitSkeleton template without dialogs."""

from __future__ import annotations

from typing import Any, Dict

from dcc_mcp_core.skills_helper import (
    run_main,
    skill_entry,
    skill_error_from_exception,
    skill_success,
)

from _common import (
    maya_modules,
    resolve_template,
    scene_summary,
    source_advancedskeleton,
)


@skill_entry
def main(
    template_name: str,
    kind: str = "body",
    replace_existing: bool = False,
    **_params: Any,
) -> Dict[str, Any]:
    try:
        if kind not in {"body", "limb"}:
            raise ValueError("kind must be 'body' or 'limb'")
        cmds, mel = maya_modules()
        source_advancedskeleton(open_ui=False)
        template = resolve_template(template_name, kind)
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
        new_nodes = (
            cmds.file(
                str(template),
                i=True,
                type="mayaAscii",
                ignoreVersion=True,
                returnNewNodes=True,
            )
            or []
        )
        if not cmds.objExists("FitSkeleton"):
            raise RuntimeError("Template import did not create FitSkeleton")
        mel.eval("asEnsureFitSkeletonAttributes;")
        if not cmds.attributeQuery(
            "fitSkeletonTemplate", node="FitSkeleton", exists=True
        ):
            cmds.addAttr(
                "FitSkeleton", longName="fitSkeletonTemplate", dataType="string"
            )
        cmds.setAttr("FitSkeleton.fitSkeletonTemplate", template.stem, type="string")
        cmds.select("FitSkeleton", replace=True)
        return skill_success(
            "Imported AdvancedSkeleton {} template '{}'".format(kind, template.name),
            prompt="Position or configure the FitSkeleton, then call build_advancedskeleton.",
            template=template.name,
            kind=kind,
            created_node_count=len(new_nodes),
            scene=scene_summary(),
        )
    except Exception as exc:
        return skill_error_from_exception(
            exc,
            message="Failed to import AdvancedSkeleton template",
            prompt="Call inspect_advancedskeleton to list installed templates and current scene state.",
        )


if __name__ == "__main__":
    run_main(main)
