extends Node

const MNMU_SCENE := preload("res://scene/mainmenu.tscn")
const GAME_SCENE := preload("res://scene/game.tscn")

func go_to_mainmenu() :
	get_tree().change_scene_to(MNMU_SCENE)

func go_to_game() :
	get_tree().change_scene_to(GAME_SCENE)

func inte(i : RigidBody, state : PhysicsDirectBodyState) :
	# physics thing
	# ask gongpha for the questions
	if !i.has_meta("get_picking") :
		return
	var vel = i.get_meta("get_picking").get("global_translation") - i.get("global_translation")
	state.set_linear_velocity(vel * 20)