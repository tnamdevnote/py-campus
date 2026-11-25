"""Builds buildings from the dicts in config.BUILDINGS.

Each building is built in its own local frame, with the front (door) wall on
the local -z side, then rotated so the door faces the configured direction.
Enterable buildings are hollow: four walls with a doorway, a roof, a floor,
and a little furniture. Other buildings are a solid block.
"""
from ursina import Entity, Text, scene

from .style import col, shaded, GLASS

# Ursina's rotation_y that makes local -z (the front) face each direction.
FACING_ROTATION = {"south": 0, "west": 90, "north": 180, "east": 270}

WALL = 0.4          # wall thickness
DOOR_WIDTH = 3.0
DOOR_HEIGHT = 3.2
FLOOR_HEIGHT = 3.5  # spacing of window rows


def facing_rotation(direction):
    try:
        return FACING_ROTATION[direction]
    except KeyError:
        raise ValueError(
            f"door/facing must be one of {sorted(FACING_ROTATION)}, got {direction!r}"
        ) from None


def _box(parent, position, scale, color, collider=True, **kwargs):
    return Entity(
        parent=parent,
        model="cube",
        position=position,
        scale=scale,
        color=col(color),
        collider="box" if collider else None,
        **shaded(),
        **kwargs,
    )


def build_building(spec, parent=scene):
    """Create one building from a config dict and return its root Entity."""
    w, d, h = spec["width"], spec["depth"], spec["height"]
    wall_color = spec.get("color", "#d8cbb5")
    roof_color = spec.get("roof", "#5b5650")
    trim = spec.get("trim", "#7a6a58")

    root = Entity(
        parent=parent,
        position=(spec["x"], 0, spec["z"]),
        rotation_y=facing_rotation(spec["door"]),
        name=spec["name"],
    )

    front_z = -d / 2

    if spec.get("enterable"):
        _build_shell(root, w, d, h, wall_color)
        _build_interior(root, w, d, spec.get("interior", "empty"), trim)
    else:
        _box(root, (0, h / 2, 0), (w, h, d), wall_color)
        # A closed door so it still reads as a building.
        _box(root, (0, DOOR_HEIGHT / 2, front_z - 0.05), (DOOR_WIDTH - 0.6, DOOR_HEIGHT, 0.1),
             "#4b3a2e", collider=False)

    # Roof slab, slightly overhanging.
    _box(root, (0, h + 0.25, 0), (w + 0.6, 0.5, d + 0.6), roof_color)

    # Door frame.
    for sx in (-1, 1):
        _box(root, (sx * (DOOR_WIDTH / 2 + 0.15), DOOR_HEIGHT / 2, front_z - 0.12),
             (0.3, DOOR_HEIGHT, 0.25), trim, collider=False)
    _box(root, (0, DOOR_HEIGHT + 0.15, front_z - 0.12), (DOOR_WIDTH + 0.6, 0.3, 0.25),
         trim, collider=False)

    _build_windows(root, w, h, front_z, spec.get("floors"))

    sign = spec.get("sign", spec["name"])
    if sign:
        _build_sign(root, sign, w, front_z, trim)

    return root


def _build_shell(root, w, d, h, wall_color):
    t = WALL
    front_z = -d / 2
    # Back and side walls.
    _box(root, (0, h / 2, d / 2 - t / 2), (w, h, t), wall_color)
    _box(root, (-w / 2 + t / 2, h / 2, 0), (t, h, d), wall_color)
    _box(root, (w / 2 - t / 2, h / 2, 0), (t, h, d), wall_color)
    # Front wall, split around the doorway.
    side = (w - DOOR_WIDTH) / 2
    for sx in (-1, 1):
        _box(root, (sx * (DOOR_WIDTH / 2 + side / 2), h / 2, front_z + t / 2), (side, h, t),
             wall_color)
    _box(root, (0, DOOR_HEIGHT + (h - DOOR_HEIGHT) / 2, front_z + t / 2),
         (DOOR_WIDTH, h - DOOR_HEIGHT, t), wall_color)
    # Interior floor and ceiling (no collider on the floor: the ground holds you up).
    _box(root, (0, 0.03, 0), (w - 2 * t, 0.06, d - 2 * t), "#b89c7a", collider=False)
    _box(root, (0, h - 0.1, 0), (w - 2 * t, 0.2, d - 2 * t), "#efe9dc", collider=False)


