"""Campus landmarks for the Guadalupe Street ("the Drag") scene.

Simple box-and-color stand-ins for:

* the UT Tower (Main Building) in the background, east of Guadalupe
* the University Co-op on the west side of Guadalupe
* the West Mall entrance on the campus (east) side of Guadalupe
* sidewalks along both sides of Guadalupe, plus the West Mall walk

Coordinates
-----------
Every landmark is stored at its real-world latitude/longitude and projected
into scene space, so it lines up with map (OSM) data projected the same way.
Scene space follows Ursina's axes: 1 unit = 1 metre, +x = east, +z = north,
+y = up. ``ORIGIN`` is the point that becomes (0, 0, 0); pass your own
``origin`` or ``project`` function to ``build_landmarks`` if the street
layout uses a different one.

Usage from the scene::

    from landmarks import build_landmarks
    build_landmarks()            # after app = Ursina()

Run ``python landmarks.py`` for a standalone preview.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Iterable

# Guadalupe St & W 24th St. The street-layout code should use the same
# origin (or pass its own projection into build_landmarks).
ORIGIN = (30.28737, -97.74200)

EARTH_RADIUS_M = 6_371_000.0

LatLon = tuple[float, float]
Projector = Callable[[float, float], tuple[float, float]]


def latlon_to_xz(lat: float, lon: float, origin: LatLon = ORIGIN) -> tuple[float, float]:
    """Project lat/lon to local metres (x east, z north) around ``origin``.

    Equirectangular projection; accurate to well under a metre over the
    few hundred metres this scene covers.
    """
    lat0, lon0 = origin
    x = math.radians(lon - lon0) * EARTH_RADIUS_M * math.cos(math.radians(lat0))
    z = math.radians(lat - lat0) * EARTH_RADIUS_M
    return x, z


# --------------------------------------------------------------------------
# Data layer (no Ursina import needed, so it can be tested on its own)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Part:
    """One box of a landmark, relative to the landmark's ground position.

    ``offset`` is (x, y, z) of the box's bottom-centre; ``size`` is
    (width x, height y, depth z), all in metres.
    """

    offset: tuple[float, float, float]
    size: tuple[float, float, float]
    color: str  # hex, e.g. "#c9a46a"


@dataclass(frozen=True)
class Landmark:
    name: str
    lat: float
    lon: float
    parts: tuple[Part, ...] = field(default_factory=tuple)
    rotation_y: float = 0.0  # degrees, clockwise seen from above (Ursina)


# Palette
LIMESTONE = "#d8c7a0"
LIMESTONE_DARK = "#bfa97c"
TERRACOTTA = "#b5563a"
BURNT_ORANGE = "#bf5700"
BRICK = "#9c5a3c"
GLASS = "#5d7f99"
CONCRETE = "#b9b6ae"
PAVER = "#c7b299"
GRASS = "#6f9a4a"
WHITE = "#f2efe8"


def _ut_tower() -> Landmark:
    # Main Building + 307 ft (94 m) tower. The tower sits on the
    # north-centre of the Main Building, facing south toward the South Mall.
    parts = (
        # Main Building: long east-west block.
        Part((0, 0, 0), (90, 20, 40), LIMESTONE),
        Part((0, 20, 0), (92, 2, 42), TERRACOTTA),  # tile roof band
        # Tower shaft.
        Part((0, 0, 8), (19, 76, 19), LIMESTONE),
        # Observation deck / colonnade.
        Part((0, 76, 8), (21, 8, 21), LIMESTONE_DARK),
        # Clock stage and cap.
        Part((0, 84, 8), (15, 6, 15), LIMESTONE),
        Part((0, 90, 8), (9, 4, 9), TERRACOTTA),
        # Clock faces (thin plates on each side).
        Part((0, 85, 8 - 7.6), (6, 4, 0.3), WHITE),
        Part((0, 85, 8 + 7.6), (6, 4, 0.3), WHITE),
        Part((-7.6, 85, 8), (0.3, 4, 6), WHITE),
        Part((7.6, 85, 8), (0.3, 4, 6), WHITE),
    )
    return Landmark("UT Tower", 30.28613, -97.73937, parts)


def _university_coop() -> Landmark:
    # 2246 Guadalupe, west side of the street, storefront facing east.
    parts = (
        Part((0, 0, 0), (32, 14, 40), BRICK),
        Part((16.2, 0, 0), (0.4, 9, 34), GLASS),  # storefront windows
        Part((17.5, 9.5, 0), (3, 0.6, 36), BURNT_ORANGE),  # awning
        Part((16.4, 10.5, 0), (0.4, 3, 18), BURNT_ORANGE),  # sign band
    )
    return Landmark("University Co-op", 30.28555, -97.74231, parts)


def _west_mall_entrance() -> Landmark:
    # Entrance from Guadalupe onto the West Mall, east side of the street.
    # Two limestone pylons with low walls and planters framing the walk.
    parts = (
        Part((0, 0, -9), (2.5, 4.5, 2.5), LIMESTONE),
        Part((0, 0, 9), (2.5, 4.5, 2.5), LIMESTONE),
        Part((0, 4.5, -9), (3, 0.5, 3), LIMESTONE_DARK),
        Part((0, 4.5, 9), (3, 0.5, 3), LIMESTONE_DARK),
        Part((6, 0, -12), (12, 1, 3), LIMESTONE),  # low wall / bench
        Part((6, 0, 12), (12, 1, 3), LIMESTONE),
        Part((6, 1, -12), (11, 0.3, 2.4), GRASS),  # planters
        Part((6, 1, 12), (11, 0.3, 2.4), GRASS),
    )
    return Landmark("West Mall entrance", 30.28555, -97.74183, parts)


LANDMARKS: tuple[Landmark, ...] = (
    _ut_tower(),
    _university_coop(),
    _west_mall_entrance(),
)


# Guadalupe centreline, roughly 21st St to 24th St (south to north).
GUADALUPE_SOUTH = (30.28330, -97.74203)
GUADALUPE_NORTH = (30.28737, -97.74200)
ROAD_WIDTH = 18.0      # curb to curb, metres
SIDEWALK_WIDTH = 4.5
SIDEWALK_HEIGHT = 0.15  # curb height


@dataclass(frozen=True)
class Slab:
    """A flat walkway: a box centred at (x, z) on the ground."""

    name: str
    x: float
    z: float
    width: float   # along x before rotation
    length: float  # along z before rotation
    rotation_y: float
    color: str
    height: float = SIDEWALK_HEIGHT


def _strip_between(name: str, a: tuple[float, float], b: tuple[float, float],
                   width: float, color: str) -> Slab:
    (ax, az), (bx, bz) = a, b
    dx, dz = bx - ax, bz - az
    length = math.hypot(dx, dz)
    # Ursina rotation_y is clockwise from +z when viewed from above.
    rot = math.degrees(math.atan2(dx, dz))
    return Slab(name, (ax + bx) / 2, (az + bz) / 2, width, length, rot, color)


def sidewalks(project: Projector) -> list[Slab]:
    """Sidewalks along both sides of Guadalupe and the West Mall walk."""
    s = project(*GUADALUPE_SOUTH)
    n = project(*GUADALUPE_NORTH)
    dx, dz = n[0] - s[0], n[1] - s[1]
    length = math.hypot(dx, dz)
    # Unit vector pointing east, perpendicular to the street.
    ex, ez = dz / length, -dx / length
    off = ROAD_WIDTH / 2 + SIDEWALK_WIDTH / 2

    slabs = []
    for side, sign in (("west", -1), ("east", 1)):
        a = (s[0] + sign * ex * off, s[1] + sign * ez * off)
        b = (n[0] + sign * ex * off, n[1] + sign * ez * off)
        slabs.append(_strip_between(f"Guadalupe sidewalk ({side})", a, b,
                                    SIDEWALK_WIDTH, CONCRETE))

    # West Mall: paved walk from the entrance east to the Main Building.
    entrance = next(l for l in LANDMARKS if l.name == "West Mall entrance")
    tower = next(l for l in LANDMARKS if l.name == "UT Tower")
    start = project(entrance.lat, entrance.lon)
    tx, tz = project(tower.lat, tower.lon)
    end = (tx - 45, start[1])  # stop at the Main Building's west face
    slabs.append(_strip_between("West Mall walk", start, end, 16, PAVER))
    return slabs


# --------------------------------------------------------------------------
# Ursina layer
# --------------------------------------------------------------------------

def build_landmarks(parent=None, origin: LatLon = ORIGIN,
                    project: Projector | None = None,
                    landmarks: Iterable[Landmark] = LANDMARKS,
                    include_sidewalks: bool = True):
    """Create the landmark entities in the current Ursina scene.

    Call after ``Ursina()`` has been created. Returns the root Entity, whose
    children are one Entity per landmark (plus one holding the sidewalks).

    ``project`` maps (lat, lon) -> (x, z) in metres; it defaults to
    ``latlon_to_xz`` around ``origin``. Pass the street layout's own
    projection here so everything shares one coordinate system.
    """
    from ursina import Entity, color, scene

    if project is None:
        def project(lat, lon):
            return latlon_to_xz(lat, lon, origin)

    root = Entity(name="landmarks", parent=parent or scene)

    for lm in landmarks:
        x, z = project(lm.lat, lm.lon)
        group = Entity(name=lm.name, parent=root, position=(x, 0, z),
                       rotation_y=lm.rotation_y)
        for p in lm.parts:
            ox, oy, oz = p.offset
            w, h, d = p.size
            Entity(parent=group, model="cube", color=color.hex(p.color),
                   position=(ox, oy + h / 2, oz), scale=(w, h, d),
                   collider="box")

    if include_sidewalks:
        walks = Entity(name="sidewalks", parent=root)
        for s in sidewalks(project):
            Entity(name=s.name, parent=walks, model="cube",
                   color=color.hex(s.color),
                   position=(s.x, s.height / 2, s.z),
                   scale=(s.width, s.height, s.length),
                   rotation_y=s.rotation_y, collider="box")

    return root


def _preview():
    """Standalone preview: ground, a stand-in road, and the landmarks."""
    from ursina import Ursina, Entity, EditorCamera, DirectionalLight, Sky, color

    app = Ursina(title="Py Campus: landmarks preview")
    Sky()
    DirectionalLight().look_at((1, -1, 1))
    Entity(model="plane", scale=800, color=color.hex("#7a8f5a"))

    s = latlon_to_xz(*GUADALUPE_SOUTH)
    n = latlon_to_xz(*GUADALUPE_NORTH)
    road = _strip_between("Guadalupe (preview)", s, n, ROAD_WIDTH, "#3b3b3b")
    Entity(model="cube", color=color.hex(road.color),
           position=(road.x, 0.02, road.z), scale=(road.width, 0.04, road.length),
           rotation_y=road.rotation_y)

    build_landmarks()

    # Stand on Guadalupe looking east toward the Tower.
    x, z = latlon_to_xz(30.28555, -97.74200)
    EditorCamera(position=(x, 2, z), rotation=(-10, 80, 0))
    app.run()


if __name__ == "__main__":
    _preview()
