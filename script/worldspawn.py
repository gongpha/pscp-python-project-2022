from godot import exposed, Vector3, Array
from godot import *

# just a game world. not a Quake's Worldspawn


@exposed
class Worldspawn(Spatial):
    sun: DirectionalLight  # The sun. (Just a light source)
    # The 3D root of the clock hand. For rotating the clock hand by the time
    clock_hand_root: Spatial

    # The list of item spawn points that placed in the world (Areas)
    itemspawnpoints = []

    def _ready(self):
        self.set("counter_good", self.get_node("counter_good"))
        self.set("counter_bad", self.get_node("counter_bad"))
        self.sun = self.get_node("sun")
        self.clock_hand_root = self.get_node("clock/hand")

        # Get all the item spawn points
        # They were used by a game node. For spawning items randomly
        for c in self.get_node("itemspawner").get_children():
            if isinstance(c, Area):
                self.itemspawnpoints.append(c)
        self.set("itemspawnpoints", Array(self.itemspawnpoints))
