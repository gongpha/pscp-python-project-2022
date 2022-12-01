from godot import Dictionary
from godot import *

from .utils import linear2db

@exposed()
class PYPORT(Node):
    def item_ready(self, item) :
        item.mode = RigidBody.MODE_CHARACTER
        if str(item.name) != "clock":
            item.add_to_group('item') # Add item to the group. But not the clock
        item.collision_layer |= 0b10
        item.continuous_cd = True

    def _ready(self) :
        config = ConfigFile()
        config.load("user://settings.cfg")
        settings = {
            "master_volume" : config.get_value("settings", "master_volume", 1.0),
            "music_volume" : config.get_value("settings", "music_volume", 1.0),
            "fullscreen" : config.get_value("settings", "fullscreen", False),
            "vsync" : config.get_value("settings", "vsync", True)
        }
        self.set("settings", Dictionary(settings))
        self.settings_apply()

    def settings_save(self):
        config = ConfigFile()
        config.load("user://settings.cfg")
        settings = self.get("settings")
        config.set_value("settings", "master_volume", settings.get("master_volume", 1.0))
        config.set_value("settings", "music_volume", settings.get("music_volume", 1.0))
        config.set_value("settings", "fullscreen", settings.get("fullscreen", False))
        config.set_value("settings", "vsync", settings.get("vsync", True))
        config.save("user://settings.cfg")

    def settings_apply(self) :
        settings = self.get("settings")
        AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear2db(settings.get("master_volume", 1.0)))
        AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), linear2db(settings.get("music_volume", 1.0)))
        OS.set_window_fullscreen(settings.get("fullscreen", False))
        OS.set_use_vsync(settings.get("vsync", True))