from godot import exposed, export, Vector3
from godot import *

# An item object

@exposed
class Item(StaticBody):
    item_name : str = export(str, default="Unnamed")
    price : int = export(int, default=20)

    def _ready(self) :
        self.mode = RigidBody.MODE_CHARACTER # HL Physics style (no rotation)
        if self.name != "clock":
            self.add_to_group('item') # Add item to the group. But not the clock
        self.collision_layer |= 0b10
        self.continuous_cd = True # IDK if this will improve physics