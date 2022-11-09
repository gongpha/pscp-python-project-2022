from godot import exposed, export, Vector3, Quat
from godot import *

# An item object


@exposed
class Item(RigidBody):
    item_name: str = export(str, default="Unnamed")
    price: int = export(int, default=20)

    get_picking: Spatial = None
    picking_rot_input: Vector3
    home_place: Vector3

    def _ready(self):
        self.mode = RigidBody.MODE_CHARACTER  # HL Physics style (no rotation)
        if str(self.name) != "clock":
            # Add item to the group. But not the clock
            self.add_to_group('item')
        self.collision_layer = 0b10
        self.continuous_cd = True  # IDK if this will improve physics

    def _integrate_forces(self, state: PhysicsDirectBodyState):
        # physics things
        # ask gongpha for details
        if not self.has_meta('get_picking'):
            return
        vel = self.get_meta('get_picking').get("global_translation") - self.get("global_translation")
        state.set_linear_velocity(vel * 20)
