extends Node
class_name InputProxy

# A node that receives an input event
# Use _input directly in Python is causing a crash right now :(

signal input()

func _input(e) :
	emit_signal("input", e)