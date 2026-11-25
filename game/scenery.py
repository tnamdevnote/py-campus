"""Ground, Guadalupe Street, paths, trees, and the Main Building tower."""
from ursina import Entity, scene
from . import meshes, style
from .style import col, shade_of, shaded

STREET_HALF_WIDTH = 6
SIDEWALK_WIDTH = 5
STREET_LENGTH = 200


def _flat(parent, x, z, sx, sz, color, y=0.02, thickness=0.04):
    """A flat slab lying on the ground (no collider, the ground holds you up)."""
    return Entity(
        parent=parent, model=meshes.cube(), position=(x, y, z), scale=(sx, thickness, sz),
        color=col(color), **shaded(),
    )


def build_ground(parent=scene):
    return Entity(
        parent=parent, model="plane", scale=(400, 1, 400), color=col(style.GRASS),
        collider="box", **shaded(),
    )


def build_street(parent=scene):
    """Guadalupe Street: road, center line, lane dashes, sidewalks, crosswalk."""
    root = Entity(parent=parent, name="Guadalupe St")
    w = STREET_HALF_WIDTH
    _flat(root, 0, 0, w * 2, STREET_LENGTH, style.ROAD, y=0.03)
    # Double yellow center line.
    for x in (-0.15, 0.15):
        _flat(root, x, 0, 0.12, STREET_LENGTH, style.LANE_YELLOW, y=0.06, thickness=0.02)
    # White lane dashes.
    for x in (-w / 2, w / 2):
        for z in range(-STREET_LENGTH // 2, STREET_LENGTH // 2, 6):
            _flat(root, x, z, 0.15, 3, style.LANE_WHITE, y=0.06, thickness=0.02)
    # Sidewalks (raised slightly, like curbs).
    for sx in (-1, 1):
        x = sx * (w + SIDEWALK_WIDTH / 2)
        _flat(root, x, 0, SIDEWALK_WIDTH, STREET_LENGTH, style.SIDEWALK, y=0.06, thickness=0.12)
    # Crosswalk at the West Mall.
    for z in range(-4, 5, 1):
        _flat(root, 0, z, w * 2 - 1, 0.5, style.LANE_WHITE, y=0.065, thickness=0.02)
    return root


def build_paths(paths, parent=scene):
    root = Entity(parent=parent, name="paths")
    for x, z, sx, sz in paths:
        _flat(root, x, z, sx, sz, style.PAVER, y=0.04, thickness=0.06)
    return root


def build_tree(x, z, parent=scene, scale=1.0):
    """A low-poly tree: hexagonal trunk with two stacked cones of leaves."""
    root = Entity(parent=parent, position=(x, 0, z), scale=scale, name="tree")
    Entity(parent=root, model=meshes.cylinder(6), scale=(0.6, 2.6, 0.6),
           color=col(style.TRUNK), **shaded())
    Entity(parent=root, model=meshes.cone(7), y=2.0, scale=(4.4, 3.2, 4.4),
           color=col(style.LEAF_DARK), **shaded())
    Entity(parent=root, model=meshes.cone(7), y=3.6, scale=(3.2, 2.6, 3.2),
           color=col(style.LEAF), **shaded())
    # Invisible trunk collider so you bump into trees instead of walking through.
    Entity(parent=root, model="cube", position=(0, 1.2, 0), scale=(0.7, 2.4, 0.7),
           collider="box", visible=False)
    return root


def build_trees(positions, parent=scene):
    root = Entity(parent=parent, name="trees")
    for i, (x, z) in enumerate(positions):
        # Small deterministic size variation so rows don't look stamped.
        build_tree(x, z, parent=root, scale=0.9 + (i * 37 % 5) * 0.06)
    return root


def build_tower(spec, parent=scene):
    """The Main Building with its tall tower and spire, facing west down the mall."""
    from .buildings import build_building

    root = Entity(parent=parent, position=(spec["x"], 0, spec["z"]), name=spec["name"])
    c, accent, roof = spec["color"], spec["accent"], spec["roof"]
    bw, bd, bh = spec["building_width"], spec["building_depth"], spec["building_height"]
    ts, th, sh = spec["tower_size"], spec["tower_height"], spec["spire_height"]
    trim = "#f7efdc"

    # The Main Building itself uses the same builder as everything else.
    build_building(dict(
        name=spec["name"], x=0, z=0, width=bw, depth=bd, height=bh, door="west",
        style="campus", enterable=False, color=c, roof=roof, trim=accent, accent=trim,
        sign="", window_height=2.4,
    ), parent=root)

    def box(pos, scale, color, collider=True):
        return Entity(parent=root, model=meshes.cube(), position=pos, scale=scale,
                      color=col(color), collider="box" if collider else None, **shaded())

    # Front steps and a portico of columns facing west.
    for i in range(3):
        box((-bd / 2 - 3.2 + i * 0.8, 0.15 + i * 0.3, 0), (2.4 - i * 0.8 + 2, 0.3 + i * 0.6,
            20 - i * 2), accent)
    for z in range(-6, 7, 3):
        Entity(parent=root, model=meshes.cylinder(8), position=(-bd / 2 - 1.4, 1.2, z),
               scale=(0.9, bh - 2.4, 0.9), color=col(trim), collider="box", **shaded())
    box((-bd / 2 - 1.4, bh - 0.9, 0), (1.6, 0.9, 16), trim)              # entablature

    # Tower shaft, set back from the front of the building.
    tx = 2
    box((tx, th / 2, 0), (ts, th, ts), c)
    # Corner piers and vertical window bays on every side.
    for sx in (-1, 1):
        for sz in (-1, 1):
            box((tx + sx * (ts / 2 - 0.3), bh + (th - bh) / 2, sz * (ts / 2 - 0.3)),
                (1.0, th - bh, 1.0), trim, collider=False)
    slot_h = th - bh - 8
    for k in (-ts / 4, 0, ts / 4):
        for side in (-1, 1):
            box((tx + side * (ts / 2 + 0.04), bh + 2 + slot_h / 2, k), (0.1, slot_h, 1.1),
                "#56606a", collider=False)
            box((tx + k, bh + 2 + slot_h / 2, side * (ts / 2 + 0.04)), (1.1, slot_h, 0.1),
                "#56606a", collider=False)
    # Observation deck: a cornice, a ring of columns, and a cap.
    box((tx, th + 0.3, 0), (ts + 2.4, 0.6, ts + 2.4), trim)
    for i in range(-2, 3):
        for x, z in ((i * ts / 5, -(ts / 2 + 0.6)), (i * ts / 5, ts / 2 + 0.6),
                     (-(ts / 2 + 0.6), i * ts / 5), (ts / 2 + 0.6, i * ts / 5)):
            Entity(parent=root, model=meshes.cylinder(6), position=(tx + x, th + 0.6, z),
                   scale=(0.5, 3.2, 0.5), color=col(trim), **shaded())
    box((tx, th + 2.2, 0), (ts - 0.5, 3.2, ts - 0.5), shade_of(c, -0.25), collider=False)
    box((tx, th + 4.1, 0), (ts + 2.4, 0.6, ts + 2.4), trim)
    # Clock stage with a clock face on each side.
    box((tx, th + 6.0, 0), (ts - 1.5, 3.2, ts - 1.5), c)
    half = (ts - 1.5) / 2 + 0.06
    for dx, dz, sx, sz in ((-1, 0, 0.1, 2.4), (1, 0, 0.1, 2.4), (0, -1, 2.4, 0.1), (0, 1, 2.4, 0.1)):
        box((tx + dx * half, th + 6.0, dz * half), (sx, 2.4, sz), "#fbf7ee", collider=False)
        box((tx + dx * (half + 0.05), th + 6.2, dz * (half + 0.05)),
            (max(sx, 0.06) if sx < 1 else 0.15, 0.9, max(sz, 0.06) if sz < 1 else 0.15),
            "#2f2f2f", collider=False)                                   # clock hand
    box((tx, th + 7.8, 0), (ts - 0.5, 0.5, ts - 0.5), trim)
    # Spire: a square pyramid with a gold finial.
    Entity(parent=root, model=meshes.cone(4), position=(tx, th + 8.0, 0), rotation_y=45,
           scale=((ts - 2) * 1.414, sh, (ts - 2) * 1.414), color=col(roof), **shaded())
    Entity(parent=root, model=meshes.blob(1), position=(tx, th + 8.0 + sh, 0), scale=0.5,
           color=col("#e0b84a"), **shaded())
    return root
