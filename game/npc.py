"""A talkable NPC. Walk up to one and press E; press E again for the next line."""
from ursina import Entity, Text, camera, color, distance_xz, scene

from .buildings import facing_rotation
from .style import col, shaded

TALK_DISTANCE = 4.0


class NPC(Entity):
    def __init__(self, spec, player, dialog, parent=scene):
        super().__init__(
            parent=parent,
            position=(spec["x"], 0, spec["z"]),
            # The body is built facing local -z, same as buildings.
            rotation_y=facing_rotation(spec.get("facing", "south")),
            name=spec["name"],
        )
        self.npc_name = spec["name"]
        self.lines = list(spec["lines"])
        self.player = player
        self.dialog = dialog
        self._home_rotation = self.rotation_y

        skin, shirt = spec.get("skin", "#c68e63"), spec.get("shirt", "#bf5700")
        pants, hair = spec.get("pants", "#2e3a4f"), spec.get("hair", "#2b1d14")

        def part(pos, scale, c, model="cube"):
            Entity(parent=self, model=model, position=pos, scale=scale, color=col(c), **shaded())

        for sx in (-0.17, 0.17):
            part((sx, 0.45, 0), (0.28, 0.9, 0.3), pants)          # legs
        part((0, 1.25, 0), (0.75, 0.75, 0.4), shirt)               # torso
        for sx in (-0.48, 0.48):
            part((sx, 1.2, 0), (0.2, 0.7, 0.22), shirt)           # arms
        part((0, 1.85, 0), (0.45, 0.45, 0.45), skin)               # head
        part((0, 2.1, 0.03), (0.48, 0.12, 0.5), hair)              # hair
        for sx in (-0.1, 0.1):
            part((sx, 1.9, -0.23), (0.07, 0.07, 0.02), "#1a1a1a")  # eyes

        # Collider so the player can't walk through the NPC.
        Entity(parent=self, model="cube", position=(0, 1, 0), scale=(0.9, 2, 0.6),
               collider="box", visible=False)

        self.name_tag = Text(
            parent=self, text=self.npc_name, position=(0, 2.6, 0), origin=(0, 0),
            scale=5, billboard=True, color=color.white,
        )
        self.prompt = Text(
            parent=camera.ui, text=f"Press E to talk to {self.npc_name}", origin=(0, 0),
            y=-0.18, scale=1.1, background=True, enabled=False,
        )
        self.line_index = -1

    @property
    def player_near(self):
        return distance_xz(self.world_position, self.player.world_position) < TALK_DISTANCE

    def update(self):
        near = self.player_near
        talking = self.line_index >= 0
        self.prompt.enabled = near and not talking
        if near:
            self.look_at_2d(self.player.world_position, "y")
            # look_at_2d points +z at the player; the face is on -z.
            self.rotation_y += 180
        elif talking:
            self.end_conversation()
        else:
            self.rotation_y = self._home_rotation

    def input(self, key):
        if key != "e" or not self.player_near:
            return
        self.line_index += 1
        if self.line_index >= len(self.lines):
            self.end_conversation()
            return
        self.dialog.show(self.npc_name, self.lines[self.line_index],
                         last=self.line_index == len(self.lines) - 1)

    def end_conversation(self):
        self.line_index = -1
        self.dialog.hide()

    def on_destroy(self):
        self.end_conversation()
        self.prompt.enabled = False


class DialogBox:
    """A single on-screen dialog panel shared by all NPCs."""

    def __init__(self):
        self.text = Text(
            parent=camera.ui, text="...", origin=(0, 0), y=-0.36, scale=1.15,
            background=True, wordwrap=60, enabled=False,
        )

    def show(self, speaker, line, last=False):
        hint = "E: close" if last else "E: next"
        self.text.text = f"{speaker}: {line}\n<gray>({hint})"
        self.text.create_background()
        self.text.enabled = True

    def hide(self):
        self.text.enabled = False
