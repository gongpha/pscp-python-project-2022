from godot import exposed, export, Vector2, Color, signal
from godot import *


@exposed
class MainMenuRow(HBoxContainer):
    """ Main menu choices """

    on_clicked = signal()

    def _ready(self):
        """
        Called every time the node is added to the scene.
        Initialization here.
        """

        # Get node references
        self.text_node = self.get_node("text")
        self.text_node.connect("gui_input", self, "_on_text_gui_input")
        self.text_node.connect("mouse_entered", self, "_on_text_mouse_entered")
        self.text_node.connect("mouse_exited", self, "_on_text_mouse_exited")
        self.animation: AnimationPlayer = self.get_node("ani")

    def _on_text_gui_input(self, event):
        """ Called when the text is clicked """
        # Check if the mouse was clicked on the text
        if isinstance(event, InputEventMouseButton):  # is the event a mouse button event ?
            if event.button_index == BUTTON_LEFT:  # CLICKING ON A LEFT BUTTON ???
                if not event.pressed:  # Is the button released ? (not pressed)
                    # I was clicked !
                    self.animation.play("click")
                    self.call("emit_signal", "on_clicked")

    def _on_text_mouse_entered(self):
        """ Called when the mouse enters the text """

        # GLOW !
        self.animation.play("glow_start")

    def _on_text_mouse_exited(self):
        """ Called when the mouse exits the text """

        # k, back to normal (stop glowing)
        self.animation.play("glow_end")
