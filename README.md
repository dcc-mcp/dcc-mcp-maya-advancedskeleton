# dcc-mcp-maya-advancedskeleton

<p align="center">
  <img src="docs/assets/dcc-mcp-maya-advancedskeleton.svg" alt="DCC-MCP · MAYA-ADVANCEDSKELETON" width="600">
</p>

## Agent workflow

AI agents should use the shared gateway through `dcc-mcp-cli`; IDE users may
continue to use the MCP endpoint. Prefer typed skills and tools over raw scripts.

### Install or update the CLI

`dcc-mcp-cli` is the preferred control path for every shell-capable agent. If
it is missing, ask the user before installing the latest official release:

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/dcc-mcp/dcc-mcp-core/main/scripts/install-cli.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/dcc-mcp/dcc-mcp-core/main/scripts/install-cli.ps1 | iex"
```

Keep an official build current through the release manifest:

```bash
dcc-mcp-cli update check
dcc-mcp-cli update apply
```

`update apply` downloads and stages the latest CLI for the next launch. It
does not update a running `dcc-mcp-server`; update that server in its own
environment.

```bash
dcc-mcp-cli dcc-types
dcc-mcp-cli list
dcc-mcp-cli search --query "<task>" --dcc-type maya
dcc-mcp-cli describe <tool-slug>
dcc-mcp-cli call <tool-slug> --json '{"key":"value"}'
```

`dcc-types` reports release-catalog support; `list` reports live sessions. If a
tool belongs to an inactive progressive skill, call `dcc-mcp-cli load-skill <skill-name> --dcc-type maya` before retrying. For post-task improvement,
attach a stable session id with `--meta-json`, query `dcc-mcp-cli stats --range 24h --session-id <task-id>`, then pass the bounded evidence to the
`review_skill_improvement` prompt from `dcc-mcp-skills-creator`.


AdvancedSkeleton rigging skills for `dcc-mcp-maya`.

![FitSkeleton setup, AdvancedSkeleton rig build, and bound character workflow](docs/images/maya-advancedskeleton-showcase.webp)

Illustrative workflow derived from the verified Cesium Man test case. Cesium Man is
copyright 2017 Cesium and is used under its model-specific license; see the
[case license](skill/maya-advancedskeleton/examples/CesiumMan_LICENSE.md).

## Capability coverage

| Requested workflow | Skill tools |
| --- | --- |
| Discover the installed body/limb FitSkeleton presets | `inspect_advancedskeleton` |
| Import and position a standard FitSkeleton | `import_fit_skeleton` |
| Build a custom modular skeleton from labels and attributes | `create_fit_skeleton`, `configure_fit_joint` |
| Configure twist/bendy, orientation, follow, and controller generation | `configure_fit_joint` |
| Build once, edit FitSkeleton, and reproduce the rig | `build_advancedskeleton` (Build/ReBuild) |

The workbook's Root -> Shoulder -> Elbow -> Hand-labelled Wrist acceptance case is runnable from [RECIPES.md](skill/maya-advancedskeleton/references/RECIPES.md).

## End-to-end Maya MCP case

This verified case combines `maya-advancedskeleton` with the Maya import,
rigging, animation, and playblast tools. This Skill owns FitSkeleton setup and
the AdvancedSkeleton build; the run/jump animation is downstream validation.

| FitSkeleton aligned to the character | Generated AdvancedSkeleton controls |
| --- | --- |
| ![Cesium Man with the fitted skeleton in Maya](skill/maya-advancedskeleton/examples/fit-skeleton-alignment.webp) | ![Cesium Man with the generated AdvancedSkeleton controls in Maya](skill/maya-advancedskeleton/examples/built-advanced-rig.webp) |

[Watch the 300-frame run/jump playblast](skill/maya-advancedskeleton/examples/cesium-man-run-jump-300f.mp4)
(H.264, 1280x720, 24 fps, 12.5 seconds, approximately 15 metres of travel).

Read [CASE_STUDY.md](skill/maya-advancedskeleton/references/CASE_STUDY.md)
for the workflow boundary, validation evidence, source, and license details.

## Requirements

- Maya 2020-2026
- `dcc-mcp-core >= 0.20.0`
- `dcc-mcp-maya`
- An installed and appropriately licensed AdvancedSkeleton 6.x package

Core 0.20.0 or later supplies the runtime-scoped sibling imports used by this
Skill. Update Core in the Maya adapter environment before loading this Skill;
updating only `dcc-mcp-cli` does not update the embedded runtime.

Add `skill/maya-advancedskeleton` to the Maya adapter's skill paths, search for `maya-advancedskeleton`, load it, and call `inspect_advancedskeleton` before scene-changing tools.

## Safety

- No arbitrary MEL execution tool.
- Template names cannot escape AdvancedSkeleton's installed template directories.
- Joint, label, and AdvancedSkeleton attribute inputs are validated.
- Existing FitSkeleton replacement is opt-in and refused after a rig has been built.

## Licenses

This MCP integration is MIT licensed. AdvancedSkeleton is third-party software governed by its own EULA and commercial-use terms. This repository does not redistribute AdvancedSkeleton code, templates, example rigs, or documentation.
