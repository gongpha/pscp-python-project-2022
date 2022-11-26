from godot import exposed, Vector2, Array, Color, Vector3
from godot import *

from .utils import linear2db

@exposed
class Settings(Control):
    master_slider : HSlider
    music_slider : HSlider
    fullscreen_box : CheckBox
    vsync_box : CheckBox

    def _ready(self) :
        self.master_slider = self.get_node("vbox/master_label")
        self.music_slider = self.get_node("vbox/music_label")
        self.fullscreen_box = self.get_node("vbox/fullscreen")
        self.vsync_box = self.get_node("vbox/vsync")

        self.master_slider.connect("value_changed", self, "_master_volume_changed")
        self.music_slider.connect("value_changed", self, "_music_volume_changed")
        self.fullscreen_box.connect("toggled", self, "_fullscreen_toggled")
        self.vsync_box.connect("toggled", self, "_vsync_toggled")

    def _master_volume_changed(self, val : float):
        AudioServer.get_bus_index("Master").set_volume_db(linear2db(val))

    def _music_volume_changed(self, val : float):
        AudioServer.get_bus_index("Music").set_volume_db(linear2db(val))

    def _fullscreen_toggled(self, val : bool):
        OS.set_window_fullscreen(val)

    def _vsync_toggled(self, val : bool):
        OS.set_use_vsync(val)