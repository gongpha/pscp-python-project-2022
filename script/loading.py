from godot import exposed, export
from godot import *

from .utils import GDPORT

@exposed
class loading(Control):

    # member variables here, example:
    a = export(int)
    b = export(str, default='foo')

    ril : ResourceInteractiveLoader = None
    delay : int = 0

    bar : ProgressBar

    def _ready(self):
        self.ril = ResourceLoader.load_interactive("res://scene/preload.tscn")
        self.bar = self.get_node("bar")

    def _process(self, delta : float):
        if self.delay < 0.04:
            self.delay += delta
            return
        else:
            self.delay = 0

        poll = self.ril.poll()

        if self.ril == None:
            return
        if poll == ERR_FILE_EOF:
            port : Node = GDPORT(self)
            port.set("preloaded_scene", self.ril.get_resource())
            port.call("load_ok")
        elif poll == OK:
            self.bar.set_value(self.ril.get_stage() / self.ril.get_stage_count())
