extends RigidBody
class_name Item

## The item

export var item_name : String
export var item_conname : String = "<null>"
export var fridge : bool = false
export var impact : AudioStream

var get_picking : Spatial
var picking_rot_input : Vector3
var prev_point_quat : Quat
var home_place : Vector3

var last_contact : Object

func _ready() :
    PYPORT.call("item_ready", self)
    contact_monitor = true
    contacts_reported = 1

func _integrate_forces(state : PhysicsDirectBodyState) :
    # physics thing
    # ask gongpha for the questions
    if state.get_contact_count() == 0:
        last_contact = null

    for i in state.get_contact_count() :
        #var contact := state.get_contact_collider_object(i)
        if last_contact == state.get_contact_collider_object(i) :
            break
        #print(state.get_contact_impulse(i))
        #if state.get_contact_collider_velocity_at_position(i).length() > 0.33 :
        play_impact()
        last_contact = state.get_contact_collider_object(i)

    if !get_picking :
        return
    var vel := get_picking.global_translation - global_translation
    state.set_linear_velocity(vel * 20)

func play_impact():
    var s := AudioStreamPlayer3D.new()
    s.global_transform = global_transform
    s.stream = impact
    s.unit_db = 40
    add_child(s)
    s.play()
    s.connect("finished", s, "queue_free")