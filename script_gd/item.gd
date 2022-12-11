extends RigidBody
class_name Item

## The item

export var item_name : String
export var item_conname : String = "<null>"
export var fridge : bool = false

var get_picking : Spatial
var picking_rot_input : Vector3
var prev_point_quat : Quat
var home_place : Vector3

func _ready() :
    PYPORT.call("item_ready", self)

func _integrate_forces(state : PhysicsDirectBodyState) :
    # physics thing
    # ask gongpha for the questions
    if !get_picking :
        return
    var vel := get_picking.global_translation - global_translation
    state.set_linear_velocity(vel * 20)
