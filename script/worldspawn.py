from godot import exposed, Vector3, Array
from godot import *

# just a game world. not a Quake's Worldspawn


@exposed
class Worldspawn(Spatial):
    def _ready(self):
        self.set("counter_good", self.get_node("counter_good"))
        #self.set("counter_bad", self.get_node("counter_bad"))
        self.set("sun", self.get_node("sun"))
        self.set("clock_hand_root", self.get_node("clock/hand/root"))

        # Get all the item spawn points
        # They were used by a game node. For spawning items randomly
        itemspawnpoints = [
            c for c in self.get_node("itemspawner").get_children() if isinstance(c, Area)
        ]
        self.set("itemspawnpoints", Array(itemspawnpoints))
