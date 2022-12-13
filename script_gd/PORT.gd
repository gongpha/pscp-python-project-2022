extends Node

var preloaded_scene : PackedScene
var mnmu_scene : PackedScene
var game_scene : PackedScene
var intr_scene : PackedScene

func load_ok() :
	var preloaded : ResourcePreloader = preloaded_scene.instance()
	mnmu_scene = preloaded.get_resource("mainmenu")
	game_scene = preloaded.get_resource("game")
	intr_scene = preloaded.get_resource("intro")
	preloaded.free()
	call_deferred("go_to_mainmenu")

func go_to_mainmenu() :
	#warning-ignore:return_value_discarded
	get_tree().change_scene_to(mnmu_scene)

func go_to_game() :
	#warning-ignore:return_value_discarded
	get_tree().change_scene_to(game_scene)

func go_to_intro() :
	#warning-ignore:return_value_discarded
	get_tree().change_scene_to(intr_scene)

func lerpa(a, b, t) :
	return lerp_angle(a, b, t)