def _build_windows(root, w, h, front_z, floors):
    if floors is None:
        floors = max(1, int(h // FLOOR_HEIGHT))
    # Storefront glass on either side of the door.
    pane = min(4.0, (w - DOOR_WIDTH) / 2 - 1.5)
    if pane > 0.8:
        for sx in (-1, 1):
            x = sx * (DOOR_WIDTH / 2 + 0.8 + pane / 2)
            _box(root, (x, 1.8, front_z - 0.03), (pane, 2.0, 0.08), GLASS, collider=False)
    # Rows of upper windows.
    cols = max(1, int(w // 4))
    for row in range(1, floors):
        y = row * FLOOR_HEIGHT + 1.6
        if y + 0.8 > h - 0.4:
            break
        for c in range(cols):
            x = -w / 2 + (c + 0.5) * (w / cols)
            _box(root, (x, y, front_z - 0.03), (1.4, 1.6, 0.08), GLASS, collider=False)


def _build_sign(root, text, w, front_z, trim):
    board_w = min(w - 1, max(4, len(text) * 0.9 + 1.5))
    y = DOOR_HEIGHT + 1.0
    _box(root, (0, y, front_z - 0.12), (board_w, 1.2, 0.15), trim, collider=False)
    Text(
        parent=root,
        text=text,
        position=(0, y, front_z - 0.22),
        origin=(0, 0),
        scale=36,
        color=col("#fffaf0"),
    )


def _build_interior(root, w, d, kind, trim):
    """Simple furniture so the inside isn't empty. All pieces block movement."""
    t = WALL
    back = d / 2 - t
    if kind == "shop":
        # Shelving along the back and a checkout counter by the door.
        for x in range(int(-w / 2 + 2), int(w / 2 - 1), 4):
            _box(root, (x + 1, 1.2, back - 0.5), (3, 2.4, 0.8), "#8a6a4a")
        _box(root, (w / 2 - 3, 0.55, -d / 2 + 3), (3.5, 1.1, 1.0), trim)
        for x in (-3, 0, 3):
            _box(root, (x, 0.7, 1), (2.2, 1.4, 0.8), "#c9b28d")
    elif kind == "cafe":
        _box(root, (0, 0.55, back - 1.2), (w - 3, 1.1, 1.0), trim)  # counter
        for x, z in ((-3, -1.5), (2.5, -1.5), (-3, 1.5), (2.5, 1.5)):
            _box(root, (x, 0.75, z), (1.2, 0.08, 1.2), "#6b4a32")   # tabletop
            _box(root, (x, 0.37, z), (0.15, 0.75, 0.15), "#3d3d3d")  # leg
    elif kind == "books":
        for z in range(int(-d / 2 + 4), int(d / 2 - 1), 3):
            _box(root, (-w / 4, 1.0, z), (w / 3, 2.0, 0.6), "#7a4e2d")
            _box(root, (w / 4, 1.0, z), (w / 3, 2.0, 0.6), "#7a4e2d")
    elif kind == "classroom":
        _box(root, (0, 1.8, back - 0.05), (w * 0.5, 2.0, 0.1), "#2f4a3a", collider=False)  # board
        for x in range(int(-w / 2 + 3), int(w / 2 - 2), 3):
            for z in (-1, 1.5):
                _box(root, (x, 0.4, z), (1.6, 0.8, 0.9), "#a07850")
