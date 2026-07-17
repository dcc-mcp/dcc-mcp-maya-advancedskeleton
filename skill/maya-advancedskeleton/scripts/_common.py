"""Shared AdvancedSkeleton/Maya helpers.

This project never redistributes AdvancedSkeleton code or assets. It only calls
the installed package through Maya's public command surfaces.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


_MAYA_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TEMPLATE_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")
_LABEL_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

LABEL_CODES = {
    "None": 0,
    "Root": 1,
    "Hip": 2,
    "Foot": 4,
    "ToesEnd": 18,
    "Shoulder": 10,
    "Hand": 12,
    "PropA": 15,
    "PropB": 16,
    "PropC": 17,
    "Other": 18,
    "Chest": 18,
    "Mid": 18,
    "Toes": 18,
    "Heel": 18,
    "BigToe": 18,
    "PinkyToe": 18,
    "LegAim": 18,
    "QToes": 18,
    "Eye": 18,
    "Wheel": 18,
    "0": 18,
    "1": 18,
    "2": 18,
    "3": 18,
}

SUPPORTED_ATTRIBUTES = {
    "twist/bendy",
    "inbetween",
    "global",
    "aim",
    "wheel",
    "rollingBall",
    "freeOrient",
    "worldOrient",
    "flipOrient",
    "noMirror",
    "noFlip",
    "noControl",
    "noSkin",
    "ikLocal",
    "hipSwinger",
    "follow",
    "ikFollow",
    "aimAt",
    "rootOptions",
    "cog",
    "segScaleComp",
    "childOfPart",
    "control",
    "orientConstraint",
    "footPivots",
}

_RELATIONSHIP_ATTRIBUTES = {"follow", "ikFollow", "aimAt", "orientConstraint"}

_ATTRIBUTE_VALUE_KEYS = {
    "twist/bendy": {"twistJoints", "bendyCtrls"},
    "inbetween": {"inbetweenJoints", "unTwister"},
    "global": {"global", "globalTranslate"},
    "worldOrient": {"worldOrientUp", "worldOrientForward"},
    "noMirror": {"noMirror", "noMirrorLeft"},
    "ikLocal": {"ikLocal"},
    "follow": {"follow", "followLeftRight", "followWorld"},
    "ikFollow": {"ikFollow"},
    "aimAt": {"aimAt", "aimAxis", "aimUpAxis"},
    "rootOptions": {"numMainExtras", "legLock"},
    "childOfPart": {"childOfPart"},
    "orientConstraint": {"orientConstraint", "orientConstraintMaintainOffset"},
}
for _simple_attr in SUPPORTED_ATTRIBUTES - set(_ATTRIBUTE_VALUE_KEYS):
    _ATTRIBUTE_VALUE_KEYS[_simple_attr] = {_simple_attr}


def maya_modules() -> Tuple[Any, Any]:
    """Import Maya lazily so catalog discovery works outside Maya."""
    import maya.cmds as cmds  # type: ignore
    import maya.mel as mel  # type: ignore

    return cmds, mel


def find_advancedskeleton_script() -> Path:
    """Find the installed AdvancedSkeleton MEL entrypoint."""
    for raw_dir in os.environ.get("MAYA_SCRIPT_PATH", "").split(os.pathsep):
        if not raw_dir:
            continue
        candidate = Path(raw_dir) / "AdvancedSkeleton.mel"
        if candidate.is_file():
            return candidate.resolve()
    raise RuntimeError(
        "AdvancedSkeleton.mel was not found on MAYA_SCRIPT_PATH. "
        "Launch Maya with the maya_advancedskeleton package enabled."
    )


def source_advancedskeleton(open_ui: bool = False) -> Path:
    """Source the installed MEL file and optionally initialize its controls."""
    cmds, mel = maya_modules()
    script = find_advancedskeleton_script()
    mel_path = str(script).replace("\\", "/").replace('"', '\\"')
    mel.eval('source "{}";'.format(mel_path))
    if open_ui and not cmds.control("asBuildAdvancedSkeletonButton", exists=True):
        mel.eval("AdvancedSkeleton();")
    return script


def template_directory(kind: str = "body") -> Path:
    script = find_advancedskeleton_script()
    folder = "fitSkeletons" if kind == "body" else "fitSkeletonsLimbs"
    directory = script.parent / "AdvancedSkeletonFiles" / folder
    if not directory.is_dir():
        raise RuntimeError(
            "AdvancedSkeleton template directory is missing: {}".format(folder)
        )
    return directory


def list_templates(kind: str = "body") -> List[str]:
    if kind not in {"body", "limb"}:
        raise ValueError("kind must be 'body' or 'limb'")
    return sorted(path.name for path in template_directory(kind).glob("*.ma"))


def resolve_template(template_name: str, kind: str = "body") -> Path:
    """Resolve a template name without allowing path traversal."""
    if not isinstance(template_name, str) or not _TEMPLATE_NAME.fullmatch(
        template_name
    ):
        raise ValueError("template_name must be a filename, not a path")
    requested = (
        template_name
        if template_name.lower().endswith(".ma")
        else template_name + ".ma"
    )
    matches = {
        path.name.lower(): path for path in template_directory(kind).glob("*.ma")
    }
    try:
        return matches[requested.lower()]
    except KeyError as exc:
        raise ValueError(
            "Unknown {} template {!r}. Available: {}".format(
                kind,
                template_name,
                ", ".join(sorted(path.name for path in matches.values())),
            )
        ) from exc


def package_version(script_path: Path) -> str:
    """Return the package-directory version for the conventional layout."""
    if script_path.parent.name == "scripts":
        return script_path.parent.parent.name
    return "unknown"


def validate_maya_name(value: str, field: str = "name") -> str:
    if not isinstance(value, str) or not _MAYA_NAME.fullmatch(value):
        raise ValueError("{} must match {}".format(field, _MAYA_NAME.pattern))
    return value


def validate_label(label: str) -> str:
    if not isinstance(label, str) or not _LABEL_NAME.fullmatch(label):
        raise ValueError("label must contain only letters, digits, '_' or '-' (max 64)")
    return label


def validate_position(position: Sequence[Any]) -> List[float]:
    if not isinstance(position, (list, tuple)) or len(position) != 3:
        raise ValueError("position must contain exactly three numbers")
    result = [float(value) for value in position]
    if not all(math.isfinite(value) for value in result):
        raise ValueError("position values must be finite")
    return result


def validate_joint_specs(joints: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Validate ordered joint specs and require one AdvancedSkeleton Root label."""
    if not isinstance(joints, (list, tuple)) or not joints:
        raise ValueError("joints must be a non-empty array")
    normalized: List[Dict[str, Any]] = []
    seen = set()
    has_root_label = False
    for index, spec in enumerate(joints):
        if not isinstance(spec, Mapping):
            raise ValueError("joints[{}] must be an object".format(index))
        name = validate_maya_name(spec.get("name"), "joints[{}].name".format(index))
        if name in seen or name == "FitSkeleton":
            raise ValueError("duplicate or reserved joint name: {}".format(name))
        parent = spec.get("parent")
        if parent is not None:
            parent = validate_maya_name(parent, "joints[{}].parent".format(index))
            if parent not in seen:
                raise ValueError(
                    "parent {!r} must appear before {!r}".format(parent, name)
                )
        label = validate_label(spec.get("label", "None"))
        has_root_label = has_root_label or label == "Root"
        attributes = spec.get("attributes", [])
        validate_attribute_configs(attributes)
        normalized.append(
            {
                "name": name,
                "parent": parent,
                "position": validate_position(spec.get("position", [0.0, 0.0, 0.0])),
                "label": label,
                "attributes": list(attributes),
            }
        )
        seen.add(name)
    if not has_root_label:
        raise ValueError("at least one joint must use the 'Root' label")
    return normalized


