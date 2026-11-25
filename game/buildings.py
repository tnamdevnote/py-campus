"""Builds buildings from the dicts in config.BUILDINGS.

Each building is built in its own local frame, with the front (door) wall on
the local -z side, then rotated so the door faces the configured direction.

Enterable buildings are hollow: four walls with a doorway, a floor, a ceiling
and some furniture. Other buildings are a solid block.

All the visible pieces of a building are merged into one mesh (fast to draw)
and shaded for the building's final orientation. Walls and furniture also get
invisible colliders so the player can't walk through them.
"""
from ursina import Entity, Text, scene

from . import meshes
from .style import col, shade_of, shaded

# Ursina's rotation_y that makes local -z (the front) face each direction.
FACING_ROTATION = {"south": 0, "west": 90, "north": 180, "east": 270}

WALL = 0.4          # wall thickness
DOOR_WIDTH = 3.0
DOOR_HEIGHT = 3.2
FLOOR_HEIGHT = 3.5  # spacing of window rows
WINDOW_SPACING = 3.4

# Looks you can pick with `style=` in config.py. Any key here can also be set
# directly on a building to override its style.
STYLES = {
    # A shop on the Drag: big glass storefront, awning, flat roof with parapet.
    "storefront": dict(
        roof_style="flat", storefront=True, awning=True, pilasters=True,
        window_width=1.4, window_height=1.7,
    ),
    # A UT campus building: limestone, terracotta hip roof, tall windows.
    "campus": dict(
        roof_style="hip", storefront=False, awning=False, pilasters=True,
        window_width=1.2, window_height=2.2,
    ),
    # A plain mid-rise: flat roof, even grid of windows, no awning.
    "apartment": dict(
        roof_style="flat", storefront=False, awning=False, pilasters=False,
        window_width=1.5, window_height=1.6,
    ),
}


def facing_rotation(direction):
    try:
        return FACING_ROTATION[direction]
    except KeyError:
        raise ValueError(
            f"door/facing must be one of {sorted(FACING_ROTATION)}, got {direction!r}"
        ) from None


class _Builder:
    """Collects the pieces of one building and merges them at the end."""

    def __init__(self, root, spec):
        self.root = root
        self.spec = spec
        self.w, self.d, self.h = spec["width"], spec["depth"], spec["height"]
        self.visual = Entity(parent=root, name="visual")

    def box(self, position, scale, color, collider=True, rotation=(0, 0, 0)):
        Entity(parent=self.visual, model=meshes.cube(shaded=False), position=position,
               scale=scale, rotation=rotation, color=col(color))
        if collider:
            Entity(parent=self.root, model="cube", position=position, scale=scale,
                   rotation=rotation, collider="box", visible=False)

    def panel(self, wall, u, y, width, height, out, thickness, color, rotation_x=0):
        """A thin box on the outside of a wall.

        wall: "front", "back", "left" or "right". u runs along the wall
        (left to right as you face it from outside), out is the distance
        from the wall surface to the panel's center.
        """
        w, d = self.w, self.d
        if wall == "front":
            pos, scale, rot = (u, y, -d / 2 - out), (width, height, thickness), (rotation_x, 0, 0)
        elif wall == "back":
            pos, scale, rot = (-u, y, d / 2 + out), (width, height, thickness), (-rotation_x, 0, 0)
        elif wall == "left":
            pos, scale, rot = (-w / 2 - out, y, -u), (thickness, height, width), (0, 0, -rotation_x)
        else:
            pos, scale, rot = (w / 2 + out, y, u), (thickness, height, width), (0, 0, rotation_x)
        self.box(pos, scale, color, collider=False, rotation=rot)

    def wall_length(self, wall):
        return self.w if wall in ("front", "back") else self.d

    def finish(self):
        self.visual.combine(include_normals=True)
        meshes.reshade(self.visual)
        for k, v in shaded().items():
            setattr(self.visual, k, v)


