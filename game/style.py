"""Shared rendering style: colors and the shader switch.

By default the game uses baked low-poly shading (see meshes.py) with fog,
which runs on any graphics card. `--shadows` on the command line switches to
Ursina's real-time lit shader with sun shadows, which needs a proper GPU.
"""
import sys

from ursina import color as ucolor
from ursina.shaders import lit_with_shadows_shader

LIT = "--shadows" in sys.argv


def shaded():
    """Keyword args that give an Entity the lit, shadow-receiving shader."""
    return {"shader": lit_with_shadows_shader} if LIT else {}


def col(value):
    """Turn a '#rrggbb' string (or an existing Color) into an Ursina Color."""
    if isinstance(value, str):
        return ucolor.hex(value)
    return value


# One cohesive palette: warm limestone and terracotta, sage greens, soft
# asphalt. Buildings pick their own colors in config.py; try to stay close
# to these so everything sits together.
SKY_TOP = "#5b97d6"
SKY_HORIZON = "#f3dcc0"
FOG = "#e9dccb"
GRASS = "#8fb56a"
ROAD = "#55565c"
SIDEWALK = "#d9d1c3"
CURB = "#bdb4a5"
PAVER = "#e0caa3"
LANE_YELLOW = "#f0c54e"
LANE_WHITE = "#f4f1ea"
LIMESTONE = "#ecdcb6"
LIMESTONE_DARK = "#d2bb8b"
TERRACOTTA = "#c4673f"
TRUNK = "#7a5a3e"
LEAF = "#6fa152"
LEAF_DARK = "#4f8a46"
GLASS = "#7fa7c4"
