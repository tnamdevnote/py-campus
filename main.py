"""Py Campus: a stylized low-poly Guadalupe Street ("the Drag") next to UT Austin.

Run with:  python main.py
Controls:  WASD move, mouse look, Space jump, Shift sprint, E talk,
           F5 reload game/config.py, Tab free/lock the mouse, Esc quit.

If the game crashes right after the window opens, your graphics driver may not
handle the lighting shader. Run  python main.py --flat  instead.
"""
from ursina import (
    AmbientLight,
    DirectionalLight,
    Sky,
    Ursina,
    Vec2,
    application,
    color,
    held_keys,
    mouse,
    window,
)
from ursina.prefabs.first_person_controller import FirstPersonController

from game import config, style
from game.buildings import facing_rotation
from game.npc import DialogBox
from game.world import World

WALK_SPEED = 7
SPRINT_SPEED = 13

app = Ursina(title="Py Campus: Guadalupe Street", borderless=False)
window.color = color.hex("#a9cbe6")
window.exit_button.visible = False
window.fps_counter.enabled = True

# Lighting: a warm sun with shadows plus soft ambient fill.
sun = DirectionalLight(shadows=not style.FLAT, shadow_map_resolution=Vec2(2048, 2048))
sun.color = color.hex("#fff2dc")
sun.look_at((0.6, -1, 0.4))
AmbientLight(color=color.rgba(0.55, 0.57, 0.62, 1))
Sky()

start = config.PLAYER_START
player = FirstPersonController(
    position=(start["x"], 0.5, start["z"]),
    # The player looks down +z, so flip the "door faces" rotation by 180.
    rotation_y=facing_rotation(start.get("facing", "north")) + 180,
    speed=WALK_SPEED,
)

dialog = DialogBox()
world = World(player, dialog)
if not style.FLAT:
    sun.update_bounds()


def input(key):
    if key == "escape":
        application.quit()
    elif key == "f5":
        world.reload()
    elif key == "tab":
        mouse.locked = not mouse.locked


def update():
    player.speed = SPRINT_SPEED if held_keys["shift"] else WALK_SPEED


if __name__ == "__main__":
    app.run()
