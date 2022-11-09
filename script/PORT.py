from godot import *

@exposed()
class PYPORT(Node):
	def item_ready(self, item) :
		item.mode = RigidBody.MODE_CHARACTER
		if str(item.name) != "clock":
			item.add_to_group('item') # Add item to the group. But not the clock
		item.collision_layer |= 0b10
		item.continuous_cd = True