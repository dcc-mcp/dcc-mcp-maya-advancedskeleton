---
name: maya-advancedskeleton
description: >-
  AdvancedSkeleton rigging for Maya: inspect installed templates, import or create
  FitSkeletons, configure joint labels and supported AdvancedSkeleton attributes,
  then build or rebuild the rig. Use for AdvancedSkeleton body/limb setup. Not for
  generic Maya rigging without an installed and licensed AdvancedSkeleton package.
license: MIT
compatibility: "Python 3.7+; dcc-mcp-core 0.18+; Maya 2020-2026; AdvancedSkeleton 6.x"
metadata:
  dcc-mcp:
    dcc: maya
    version: "0.1.1"
    layer: domain
    tags: ["maya", "rigging", "advancedskeleton", "fitskeleton", "ik"]
    search-hint: "maya advanced skeleton, AdvancedSkeleton, FitSkeleton, modular rig, joint labels, build rig, rebuild rig"
    tools: tools.yaml
---

# Maya AdvancedSkeleton

Use the tools in this order:

1. `inspect_advancedskeleton` proves the package is available and lists installed body/limb templates.
2. Start from either `import_fit_skeleton` or `create_fit_skeleton`.
3. Use `configure_fit_joint` for later label, orientation, follow, twist/bendy, or controller-generation changes.
4. Call `build_advancedskeleton`; the same tool performs a rebuild when an AdvancedSkeleton rig already exists.

Joint specs are parent-first. At least one joint must use the `Root` label. Template names are resolved only inside the installed AdvancedSkeleton template directories; arbitrary file paths and arbitrary MEL are intentionally unsupported.

Read [RECIPES.md](references/RECIPES.md) for the custom arm case and attribute examples.

Read [CASE_STUDY.md](references/CASE_STUDY.md) for a verified character-binding
case. It uses this Skill for FitSkeleton setup and rig construction, then uses
separate Maya rigging and animation tools for skin binding and the 300-frame
run/jump validation.

## External license

This skill is MIT licensed. AdvancedSkeleton itself is separate software with its own EULA and commercial-use terms. This repository does not redistribute its code, templates, example rigs, or documentation.