def build_building(spec, parent=scene):
    """Create one building from a config dict and return its root Entity."""
    spec = {**STYLES.get(spec.get("style", "storefront"), STYLES["storefront"]), **spec}
    w, d, h = spec["width"], spec["depth"], spec["height"]
    wall_color = spec.get("color", "#d8cbb5")
    roof_color = spec.get("roof", "#5b5650")
    trim = spec.get("trim", "#7a6a58")
    accent = spec.get("accent") or shade_of(wall_color, 0.18)

    root = Entity(
        parent=parent,
        position=(spec["x"], 0, spec["z"]),
        rotation_y=facing_rotation(spec["door"]),
        name=spec["name"],
    )
    b = _Builder(root, spec)
    front_z = -d / 2

    if spec.get("enterable"):
        _build_shell(b, wall_color)
        _build_interior(b, spec.get("interior", "empty"), trim)
    else:
        b.box((0, h / 2, 0), (w, h, d), wall_color)
        b.panel("front", 0, DOOR_HEIGHT / 2, DOOR_WIDTH - 0.6, DOOR_HEIGHT, 0.04, 0.08, "#4b3a2e")

    _build_base_and_cornice(b, wall_color, accent, spec)
    _build_roof(b, roof_color, accent, spec)
    _build_door_frame(b, trim)
    _build_windows(b, spec, accent)
    if spec.get("awning"):
        _build_awning(b, spec.get("awning_color", trim))

    sign = spec.get("sign", spec["name"])
    if sign:
        _build_sign(b, sign, front_z, trim)

    b.finish()
    return root


def _build_shell(b, wall_color):
    w, d, h, t = b.w, b.d, b.h, WALL
    front_z = -d / 2
    b.box((0, h / 2, d / 2 - t / 2), (w, h, t), wall_color)                # back
    b.box((-w / 2 + t / 2, h / 2, 0), (t, h, d), wall_color)               # left
    b.box((w / 2 - t / 2, h / 2, 0), (t, h, d), wall_color)                # right
    side = (w - DOOR_WIDTH) / 2
    for sx in (-1, 1):                                                     # front, split
        b.box((sx * (DOOR_WIDTH / 2 + side / 2), h / 2, front_z + t / 2), (side, h, t), wall_color)
    b.box((0, DOOR_HEIGHT + (h - DOOR_HEIGHT) / 2, front_z + t / 2),
          (DOOR_WIDTH, h - DOOR_HEIGHT, t), wall_color)
    # Floor and ceiling (no collider on the floor: the ground holds you up).
    b.box((0, 0.03, 0), (w - 2 * t, 0.06, d - 2 * t), "#c2a47e", collider=False)
    b.box((0, h - 0.1, 0), (w - 2 * t, 0.2, d - 2 * t), "#f3eee4", collider=False)
    # Inside walls a touch lighter than the outside, so rooms feel brighter.
    inner = shade_of(wall_color, 0.35)
    b.box((0, h / 2, d / 2 - t - 0.02), (w - 2 * t, h - 0.2, 0.04), inner, collider=False)
    for sx in (-1, 1):
        b.box((sx * (w / 2 - t - 0.02), h / 2, 0), (0.04, h - 0.2, d - 2 * t), inner, collider=False)


def _build_base_and_cornice(b, wall_color, accent, spec):
    w, d, h = b.w, b.d, b.h
    base = spec.get("base_color") or shade_of(wall_color, -0.25)
    # Plinth: a slightly wider band along the bottom of each wall.
    for wall in ("front", "back", "left", "right"):
        length = b.wall_length(wall) + 0.3
        if wall == "front" and spec.get("enterable"):
            side = (length - DOOR_WIDTH) / 2
            for sx in (-1, 1):
                b.panel(wall, sx * (DOOR_WIDTH / 2 + side / 2), 0.35, side, 0.7, 0.08, 0.16, base)
        else:
            b.panel(wall, 0, 0.35, length, 0.7, 0.08, 0.16, base)
    # Cornice: a band that sticks out along the top of the walls.
    for wall in ("front", "back", "left", "right"):
        b.panel(wall, 0, h - 0.35, b.wall_length(wall) + 0.6, 0.5, 0.15, 0.3, accent)
        b.panel(wall, 0, h - 0.75, b.wall_length(wall) + 0.3, 0.2, 0.08, 0.16, accent)
    # Corner pilasters.
    if spec.get("pilasters"):
        for sx in (-1, 1):
            for sz in (-1, 1):
                b.box((sx * (w / 2 + 0.05), h / 2, sz * (d / 2 + 0.05)), (0.7, h - 0.4, 0.7),
                      accent, collider=False)


