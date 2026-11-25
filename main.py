"""Py Campus: a stylized low-poly Guadalupe Street ("the Drag") next to UT Austin.

Run with:  python main.py
Controls:  WASD move, mouse look, Space jump, Shift sprint, E talk,
           F5 reload game/config.py, Tab free/lock the mouse, Esc quit.

Add --shadows for real-time sun shadows (needs a proper GPU):
    python main.py --shadows
"""
from PIL import Image
from ursina import (
    AmbientLight,
    DirectionalLight,
    Sky,
    Texture,
    Ursina,
    Vec2,
    application,
    camera,
    color,
    held_keys,
    mouse,
    scene,
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
window.exit_button.visible = False
window.fps_counter.enabled = True



def gradient_sky(top, horizon, height=256):
    """A vertical sky gradient texture, horizon color at the bottom."""
    top, horizon = color.hex(top), color.hex(horizon)
    img = Image.new("RGB", (1, height))
    for y in range(height):
        t = (y / (height - 1)) ** 2.5   # warm band only near the horizon
        c = [round(255 * (top[i] * (1 - t) + horizon[i] * t)) for i in range(3)]
        img.putpixel((0, y), tuple(c))
    return Texture(img)


window.color = color.hex(style.SKY_HORIZON)
Sky(texture=gradient_sky(style.SKY_TOP, style.SKY_HORIZON))
camera.clip_plane_far = 600

# Soft distance fog in the horizon color ties the scene together.
scene.fog_color = color.hex(style.FOG)
scene.fog_density = (90, 450)

if style.LIT:
    sun = DirectionalLight(shadows=True, shadow_map_resolution=Vec2(2048, 2048))
    sun.color = color.hex("#fff0d8")
    sun.look_at((-0.45, -0.8, 0.35))
    AmbientLight(color=color.rgba(0.62, 0.64, 0.7, 1))

start = config.PLAYER_START
player = FirstPersonController(
    position=(start["x"], 0, start["z"]),
    # The player looks down +z, so flip the "door faces" rotation by 180.
    rotation_y=facing_rotation(start.get("facing", "north")) + 180,
    speed=WALK_SPEED,
)

dialog = DialogBox()
world = World(player, dialog)
if style.LIT:
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
