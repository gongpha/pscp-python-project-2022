from godot import exposed, Vector3, Array
from godot import *

from .worldspawn import Worldspawn

# THE GAME LOGIC

@exposed
class Game(Control):
    worldspawn : Worldspawn
    rng : RandomNumberGenerator # The number generator for randomizing the item spawn points and more

    def _ready(self):
        # Get the nodes
        self.worldspawn = self.get_node("worldspawn")
        self.ani = self.get_node("ani")

        self.motd = self.get_node("motd")
        self.endday = self.get_node("endday")
        self.endday_day = self.get_node("endday/endday/vbox/day")
        self.motd_day = self.get_node("motd/day")


        # Then, let's initialize the random number generator
        # Random its seed by the current time
        self.rng = RandomNumberGenerator.new()
        self.rng.randomize()

        # Now, LET'S GOOOOOOOOOOOOOOOOO
        self.newday()

    def newday(self) :
        """ Called when a game day starts """
        pass
        