def _build_roof(b, roof_color, accent, spec):
    w, d, h = b.w, b.d, b.h
    if spec.get("roof_style") == "hip":
        b.box((0, h + 0.15, 0), (w + 1.0, 0.3, d + 1.0), roof_color)       # eaves
        rise = min(w, d) * 0.28
        Entity(parent=b.visual, model=meshes.hip_roof(w + 0.8, d + 0.8, rise, shaded=False),
               position=(0, h + 0.3, 0), color=col(roof_color))
    else:
        # Flat roof: slab inset behind a parapet, plus a little rooftop unit.
        b.box((0, h + 0.05, 0), (w - 0.2, 0.1, d - 0.2), shade_of(roof_color, -0.1))
        for wall in ("front", "back", "left", "right"):
            b.panel(wall, 0, h + 0.45, b.wall_length(wall) + 0.6, 0.9, 0.15, 0.3, accent)
        if w > 8 and d > 8:
            b.box((w * 0.2, h + 0.7, d * 0.15), (2.4, 1.2, 1.8), "#a9a8a3", collider=False)
            b.box((w * 0.2, h + 1.35, d * 0.15), (1.2, 0.1, 1.2), "#7d7c78", collider=False)


def _build_door_frame(b, trim):
    front_z = -b.d / 2
    for sx in (-1, 1):
        b.box((sx * (DOOR_WIDTH / 2 + 0.15), DOOR_HEIGHT / 2, front_z - 0.12),
              (0.3, DOOR_HEIGHT, 0.25), trim, collider=False)
    b.box((0, DOOR_HEIGHT + 0.15, front_z - 0.12), (DOOR_WIDTH + 0.6, 0.3, 0.25), trim,
          collider=False)
    # Doorstep.
    b.box((0, 0.08, front_z - 0.6), (DOOR_WIDTH + 1.0, 0.16, 1.2), "#c8c0b2", collider=False)


def _window(b, wall, u, y, ww, wh, frame, glass="#86aecb", sill=True):
    b.panel(wall, u, y, ww + 0.3, wh + 0.3, 0.05, 0.1, frame)          # frame
    b.panel(wall, u, y, ww, wh, 0.1, 0.04, glass)                       # glass
    b.panel(wall, u, y, 0.08, wh, 0.13, 0.04, frame)                    # mullion
    if sill:
        b.panel(wall, u, y - wh / 2 - 0.2, ww + 0.5, 0.14, 0.15, 0.3, frame)


