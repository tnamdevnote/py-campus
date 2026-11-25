"""Ground, Guadalupe Street, paths, trees, and the Main Building tower."""
from ursina import Entity, scene
from ursina.models.procedural.cone import Cone
from ursina.models.procedural.cylinder import Cylinder

from . import style
from .style import col, shaded

STREET_HALF_WIDTH = 6
SIDEWALK_WIDTH = 5
STREET_LENGTH = 200


def _flat(parent, x, z, sx, sz, color, y=0.02, thickness=0.04):
    """A flat slab lying on the ground (no collider, the ground holds you up)."""
    return Entity(
        parent=parent, model="cube", position=(x, y, z), scale=(sx, thickness, sz),
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
    Entity(parent=root, model=Cylinder(resolution=6, radius=0.3, height=2.6),
           color=col(style.TRUNK), **shaded())
    Entity(parent=root, model=Cone(resolution=7, radius=2.2, height=3.2), y=2.0,
           color=col(style.LEAF_DARK), **shaded())
    Entity(parent=root, model=Cone(resolution=7, radius=1.6, height=2.6), y=3.6,
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
    root = Entity(parent=parent, position=(spec["x"], 0, spec["z"]), name=spec["name"])
    c, accent, roof = spec["color"], spec["accent"], spec["roof"]
    bw, bd, bh = spec["building_width"], spec["building_depth"], spec["building_height"]
    ts, th, sh = spec["tower_size"], spec["tower_height"], spec["spire_height"]

    def box(pos, scale, color, collider=True):
        return Entity(parent=root, model="cube", position=pos, scale=scale, color=col(color),
                      collider="box" if collider else None, **shaded())

    # Main Building: long north-south block (x is depth, z is width).
    box((0, bh / 2, 0), (bd, bh, bw), c)
    box((0, bh + 0.4, 0), (bd + 1, 0.8, bw + 1), roof)
    # Front steps and portico columns facing west.
    for i in range(3):
        box((-bd / 2 - 1 - i, 0.2 + i * 0.2, 0), (2, 0.4 + i * 0.4, 16 - i * 2), accent)
    for z in range(-6, 7, 3):
        box((-bd / 2 - 1.2, bh * 0.4, z), (0.9, bh * 0.8, 0.9), "#f1e8d2")
    # Tower shaft, set back from the front of the building.
    tx = 2
    box((tx, th / 2, 0), (ts, th, ts), c)
    # Vertical window slots on the shaft.
    for side in (-1, 1):
        for k in (-ts / 4, ts / 4):
            box((tx - ts / 2 - 0.05, bh + (th - bh) / 2, k), (0.1, th - bh - 8, 1.0),
                "#5a5245", collider=False)
            box((tx + k, bh + (th - bh) / 2, side * (ts / 2 + 0.05)), (1.0, th - bh - 8, 0.1),
                "#5a5245", collider=False)
    # Observation deck (wider band) and clock stage.
    box((tx, th + 2, 0), (ts + 2, 4, ts + 2), accent)
    box((tx, th + 5.5, 0), (ts - 1, 3, ts - 1), c)
    for dx, dz, sx, sz in ((-1, 0, 0.1, 3), (1, 0, 0.1, 3), (0, -1, 3, 0.1), (0, 1, 3, 0.1)):
        box((tx + dx * ((ts - 1) / 2 + 0.06), th + 5.5, dz * ((ts - 1) / 2 + 0.06)),
            (sx, 2.4, sz), "#fbf7ee", collider=False)  # clock faces
    box((tx, th + 7.4, 0), (ts, 0.8, ts), roof)
    # Spire: a square pyramid.
    Entity(parent=root, model=Cone(resolution=4, radius=(ts - 2) / 2 * 1.414, height=sh),
           position=(tx, th + 7.8, 0), rotation_y=45, color=col(roof), **shaded())
    # A small gold finial on top.
    Entity(parent=root, model="sphere", position=(tx, th + 7.8 + sh, 0), scale=0.8,
           color=col("#e0b84a"), **shaded())
    return root
