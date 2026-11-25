"""Everything you place in the world lives here. Edit this file to iterate.

While the game is running, press F5 to reload this file and rebuild the
buildings, trees, and NPCs without restarting.

Coordinates are in meters (roughly). Axes:
    x  = east (+) / west (-)
    z  = north (+) / south (-)
Guadalupe Street runs north-south along x = 0. The Drag's shops are on the
west side (negative x). The UT campus is on the east side (positive x), with
the West Mall walk running east from the street at z = 0 to the Main Building
and its tower.

Colors are '#rrggbb' hex strings.
"""

# ---------------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------------
# Each building is a dict. Required keys:
#   name      shown on the sign (unless `sign` is given)
#   x, z      center of the building's footprint
#   width     length of the front (door) side
#   depth     front-to-back length
#   height    wall height
#   door      which way the front door faces: "north", "south", "east", "west"
# Optional keys:
#   style        "storefront" (glass shopfront, awning, flat roof),
#                "campus" (terracotta hip roof, tall windows), or
#                "apartment" (flat roof, plain window grid). Default storefront.
#   enterable    True = hollow with an open doorway you can walk through
#   color        wall color
#   roof         roof color
#   trim         color of the sign board, door frame and awning
#   accent       color of the cornice, corners and window frames
#                (default: a lighter version of `color`)
#   sign         text on the sign above the door ("" for no sign)
#   interior     "shop", "cafe", "books", "classroom", or "empty"
#   floors       number of window rows (default from height)
# You can also override any style setting per building, for example
#   awning=False, roof_style="hip", pilasters=False, storefront=True,
#   window_width=1.4, window_height=2.0, awning_color="#2f5d50".
BUILDINGS = [
    # --- The Drag: west side of Guadalupe, doors facing the street (east) ---
    dict(
        name="University Co-op", x=-20, z=-14, width=22, depth=16, height=9,
        door="east", style="storefront", enterable=True,
        color="#b0603f", roof="#6b4a3a", trim="#bf5700", accent="#e8d6b5",
        sign="CO-OP", interior="shop",
    ),
    dict(
        name="Drag Coffee", x=-18, z=6, width=12, depth=12, height=6.5,
        door="east", style="storefront", enterable=True,
        color="#ecdcb8", roof="#7a5a48", trim="#3f7262", sign="COFFEE", interior="cafe",
    ),
    dict(
        name="Half Price Books", x=-20, z=24, width=16, depth=16, height=7.5,
        door="east", style="storefront", enterable=True,
        color="#8eaabd", roof="#4d5c68", trim="#d9a441", accent="#eef2f4",
        sign="BOOKS", interior="books",
    ),
    dict(
        name="Guad Apartments", x=-22, z=46, width=18, depth=18, height=18,
        door="east", style="apartment", enterable=False,
        color="#d8cab4", roof="#6b6660", trim="#8b7a66", sign="",
    ),
    # --- Campus: east side, along the West Mall ---
    dict(
        name="Battle Hall", x=44, z=-20, width=24, depth=14, height=10,
        door="north", style="campus", enterable=True,
        color="#ecdcb6", roof="#c4673f", trim="#9a7b4f", accent="#f7efdc",
        sign="BATTLE HALL", interior="classroom",
    ),
    dict(
        name="Texas Union", x=44, z=22, width=26, depth=16, height=12,
        door="south", style="campus", enterable=False,
        color="#e4cfa4", roof="#c4673f", trim="#bf5700", accent="#f7efdc",
        sign="TEXAS UNION",
    ),
]

# ---------------------------------------------------------------------------
# The Main Building and its tower (east end of the West Mall)
# ---------------------------------------------------------------------------
TOWER = dict(
    name="Main Building",
    x=96, z=0,              # center of the Main Building
    building_width=56,      # north-south length (faces west, toward the mall)
    building_depth=20,      # east-west
    building_height=14,
    tower_size=12,          # square footprint of the tower shaft
    tower_height=60,        # top of the shaft, from the ground
    spire_height=13,
    color="#e2d3ad",
    accent="#c9b27f",
    roof="#b8613f",
)

# ---------------------------------------------------------------------------
# Trees: (x, z) positions. Add or remove freely.
# ---------------------------------------------------------------------------
TREES = (
    # Along the east sidewalk of Guadalupe
    [(9, z) for z in range(-60, 61, 12) if abs(z) > 6]
    # Along the west sidewalk
    + [(-9, z) for z in (-34, -28, 0, 14, 36, 58)]
    # Lining the West Mall
    + [(x, s * 7) for x in range(20, 81, 10) for s in (-1, 1)]
    # Lawn groves
    + [(26, -40), (34, -44), (62, -38), (70, 40), (24, 44), (60, 46)]
)

# ---------------------------------------------------------------------------
# Paths: flat walkways, each (x, z, size_x, size_z)
# ---------------------------------------------------------------------------
PATHS = [
    (46, 0, 70, 8),       # West Mall, Guadalupe to the Main Building
    (44, -10, 4, 12),     # to Battle Hall's door
    (44, 10, 4, 12),      # to the Texas Union's door
    (72, 0, 18, 30),      # plaza in front of the Main Building
]

# ---------------------------------------------------------------------------
# NPCs: press E near one to talk. E again shows the next line.
# ---------------------------------------------------------------------------
NPCS = [
    dict(
        name="Alex", x=15, z=3, facing="west",
        shirt="#bf5700", pants="#2e3a4f", skin="#c68e63", hair="#2b1d14",
        lines=[
            "Hey! Welcome to the Drag. That's Guadalupe Street behind you.",
            "The shops on the west side have fed and caffeinated students for decades.",
            "Head east down the West Mall and you'll hit the Main Building and the Tower.",
            "When the Tower glows orange at night, it means we won. Hook 'em!",
            "The Co-op and the coffee shop across the street are open, go take a look inside.",
        ],
    ),
]

# Where the player starts: (x, z) and the direction they face.
PLAYER_START = dict(x=4, z=-6, facing="east")
