# AdvancedSkeleton Recipes

## Custom arm IK from the acceptance workbook

Create a Root-labelled joint at the origin, then a Shoulder -> Elbow -> Hand-labelled Wrist chain:

```json
{
  "joints": [
    {"name": "Root", "position": [0, 0, 0], "label": "Root"},
    {
      "name": "Shoulder",
      "parent": "Root",
      "position": [0, 10, 0],
      "label": "Shoulder",
      "attributes": [
        {"name": "twist/bendy", "values": {"twistJoints": 2, "bendyCtrls": 0}}
      ]
    },
    {"name": "Elbow", "parent": "Shoulder", "position": [5, 9, 0], "label": "None"},
    {"name": "Wrist", "parent": "Elbow", "position": [10, 10, 0], "label": "Hand"}
  ]
}
```

Call `maya_advancedskeleton__create_fit_skeleton` with that payload, inspect placement in Maya, then call `maya_advancedskeleton__build_advancedskeleton`.

## Orientation, follow, and controller generation

`worldOrient` uses AdvancedSkeleton's enum indices. `worldOrientUp` is `xUp=0`, `yUp=1`, `zUp=2`, `xDown=3`, `yDown=4`, `zDown=5`. `worldOrientForward` is `xForward=0`, `yForward=1`, `zForward=2`, `xBackward=3`, `yBackward=4`, `zBackward=5`, `free=6`.

```json
{
  "joint": "Wrist",
  "attributes": [
    {"name": "worldOrient", "values": {"worldOrientUp": 1, "worldOrientForward": 2}},
    {"name": "follow", "target": "Root", "values": {"followWorld": true}},
    {"name": "noControl", "values": {"noControl": false}}
  ]
}
```

After changing FitSkeleton placement, labels, or attributes, call `maya_advancedskeleton__build_advancedskeleton` again. It detects the existing `Group` and performs AdvancedSkeleton's rebuild path.
