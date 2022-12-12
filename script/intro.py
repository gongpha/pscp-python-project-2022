"""intro scene"""
from godot import exposed, export
from godot import *

from .utils import GDPORT

@exposed
class intro(Control):
    """intro"""

    def _ready(self):
        """
        Called every time the node is added to the scene.
        Initialization here.
        """
        pass


        self.get_node("next").connect("pressed", self, "next")

    def next(self):
        """next"""
        GDPORT(self).call("go_to_game")