def _build_windows(b, spec, frame):
    h = b.h
    ww, wh = spec["window_width"], spec["window_height"]
    floors = spec.get("floors") or max(1, int(h // FLOOR_HEIGHT))
    walls = ["front", "left", "right"] + ([] if spec.get("enterable") else ["back"])
    for wall in walls:
        length = b.wall_length(wall)
        cols = max(1, int((length - 1.5) // WINDOW_SPACING))
        for row in range(floors):
            y = row * FLOOR_HEIGHT + 1.9 if row else 1.9
            if y + wh / 2 > h - 1.0:
                break
            if row == 0 and wall == "front" and spec.get("storefront"):
                _storefront(b, frame)
                continue
            for c in range(cols):
                u = -length / 2 + (c + 0.5) * (length / cols)
                if row == 0 and wall == "front" and abs(u) < DOOR_WIDTH / 2 + ww / 2 + 0.4:
                    continue   # leave room for the door
                _window(b, wall, u, y, ww, wh, frame)


def _storefront(b, frame):
    """Big shop windows on either side of the door."""
    w = b.w
    pane = (w - DOOR_WIDTH) / 2 - 1.6
    if pane < 1:
        return
    for sx in (-1, 1):
        u = sx * (DOOR_WIDTH / 2 + 0.8 + pane / 2)
        b.panel("front", u, 1.75, pane + 0.3, 2.5, 0.05, 0.1, frame)
        b.panel("front", u, 1.8, pane, 2.2, 0.1, 0.04, "#8fb8d4")
        for k in range(1, int(pane // 2.2) + 1):
            b.panel("front", u - pane / 2 + k * pane / (int(pane // 2.2) + 1), 1.8, 0.1, 2.2,
                    0.13, 0.04, frame)


def _build_awning(b, color):
    """A sloped fabric awning over the ground floor, in alternating stripes."""
    w = b.w
    width = w - 1.2
    stripes = max(4, int(width // 1.2))
    sw = width / stripes
    light = shade_of(color, 0.55)
    for i in range(stripes):
        u = -width / 2 + (i + 0.5) * sw
        b.panel("front", u, 3.75, sw, 0.08, 0.8, 1.7, color if i % 2 == 0 else light,
                rotation_x=-22)
    b.panel("front", 0, 3.35, width, 0.35, 1.6, 0.06, color)   # valance


def _build_sign(b, text, front_z, trim):
    board_w = min(b.w - 1, max(4, len(text) * 0.9 + 1.5))
    y = DOOR_HEIGHT + 1.0 if not b.spec.get("awning") else 4.9
    b.box((0, y, front_z - 0.12), (board_w + 0.3, 1.5, 0.12), shade_of(trim, -0.3),
          collider=False)
    b.box((0, y, front_z - 0.2), (board_w, 1.2, 0.12), trim, collider=False)
    Text(
        parent=b.root,
        text=text,
        position=(0, y, front_z - 0.3),
        origin=(0, 0),
        scale=36,
        color=col("#fffaf0"),
    )


def _build_interior(b, kind, trim):
    """Simple furniture so the inside isn't empty. All pieces block movement."""
    w, d, t = b.w, b.d, WALL
    back = d / 2 - t
    wood, dark_wood = "#9a7552", "#6b4a32"
    if kind == "shop":
        for x in range(int(-w / 2 + 2), int(w / 2 - 1), 4):
            b.box((x + 1, 1.2, back - 0.5), (3, 2.4, 0.8), wood)
            for shelf_y in (0.6, 1.3, 2.0):
                b.box((x + 1, shelf_y, back - 0.95), (2.8, 0.35, 0.1), "#d6a24a" if x % 8 else
                      "#bf5700", collider=False)
        b.box((w / 2 - 3, 0.55, -d / 2 + 3), (3.5, 1.1, 1.0), trim)
        for x in (-3, 0, 3):
            b.box((x, 0.7, 1), (2.2, 1.4, 0.8), "#d9c29c")
    elif kind == "cafe":
        b.box((0, 0.55, back - 1.2), (w - 3, 1.1, 1.0), trim)          # counter
        b.box((0, 1.15, back - 1.2), (w - 2.8, 0.1, 1.2), dark_wood, collider=False)
        for x, z in ((-3, -1.5), (2.5, -1.5), (-3, 1.5), (2.5, 1.5)):
            b.box((x, 0.75, z), (1.2, 0.08, 1.2), dark_wood)             # tabletop
            b.box((x, 0.37, z), (0.15, 0.75, 0.15), "#3d3d3d")           # leg
    elif kind == "books":
        spines = ("#b5563a", "#3f6c8f", "#d6a24a", "#5b8a4f")
        for i, z in enumerate(range(int(-d / 2 + 4), int(d / 2 - 1), 3)):
            for sx in (-1, 1):
                b.box((sx * w / 4, 1.0, z), (w / 3, 2.0, 0.6), "#7a4e2d")
                b.box((sx * w / 4, 1.0, z - 0.32), (w / 3 - 0.3, 1.6, 0.04),
                      spines[i % len(spines)], collider=False)
    elif kind == "classroom":
        b.box((0, 1.8, back - 0.05), (w * 0.5, 2.0, 0.1), "#2f4a3a", collider=False)  # board
        for x in range(int(-w / 2 + 3), int(w / 2 - 2), 3):
            for z in (-1, 1.5):
                b.box((x, 0.4, z), (1.6, 0.8, 0.9), "#a07850")
