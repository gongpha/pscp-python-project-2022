from godot import exposed, Vector3, Array
from godot import *

from .worldspawn import Worldspawn

# THE GAME LOGIC

@exposed
class Game(Control):
    worldspawn : Worldspawn
    rng : RandomNumberGenerator # The number generator for randomizing the item spawn points and more

    ani : AnimationPlayer # Play animations that defined inside the editor

    motd : ColorRect # MOTD (Message of the day) Black screen
    endday : ColorRect # End day black transparent screen
    endday_day : Label # The current day text
    motd_day : Label # The current day in MOTD (THE BIG TEXT)

    hint_day : Label # Day text
    balance_text : Label # Balance Text (used $ as a placeholder)

    tscale : float = 0.05 # Time scale
    current_day : int = 1
    balance : int = 200

    def _ready(self):
        # Get the nodes
        self.worldspawn = self.get_node("worldspawn")
        self.ani = self.get_node("ani")

        self.motd = self.get_node("motd")
        self.endday = self.get_node("endday")
        self.endday_day = self.get_node("endday/endday/vbox/day")
        self.motd_day = self.get_node("motd/day")

        self.hint_day = self.get_node("ui/vbox/day")
        self.balance_text = self.get_node("ui/vbox/balance")


        # Then, let's initialize the random number generator
        # Random its seed by the current time
        self.rng = RandomNumberGenerator()
        self.rng.randomize()

        # Now, LET'S GOOOOOOOOOOOOOOOOO
        self.newday()

    def newday(self) :
        """ Called when a game day starts """

        # Show MOTD screen
        self.motd_day.text = "Day %d" % self.current_day
        self.hint_day.text = self.motd_day.text
        self.endday.hide()
        self.ani.play("motd")
        # Wait for the animation to finish