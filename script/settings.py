from godot import exposed, Node
from godot import *

from .utils import PYPORT

@exposed
class Settings(Node):
    master_slider : HSlider
    music_slider : HSlider
    fullscreen_box : CheckBox
    vsync_box : CheckBox
    pyport : Node
    settings_dict : dict
    testmusic : AudioStreamPlayer

    def _ready(self) :
        self.master_slider = self.get_node("vbox/master")
        self.music_slider = self.get_node("vbox/music")
        self.fullscreen_box = self.get_node("vbox/fullscreen")
        self.vsync_box = self.get_node("vbox/vsync")

        self.master_slider.connect("value_changed", self, "_master_volume_changed")
        self.music_slider.connect("value_changed", self, "_music_volume_changed")
        self.fullscreen_box.connect("toggled", self, "_fullscreen_toggled")
        self.vsync_box.connect("toggled", self, "_vsync_toggled")

        self.pyport = PYPORT(self)
        self.settings_dict = self.pyport.get("settings")

        self.master_slider.connect("drag_started", self, "_mt_start")
        self.master_slider.connect("drag_ended", self, "_mt_end")

        self.testmaster = self.get_node("vbox/testmaster")

        self.update_settings()

    def _mt_start(self) :
        self.testmaster.play()

    def _mt_end(self, _) :
        self.testmaster.stop()

    def update_settings(self) :
        """ Update the settings from the files """
        self.master_slider.value = self.settings_dict.get("master_volume", 1.0)
        self.music_slider.value = self.settings_dict.get("music_volume", 1.0)
        self.fullscreen_box.pressed = self.settings_dict.get("fullscreen", False)
        self.vsync_box.pressed = self.settings_dict.get("vsync", True)


    def _master_volume_changed(self, val : float):
        self.settings_dict["master_volume"] = val
        self.apply()

    def _music_volume_changed(self, val : float):
        self.settings_dict["music_volume"] = val
        self.apply()

    def _fullscreen_toggled(self, val : bool):
        self.settings_dict["fullscreen"] = val
        self.apply()

    def _vsync_toggled(self, val : bool):
        self.settings_dict["vsync"] = val
        self.apply()

    def apply(self):
        self.pyport.call("settings_apply")
        self.pyport.call("settings_save")
