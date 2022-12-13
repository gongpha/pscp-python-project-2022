extends AudioStreamPlayer

func _ready() :
	connect("finished", self, "_add_pitch")

func _add_pitch() :
	pitch_scale += 0.1
	play()