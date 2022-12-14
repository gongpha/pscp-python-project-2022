from godot import exposed, Vector2, Array, GDString, Color
from godot import *

# inspired (?) from half-life WON-edition menu

from .utils import GDPORT

@exposed
class MainMenu(Control):
    """ Main menu """

    def_item_scale = Vector2(0.343, 0.343)
    current_menu_list = {}
    previous_clicked_item_name = None

    item_scene : PackedScene

    title : Label

    def _ready(self):
        """ Ready ! """
        self.item_scene = ResourceLoader.load("res://scene/mainmenu_row.tscn")

        # Setup nodes
        self.pause_mode = Node.PAUSE_MODE_PROCESS

        self.menu_list = self.get_node("menu_list")
        self.tween = self.get_node("tween")
        self.title = self.get_node("title")
        self.title_original = self.title.text
        self.ani = self.get_node("ani")
        self.things = self.get_node("things/inside")
        self.settings_node = self.things.get_node("SETTINGS")

        self.layout()

        if self.has_node("console") :
            self.get_node("console").connect("pressed", self, "go_to_console")

        # Create a default menu
        self.go_to(self.item_list)

    def layout(self) :
        # Customize this to change the menu list
        self.item_list = {
            "Start": {
                'description': "Start the game",
                'callback': self.start
            },
            "Settings": {
                'description': "Change the game settings",
                'callback': self.option_settings
            },
            "Credits": {
                'description': "See the credits",
                'callback': self.option_credits
            },
            "Exit": {
                'description': "Exit the game",
                'callback': self.option_exit
            }
        }

    def _animated_normal(self, attached_scene):
        """ Called when the title animation is done """
        # K, continue the below function (without playing the animation)
        self.go_to(self.current_menu_list, None, attached_scene)

    def _animated_reverse(self, target_item):
        """ Called when the title animation is done """
        # Done ? bring the original title back
        self.title.text = self.title_original
        self.ani.play("re_glow_title")
        self.title.margin_top = 0.0
        self.title.margin_left = 0.5
        self.title.set_anchors_and_margins_preset(Control.LayoutPreset.PRESET_CENTER_TOP)
        self.title.anchor_top = 0.1
        self.title.rect_scale = Vector2(1.0, 1.0)
        # And the item too
        target_item.get_node("text").modulate = Color(1, 1, 1, 1)

    def go_to(self, item_list, current_item=None, attached_scene = None):
        """ Go to a layout """
        self.current_menu_list = item_list

        if current_item != None:
            # Animating options (don't CARE these)
            duration = 0.2
            trans = 1  # Sine
            ease = 1  # Out

            # ANIMATE
            if not isinstance(current_item, GDString):
                # Animate the title
                self.title.text = current_item.get_node("text").text
                self.title.rect_global_position = current_item.rect_global_position
                self.title.rect_scale = self.def_item_scale
                self.tween.interpolate_property(
                    self.title, "margin_left", self.title.margin_left, 0.5, duration, trans, ease)
                self.tween.interpolate_property(
                    self.title, "margin_right", self.title.margin_right, 0.0, duration, trans, ease)
                self.tween.interpolate_property(
                    self.title, "margin_top", self.title.margin_top, 0.0, duration, trans, ease)

                self.tween.interpolate_property(
                    self.title, "anchor_left", self.title.anchor_left, 0.5, duration, trans, ease)
                self.tween.interpolate_property(
                    self.title, "anchor_top", self.title.anchor_top, 0.1, duration, trans, ease)

                self.tween.interpolate_property(
                    self.title, "rect_scale", self.title.rect_scale, Vector2(1.0, 1.0), duration, trans, ease)
                self.tween.start()
                self.tween.connect(
                    "tween_all_completed", self, "_animated_normal", Array([attached_scene]), 4) # ONESHOT
                # NOW, wait for the animation to finish, then continue
                return

        # First, clear the menu
        for node in self.menu_list.get_children():
            node.queue_free()  # Delete the node (item)
        for c in self.things.get_children() :
            if str(c.name) != "SETTINGS" :
                c.queue_free()
        self.settings_node.hide()

        # Load "Menu Items" scene
        

        # Add each item to the menu list
        for name, data in item_list.items():
            row_node = self.item_scene.instance()  # Create a new instance of the item
            row_node.name = name  # Set the name of the item
            row_node.get_node("text").text = name  # Set item name
            # Set item description
            row_node.get_node("description").text = data['description']
            self.menu_list.add_child(row_node)  # ADD IT TO THE LIST !

            # Hey, item.
            # When you are clicked, call the _on_item_clicked function
            # in this class (mainmenu)
            row_node.connect("on_clicked", self,
                             "_on_item_clicked", Array([name, row_node]))
        
        if isinstance(attached_scene, PackedScene):
            # Add "things" here
            new_thing_instance = attached_scene.instance()
            self.things.add_child(new_thing_instance)
            new_thing_instance.raise_()

        elif isinstance(attached_scene, GDString):
            # Show settings
            self.settings_node.show()

        if isinstance(current_item, GDString):
            self.get_tree().create_timer(0.001).connect(
                "timeout", self, "reverse_animation", Array([current_item]), 4
            )

    def reverse_animation(self, current_item):
        """ Reverse the animation (Click a back button) """
        duration = 0.2
        trans = 7  # Cubic
        ease = 2  # In
        self.title.text = current_item
        target_item = self.menu_list.get_node(str(current_item))
        target_item.get_node("text").modulate = Color(1, 1, 1, 0) # Hide that item !

        #self.title.rect_global_position = current_item.rect_global_position
        #self.title.rect_scale = Vector2(0.4, 0.4)
        self.tween.interpolate_property(
            self.title, "rect_global_position", self.title.rect_global_position, target_item.rect_global_position, duration, trans, ease)
        self.tween.interpolate_property(
            self.title, "rect_scale", self.title.rect_scale, self.def_item_scale, duration, trans, ease)
        self.tween.start()
        self.tween.connect(
            "tween_all_completed", self, "_animated_reverse", Array([target_item]), 4) # ONESHOT

    def _on_item_clicked(self, which_key, which_item):
        """ Who got clicked ? """

        # Is title animating ? If yes, don't do anything
        if self.tween.is_active():
            return

        that = self.current_menu_list[str(which_key)]['callback']

        if that == -1:
            # Go back to the DEFAULT main menu
            self.go_to(self.item_list, self.previous_clicked_item_name)
            return

        # Call that thing (Function)
        that(which_item)

        # Hide that item and memorize it
        which_item.get_node("text").modulate = Color(1, 1, 1, 0)
        self.previous_clicked_item_name = which_key

    def option_settings(self, item_that_was_clicked):
        """ Settings """
        self.go_to({
            "Back": {
                'description': "Go back to the main menu",
                'callback': -1
            }
        }, item_that_was_clicked, "SETTINGS")

    def option_credits(self, item_that_was_clicked):
        """ Credits """
        self.go_to({
            "Back": {
                'description': "Go back to the main menu",
                'callback': -1
            }
        }, item_that_was_clicked, ResourceLoader.load("res://scene/sub/credits.tscn"))

    def option_exit(self, item_that_was_clicked):
        """ Exit """
        self.go_to({
            "Yes": {
                'description': "Close the game",
                'callback': self.option_exit_confirmed
            },
            "No": {
                'description': "Go back to the main menu",
                'callback': -1
            }
        }, item_that_was_clicked)

    def option_exit_confirmed(self, _):
        """ Exit (REAL) """
        self.get_tree().quit()

    def start(self, _):
        """ LET'S GOOOOOOOOOO """
        GDPORT(self).call("go_to_intro")

    def go_to_console(self):
        """ Go to the console """
        GDPORT(self).call("go_to_console")
