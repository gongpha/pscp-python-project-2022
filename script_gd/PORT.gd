extends Node

func inte(i : RigidBody, state : PhysicsDirectBodyState) :
	# physics thing
	# ask gongpha for the questions
	if !i.has_meta("get_picking") :
		return
	var vel = i.get_meta("get_picking").get("global_translation") - i.get("global_translation")
	state.set_linear_velocity(vel * 20)