"""Builds the whole scene from config.py, and rebuilds it on demand (F5)."""
import importlib
import traceback

from ursina import Entity, destroy, print_on_screen

from . import config as config_module
from .buildings import build_building
from .npc import NPC
from .scenery import build_ground, build_paths, build_street, build_tower, build_trees


class World:
    def __init__(self, player, dialog):
        self.player = player
        self.dialog = dialog
        self.config = config_module
        # Fixed parts that never change.
        build_ground()
        build_street()
        self.root = None
        self.npcs = []
        self.build()

    def build(self):
        cfg = self.config
        self.root = Entity(name="world")
        build_paths(cfg.PATHS, parent=self.root)
        build_trees(cfg.TREES, parent=self.root)
        build_tower(cfg.TOWER, parent=self.root)
        for spec in cfg.BUILDINGS:
            build_building(spec, parent=self.root)
        self.npcs = [NPC(spec, self.player, self.dialog) for spec in cfg.NPCS]

    def clear(self):
        for npc in self.npcs:
            destroy(npc)
        self.npcs = []
        if self.root:
            destroy(self.root)
        self.root = None

    def reload(self):
        """Re-read config.py and rebuild. Keeps the old world if the file has an error."""
        try:
            new_config = importlib.reload(self.config)
        except Exception:
            traceback.print_exc()
            print_on_screen("config.py has an error, see the terminal", duration=4)
            return
        self.config = new_config
        self.clear()
        try:
            self.build()
        except Exception:
            traceback.print_exc()
            print_on_screen("Couldn't build the world, see the terminal", duration=4)
            return
        print_on_screen(f"Reloaded {len(new_config.BUILDINGS)} buildings", duration=2)