def validate_attribute_configs(attributes: Iterable[Mapping[str, Any]]) -> None:
    if not isinstance(attributes, (list, tuple)):
        raise ValueError("attributes must be an array")
    for index, config in enumerate(attributes):
        if not isinstance(config, Mapping):
            raise ValueError("attributes[{}] must be an object".format(index))
        name = config.get("name")
        if name not in SUPPORTED_ATTRIBUTES:
            raise ValueError(
                "unsupported AdvancedSkeleton attribute: {!r}".format(name)
            )
        target = config.get("target")
        if name in _RELATIONSHIP_ATTRIBUTES:
            validate_maya_name(target, "attributes[{}].target".format(index))
        elif target is not None:
            raise ValueError("attribute {!r} does not accept target".format(name))
        values = config.get("values", {})
        if not isinstance(values, Mapping):
            raise ValueError("attributes[{}].values must be an object".format(index))
        unknown = set(values) - _ATTRIBUTE_VALUE_KEYS[name]
        if unknown:
            raise ValueError(
                "unsupported value keys for {!r}: {}".format(
                    name, ", ".join(sorted(unknown))
                )
            )
        if any(isinstance(value, (dict, list, tuple)) for value in values.values()):
            raise ValueError("attribute values must be scalar")


def set_joint_label(joint: str, label: str) -> None:
    cmds, _ = maya_modules()
    validate_maya_name(joint, "joint")
    label = validate_label(label)
    code = LABEL_CODES.get(label, 18)
    cmds.setAttr(joint + ".drawLabel", label != "None")
    cmds.setAttr(joint + ".type", code)
    if code == 18:
        cmds.setAttr(joint + ".otherType", label, type="string")


