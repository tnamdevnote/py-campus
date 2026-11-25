"""Faceted, pre-shaded meshes for the low-poly look.

Every triangle gets its own vertices and a vertex color based on which way it
faces, as if lit by a soft sun from the south-east plus sky light from above.
The entity's own color tints that shading. This gives clean, readable
low-poly shading without any lighting shader, so it looks the same on every
graphics card.
"""
from functools import lru_cache

from ursina import Mesh, Vec3, color, load_model
from ursina.models.procedural.cone import Cone
from ursina.models.procedural.cylinder import Cylinder

SUN_DIR = Vec3(0.45, 0.8, -0.35).normalized()   # points toward the sun
SKY_FILL = 0.72    # brightness of faces turned away from the sun
SUN_STRENGTH = 0.34
GROUND_BOUNCE = 0.06


def _shade(normal):
    n = normal.normalized()
    sun = max(0.0, n.dot(SUN_DIR))
    sky = 0.5 + 0.5 * n.y              # faces pointing up see more sky
    b = SKY_FILL * (0.75 + 0.25 * sky) + SUN_STRENGTH * sun + GROUND_BOUNCE * (1 - sky)
    b = min(b, 1.0)
    # Slight warm tint in sunlit faces, cool tint in shade.
    return color.rgba(min(1, b * (1.0 + 0.04 * sun)), b, min(1, b * (1.02 - 0.05 * sun)), 1)


def _triangles(verts, tris):
    """Flatten a mesh's vertices/triangles into a list of corner positions."""
    if not tris:
        return [Vec3(*v) for v in verts]
    if isinstance(tris[0], int):
        return [Vec3(*verts[i]) for i in tris]
    corners = []
    for t in tris:
        if len(t) == 3:
            idx = t
        else:                              # quad -> two triangles
            idx = (t[0], t[1], t[2], t[2], t[3], t[0])
        corners += [Vec3(*verts[i]) for i in idx]
    return corners


def facet(verts, tris=None):
    """Build a Mesh with one vertex per triangle corner and baked shading.

    Works for convex shapes: each face's outward direction is taken from the
    shape's center, and the winding is fixed to what Ursina renders as front.
    """
    corners = _triangles(verts, tris)
    center = sum(corners, Vec3(0, 0, 0)) / max(1, len(corners))
    out_v, out_c, out_n = [], [], []
    for i in range(0, len(corners) - 2, 3):
        a, b, c = corners[i], corners[i + 1], corners[i + 2]
        n = (b - a).cross(c - a)
        if n.length() < 1e-9:
            continue
        n = n.normalized()
        outward = n if n.dot((a + b + c) / 3 - center) > 0 else -n
        # Ursina treats a triangle as front-facing when this cross product points inward.
        if n.dot(outward) > 0:
            b, c = c, b
        shade = _shade(outward)
        out_v += [a, b, c]
        out_c += [shade] * 3
        out_n += [outward] * 3
    return out_v, out_c, out_n


def _mesh(data):
    # Each entity needs its own Mesh (a Mesh can only be attached to one entity).
    v, c, n = data
    return Mesh(vertices=v, colors=c, normals=n, mode="triangle", static=True)


def _box_corners():
    """Unit cube centered on the origin, as 12 triangles."""
    p = [Vec3(x, y, z) for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return p, [list(f) for f in faces]


@lru_cache(maxsize=None)
def _cube_data():
    return facet(*_box_corners())


def cube():
    return _mesh(_cube_data())


@lru_cache(maxsize=None)
def _cone_data(resolution):
    m = Cone(resolution=resolution, radius=0.5, height=1)
    return facet(m.vertices, m.triangles)


def cone(resolution=7):
    """Cone with its base at y=0 and tip at y=1, radius 0.5."""
    return _mesh(_cone_data(resolution))


@lru_cache(maxsize=None)
def _cylinder_data(resolution):
    m = Cylinder(resolution=resolution, radius=0.5, height=1)
    return facet(m.vertices, m.triangles)


def cylinder(resolution=6):
    """Cylinder from y=0 to y=1, radius 0.5."""
    return _mesh(_cylinder_data(resolution))


def blob(seed=0):
    """A lumpy low-poly ball (radius about 0.5) for tree canopies and bushes."""
    return _mesh(_blob_data(seed % 6))


@lru_cache(maxsize=None)
def _blob_data(seed):
    import random

    rnd = random.Random(seed)
    sphere = load_model("icosphere")
    verts = []
    cache = {}
    for v in sphere.vertices:
        key = (round(v[0], 4), round(v[1], 4), round(v[2], 4))
        if key not in cache:
            k = 1 + rnd.uniform(-0.12, 0.12)
            cache[key] = Vec3(v[0] * k, v[1] * k * 0.85, v[2] * k)
        verts.append(cache[key])
    return facet(verts, sphere.triangles)
