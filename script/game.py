from godot import exposed, Vector3, Array
from godot import *

from .worldspawn import Worldspawn
from . import dialogue
from .player import Player

import math

# THE GAME LOGIC

ITEM_PATHS = [
    "res://scene/item/carton.tscn",
    "res://scene/item/tin.tscn"
]


@exposed
class Game(Control):
    worldspawn: Worldspawn
    dialogue_richtext: RichTextLabel
    dialogue_panel: PanelContainer
    crosshair: TextureRect
    linetween: Tween
    adv_hint: Control
    hint: Control

    player: Player

    # The number generator for randomizing the item spawn points and more
    rng: RandomNumberGenerator

    ani: AnimationPlayer  # Play animations that defined inside the editor

    motd: ColorRect  # MOTD (Message of the day) Black screen
    endday: ColorRect  # End day black transparent screen
    endday_day: Label  # The current day text
    motd_day: Label  # The current day in MOTD (THE BIG TEXT)

    hint_day: Label  # Day text
    balance_text: Label  # Balance Text (used $ as a placeholder)

    tscale: float = 0.05  # Time scale
    current_day: int = 1
    balance: int = 200

    ###########################

    order: dict  # Order
    dialogue_lines: list = ["hello"]
    dialogue_repeat: list

    dialogue_animating_chars: bool = False
    holding_confirm: bool = False

    def _ready(self):
        # Get the nodes
        self.worldspawn = self.get_node("worldspawn")
        self.dialogue_richtext = self.get_node("dialogue/rich")
        self.dialogue_panel = self.get_node("dialogue")
        self.crosshair = self.get_node("crosshair")
        self.linetween = self.get_node("linetween")
        self.adv_hint = self.get_node("dialogue/rich/advance")
        self.hint = self.get_node("ui/hint")

        self.player = self.get_node("player")

        self.ani = self.get_node("ani")
        self.ani.connect("animation_finished", self, "_on_ani_finished")

        self.motd = self.get_node("motd")
        self.endday = self.get_node("endday")
        self.endday_day = self.get_node("endday/endday/vbox/day")
        self.motd_day = self.get_node("motd/day")

        self.hint_day = self.get_node("ui/vbox/day")
        self.balance_text = self.get_node("ui/vbox/balance")

        # Then, let's initialize the random number generator
        self.rng = RandomNumberGenerator()

        # Now, LET'S GOOOOOOOOOOOOOOOOO
        self.newday()

    def newday(self):
        """ Called when a game day starts """

        # Random its seed by the current time
        self.rng.randomize()

        # Prepare items on the shelf
        self.prepare_items()

        # Show MOTD screen
        self.motd_day.text = "Day %d" % self.current_day
        self.hint_day.text = self.motd_day.text
        self.endday.hide()
        self.ani.play("motd")
        # Wait for the animation to finish

    def _on_ani_finished(self, ani_name):
        """ Called when an animation is finished """
        ani_name = str(ani_name)
        if ani_name == "motd":
            # MOTD is finished, let's start the day
            Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
            self.set_process(True)  # Start the game loop
            self.rng.randomize()  # Randomize the seed

            # Summon the customer
            self.feed_customer()
        elif ani_name == "customer_enter":
            self.fetch_order()
        elif ani_name == "dialogue_enter":
            self.feed_dialogue()

    def feed_customer(self):
        """ Summon thee customer """

        # TODO : Add a various customer here
        self.ani.play("customer_enter")

    def get_all_item_objects(self):
        """ Get all item objects """
        return self.get_tree().get_nodes_in_group("item")

    def fetch_order(self):
        """ Fetch the order from the customer """

        #
        items = self.get_all_item_objects()

        assert items, "No items in the world"

        order_item = {}

        self.order = {
            'items': order_item,
            'completed': False
        }

        # Randomize an item count
        item_count = self.rng.randi_range(1, 6)
        for _ in range(item_count):
            # Randomize an item
            item: Node = items[self.rng.randi_range(0, len(items) - 1)]
            if item.filename in order_item:
                order_item[item.filename][1] += 1
            else:
                order_item[item.filename] = (item.item_name, 1)

            break

        # Prepare the texts
        order_dialogue = ["%s x%d" % vvv for vvv in order_item.values()]

        self.dialogue_repeat = [', '.join(order_dialogue)]
        self.dialogue_lines = dialogue.greeting + self.dialogue_repeat

        self.show_dialogue()

    def show_dialogue(self):
        """ Show the dialogue """
        # Animate the dialogue
        if not self.dialogue_lines or self.dialogue_panel.visible:
            return  # Already showed the dialogue. SKIP

        self.dialogue_richtext.text = ""  # clear texts
        self.ani.play("dialogue_enter")
        self.player.set("block_pick", True)  # Block player from picking items

        # Hide other UIs
        self.hint.hide()
        self.crosshair.hide()

    def feed_dialogue(self) -> bool:
        """ Advance the dialogue text from the list """
        if not self.dialogue_panel.visible:
            return False  # NOT VISIBLE AT FIRST lets ignore this event

        self.adv_hint.hide()

        if not self.dialogue_lines:  # empty
            self.ani.play("dialogue_exit")
            self.player.block_pick = False
            self.hint.show()
            self.crosshair.show()
            return True
        current: str = self.dialogue_lines.pop(0)
        self.dialogue_richtext.bbcode_text = current
        self.dialogue_richtext.percent_visible = 0.0
        self.dialogue_animating_chars = True
        self.holding_confirm = False
        return True

    def prepare_items(self):
        """
            Place items on the shelf
            Also charge the balance :/
        """
        for area in self.worldspawn.get("itemspawnpoints"):
            # Check if there's an item on the area
            overlapping: Area = area.get_overlapping_bodies()
            if overlapping.size() > 0:
                continue  # Okay, there's an item on the area. SKIP

            # TODO : The items are completely random. Make it more balanced to the order

            path = ITEM_PATHS[self.rng.randi_range(0, len(ITEM_PATHS) - 1)]
            item_scene: PackedScene = ResourceLoader.load(path)
            item: RigidBody = item_scene.instance()
            self.add_child(item)  # Add the item to the world
            self.update_balance(self.balance - item.price)
            item.global_translation = area.global_translation
            item.home_place = area.global_translation

    def update_balance(self, new_b: int):
        self.balance = new_b
        self.balance_text.text = "$" + str(self.balance)

    def _process(self, delta: float):
        """ Called every frame """

        if self.dialogue_animating_chars:
            self.dialogue_richtext.percent_visible += 0.25 / \
                max(0.1, self.dialogue_richtext.bbcode_text.length())
            if self.dialogue_richtext.percent_visible == 1.0:
                # STOP
                self.dialogue_animating_chars = False
                self.adv_hint.show()
