"""Inspect the installed AdvancedSkeleton package, templates, and scene state."""

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

from _common import (  # noqa: E402
    list_templates,
    package_version,
    scene_summary,
    source_advancedskeleton,
)


@skill_entry
def main(verbose: bool = False, **_params: Any) -> Dict[str, Any]:
    try:
        script = source_advancedskeleton(open_ui=False)
        context = {
            "available": True,
            "package_version": package_version(script),
            "body_templates": list_templates("body"),
            "limb_templates": list_templates("limb"),
            "scene": scene_summary(),
        }
        if verbose:
            context["script_path"] = str(script)
        return skill_success(
            "AdvancedSkeleton is available",
            prompt="Import a template or create a custom FitSkeleton before building.",
            **context,
        )
    except Exception as exc:
        return skill_error_from_exception(
            exc,
            message="AdvancedSkeleton is unavailable",
            prompt="Launch Maya with maya_advancedskeleton enabled, then retry.",
            available=False,
        )


if __name__ == "__main__":
    run_main(main)