def _ensure_attribute(
    cmds: Any,
    node: str,
    name: str,
    attribute_type: str,
    default: Any = None,
    minimum: Any = None,
    maximum: Any = None,
    enum_name: str = None,
) -> None:
    if cmds.attributeQuery(name, node=node, exists=True):
        if enum_name is not None:
            cmds.addAttr(node + "." + name, edit=True, enumName=enum_name)
        return
    options = {
        "longName": name,
        "attributeType": attribute_type,
        "keyable": True,
    }
    if default is not None:
        options["defaultValue"] = default
    if minimum is not None:
        options["minValue"] = minimum
    if maximum is not None:
        options["maxValue"] = maximum
    if enum_name is not None:
        options["enumName"] = enum_name
    cmds.addAttr(node, **options)


def _create_advancedskeleton_attribute(
    cmds: Any, joint: str, name: str, target: str = None
) -> None:
    if name == "twist/bendy":
        if cmds.attributeQuery("inbetweenJoints", node=joint, exists=True):
            raise ValueError("twist/bendy cannot be combined with inbetween")
        _ensure_attribute(cmds, joint, "twistJoints", "long", 2, 0, 10)
        _ensure_attribute(cmds, joint, "bendyCtrls", "long", 0, 0)
    elif name == "inbetween":
        if cmds.attributeQuery("twistJoints", node=joint, exists=True):
            raise ValueError("inbetween cannot be combined with twist/bendy")
        _ensure_attribute(cmds, joint, "inbetweenJoints", "long", 2, 0)
        _ensure_attribute(cmds, joint, "unTwister", "bool", False)
    elif name == "global":
        _ensure_attribute(cmds, joint, "global", "double", 0, 0, 10)
        _ensure_attribute(cmds, joint, "globalTranslate", "bool", False)
    elif name == "noMirror":
        _ensure_attribute(cmds, joint, "noMirror", "bool", True)
        _ensure_attribute(cmds, joint, "noMirrorLeft", "bool", False)
    elif name == "worldOrient":
        _ensure_attribute(
            cmds,
            joint,
            "worldOrientUp",
            "enum",
            0,
            enum_name="xUp:yUp:zUp:xDown:yDown:zDown:",
        )
        _ensure_attribute(
            cmds,
            joint,
            "worldOrientForward",
            "enum",
            6,
            enum_name="xForward:yForward:zForward:xBackward:yBackward:zBackward:free:",
        )
    elif name == "ikLocal":
        _ensure_attribute(
            cmds, joint, "ikLocal", "enum", 0, enum_name="addCtrl:nonZero:localOrient:"
        )
    elif name in _RELATIONSHIP_ATTRIBUTES:
        if not cmds.objExists(target) or cmds.nodeType(target) != "joint":
            raise ValueError("target joint does not exist: {}".format(target))
        _ensure_attribute(cmds, joint, name, "enum", 0, enum_name=target)
        if name == "follow":
            _ensure_attribute(cmds, joint, "followLeftRight", "bool", False)
            _ensure_attribute(cmds, joint, "followWorld", "bool", False)
        elif name == "aimAt":
            _ensure_attribute(cmds, joint, "aimAxis", "enum", 0, enum_name="x:y:z:")
            _ensure_attribute(cmds, joint, "aimUpAxis", "enum", 1, enum_name="x:y:z:")
        elif name == "orientConstraint":
            _ensure_attribute(
                cmds, joint, "orientConstraintMaintainOffset", "bool", False
            )
    elif name == "rootOptions":
        if joint != "Root":
            raise ValueError("rootOptions can only be added to the Root joint")
        _ensure_attribute(cmds, joint, "numMainExtras", "long", 0, 0)
        _ensure_attribute(cmds, joint, "legLock", "bool", True)
    elif name == "childOfPart":
        _ensure_attribute(cmds, joint, "childOfPart", "long", 2, 1, 10)
    else:
        _ensure_attribute(cmds, joint, name, "bool", True)


def add_joint_attributes(
    joint: str, attributes: Sequence[Mapping[str, Any]]
) -> List[str]:
    """Add the whitelisted Maya attributes consumed by AdvancedSkeleton."""
    validate_attribute_configs(attributes)
    if not attributes:
        return []
    cmds, _ = maya_modules()
    validate_maya_name(joint, "joint")
    configured = []
    for config in attributes:
        name = config["name"]
        _create_advancedskeleton_attribute(cmds, joint, name, config.get("target"))
        for attr_name, value in config.get("values", {}).items():
            if not cmds.attributeQuery(attr_name, node=joint, exists=True):
                raise RuntimeError(
                    "AdvancedSkeleton attribute was not created: {}.{}".format(
                        joint, attr_name
                    )
                )
            cmds.setAttr(joint + "." + attr_name, value)
        configured.append(name)
    return configured


def scene_summary() -> Dict[str, Any]:
    cmds, _ = maya_modules()
    has_fit = cmds.objExists("FitSkeleton")
    joints = (
        cmds.listRelatives("FitSkeleton", allDescendents=True, type="joint") or []
        if has_fit
        else []
    )
    return {
        "fit_skeleton_exists": has_fit,
        "advanced_rig_exists": cmds.objExists("Group"),
        "joint_count": len(joints),
        "joints": sorted(joints),
    }
