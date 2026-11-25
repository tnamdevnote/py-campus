"""Shared rendering style: colors and the shader switch.

`--flat` on the command line turns off the lit shader and shadows, for
graphics drivers that can't compile it (see README).
"""
import sys

from ursina import color as ucolor
from ursina.shaders import lit_with_shadows_shader

FLAT = "--flat" in sys.argv


def shaded():
    """Keyword args that give an Entity the lit, shadow-receiving shader."""
    return {} if FLAT else {"shader": lit_with_shadows_shader}


def col(value):
    """Turn a '#rrggbb' string (or an existing Color) into an Ursina Color."""
    if isinstance(value, str):
        return ucolor.hex(value)
    return value


# Palette used by the scenery. Buildings pick their own colors in config.py.
GRASS = "#7aa95c"
ROAD = "#4a4a50"
SIDEWALK = "#c9c3b6"
PAVER = "#d6c3a0"
LANE_YELLOW = "#e8c547"
LANE_WHITE = "#f2f0ea"
LIMESTONE = "#e2d3ad"
LIMESTONE_DARK = "#c9b27f"
TERRACOTTA = "#b8613f"
TRUNK = "#6b4a32"
LEAF = "#4f8a3c"
LEAF_DARK = "#3e7431"
GLASS = "#5f86a6"
