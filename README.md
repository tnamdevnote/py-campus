# Py Campus

A small, stylized low-poly take on Guadalupe Street ("the Drag") next to the UT Austin campus, built in Python with [Ursina](https://www.ursinaengine.org/) (a game engine on top of Panda3D).

Walk down the Drag, step inside the shops, head east down the West Mall to the Main Building and its tower, and chat with a student on the way.

## Run it

You need Python 3.10 or newer and a computer with a normal graphics card (any laptop from the last several years is fine).

```bash
git clone https://github.com/tnamdevnote/py-campus.git
cd py-campus
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

If the window opens and then the game crashes right away, your graphics driver can't handle the lighting shader. Run the unlit version instead:

```bash
python main.py --flat
```

## Controls

| Key | Action |
| --- | --- |
| W A S D | Walk |
| Mouse | Look around |
| Shift | Sprint |
| Space | Jump |
| E | Talk to the NPC (press again for the next line) |
| F5 | Reload `game/config.py` and rebuild the world |
| Tab | Free or lock the mouse cursor |
| Esc | Quit |

## What's in the world

- **Guadalupe Street** running north to south, with lanes, sidewalks, and a crosswalk at the West Mall.
- **The Drag** on the west side: the Co-op, a coffee shop, and a bookstore you can walk into, plus an apartment block.
- **Campus** on the east side: the West Mall walk lined with trees, Battle Hall (enterable), the Texas Union, and the **Main Building** with its tall tower, clock faces, and spire.
- **Alex**, a student standing at the West Mall entrance who'll tell you about the area.

Everything has collision, so you can't walk through walls, trees, or people. Doorways are open, so you can walk into buildings marked `enterable`.

## Adding or changing buildings

Everything you place in the world lives in [`game/config.py`](game/config.py). Edit it while the game is running and press **F5** to see your change without restarting. If you make a typo, the game keeps the old world and prints the error in the terminal.

A building is one dict in the `BUILDINGS` list:

```python
dict(
    name="Drag Coffee",
    x=-18, z=6,                 # center of the footprint (x = east, z = north)
    width=12, depth=12, height=6,
    door="east",                # which way the front door faces
    enterable=True,             # hollow with an open doorway
    color="#e6d2a8", roof="#6d4c3d", trim="#2f5d50",
    sign="COFFEE",
    interior="cafe",            # "shop", "cafe", "books", "classroom", or "empty"
),
```

In the same file you can move the tower (`TOWER`), add trees (`TREES`), lay paths (`PATHS`), change the NPC's lines (`NPCS`), and set where the player starts (`PLAYER_START`). Guadalupe Street runs along `x = 0`; the Drag is at negative `x`, campus at positive `x`.

## Project layout

```
main.py              window, lighting, sky, player, and keys
game/config.py       the world's contents: edit this to iterate
game/buildings.py    turns a building dict into walls, door, windows, sign, furniture
game/scenery.py      ground, Guadalupe Street, paths, trees, the Main Building tower
game/npc.py          the talkable NPC and the dialog box
game/world.py        builds everything from config.py and handles F5 reload
game/style.py        colors and the lit/flat shader switch
```
