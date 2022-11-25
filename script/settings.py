from godot import exposed, Vector2, Array, Color, Vector3
from godot import *

@exposed
class Settings(Control):
    master_slider : HSlider
    music_slider : HSlider
    fullscreen_box : CheckBox
    vsync_box : CheckBox

    def _ready(self) :
        master_slider = self.get_node("vbox/master_label")
        music_slider = self.get_node("vbox/music_label")
        fullscreen_box = self.get_node("vbox/fullscreen")
        vsync_box = self.get_node("vbox/vsync")