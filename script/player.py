from godot import exposed, export, Vector3
from godot import *
import math

from .utils import clamp

# The player body


@exposed
class player(StaticBody):
    # nodes
    camera: Camera
    ray: RayCast
    itemfront: Position3D

    sens = 100 * 0.5  # Sensitivity of the mouse

    picking = None
    block_pick: bool = False
    old_rot_y: float = 1.0
    is_look_front: bool = False

    look_front = signal()

    def _ready(self):
        self.camera = self.get_node("camera")
        self.ray = self.get_node("camera/ray")
        self.itemfront = self.get_node("camera/itemfront")

        input_node: Node = self.get_node("input")

        input_node.connect("input", self, "_input_proxy")
        Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

    def _input_proxy(self, event):
        if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
            return

        # Looking
        if isinstance(event, InputEventMouseMotion):
            rel = -event.relative / math.pi / self.sens
            self.rotate(Vector3(0, 1, 0), rel.x)
            self.camera.rotate(Vector3(1, 0, 0), rel.y)

            self.camera.rotation_degrees.x = clamp(
                self.camera.rotation_degrees.x, -90.0, 90.0
            )

            new_look = abs(self.rotation_degrees.y) < 45
            if new_look != self.is_look_front:
                if new_look:
                    self.call("emit_signal", "look_front")
                self.is_look_front = new_look

        # Picking (left click)
        elif isinstance(event, InputEventMouseButton):
            if event.pressed:
                if event.button_index == BUTTON_LEFT and not self.block_pick:
                    # Check if the ray hit something
                    self.ray.force_raycast_update()
                    that_thing = self.ray.get_collider()
                    # TODO : ITEMS !
                    # if not that_thing is Item :
                    #    return

                    self.picking = that_thing
                    self.picking.get_picking = self.itemfront
                    self.picking.sleeping = False
                    self.picking.prev_point_quat = self.itemfront.global_transform.basis.get_rotation_quat()
            else:
                if self.picking:
                    self.picking.get_picking = None
                    self.picking = None  # release
