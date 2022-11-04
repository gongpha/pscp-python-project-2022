extends Node
class_name InputProxy

# A node that receives an input event
# Use _input directly in Python is causing a crash right now :(

signal input()

func _input(e) :
	call_deferred("emit_signal", "input", e)