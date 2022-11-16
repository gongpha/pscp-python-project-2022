from godot import exposed, Vector2, Array, Color
from godot import *

from .worldspawn import Worldspawn
from . import dialogue
from .player import Player
from .utils import lerp

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
    confirmorder: Control
    confirmorder_hbox: HBoxContainer
    pick: Control

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

    tscale: float = 1.0  # Time scale
    current_day: int = 1
    balance: int = 1000

    ###########################

    order = {}  # Order
    dialogue_lines: list = ["hello"]
    dialogue_repeat: list

    dialogue_animating_chars: bool = False
    holding_confirm: bool = False
    confirm_order_value: float = 0.0

    day_counter_item : int = 0

    def _ready(self):
        # Get the nodes
        self.worldspawn = self.get_node("worldspawn")
        self.dialogue_richtext = self.get_node("dialogue/rich")
        self.dialogue_panel = self.get_node("dialogue")
        self.crosshair = self.get_node("crosshair")
        self.linetween = self.get_node("linetween")
        self.adv_hint = self.get_node("dialogue/rich/advance")
        self.hint = self.get_node("ui/hint")
        self.confirmorder = self.get_node("ui/hint/confirmorder")
        self.confirmorder_hbox = self.get_node("ui/hint/confirmorder/hbox")
        self.pick = self.get_node("ui/hint/pick")

        self.player = self.get_node("player")
        self.player.connect("look_front", self, "_on_player_look_front")

        self.ani = self.get_node("ani")
        self.ani.connect("animation_finished", self, "_on_ani_finished")

        self.motd = self.get_node("motd")
        self.endday = self.get_node("endday")
        self.endday_day = self.get_node("endday/endday/vbox/day")
        self.motd_day = self.get_node("motd/day")

        self.hint_day = self.get_node("ui/vbox/day")
        self.balance_text = self.get_node("ui/vbox/balance")

        input_node: Node = self.get_node("input")
        input_node.connect("input", self, "_input_proxy",
                           Array(), Object.CONNECT_DEFERRED)

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
        elif ani_name == "dialogue_exit":
            if self.order:
                if self.order["completed"]:
                    self.ani.play("customer_exit")
                    self.order = None
                    self.dialogue_repeat = []
        elif ani_name == "customer_exit":
            # NEXT
            self.feed_customer()

    def feed_customer(self):
        """ Summon thee customer """

        # TODO : Add a various customer here
        self.ani.play("customer_enter")

    def get_all_item_objects(self) -> list:
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
            while True:
                # Randomize an item
                item: Node = items[self.rng.randi_range(0, len(items) - 1)]
                ttt = order_item.get(item.filename, [item.item_name, 1])
                ttt[1] += 1
                order_item[item.filename] = ttt
                break  # TODO : Fix this

        # Prepare the texts
        order_dialogue = ["%s x%d" % (vvv[0], vvv[1])
                          for vvv in order_item.values()]

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
            self.player.set("block_pick", False)
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
        self.balance = int(new_b)
        self.balance_text.text = "$" + str(self.balance)

    def _process(self, delta: float):
        """ Called every frame """

        if self.holding_confirm:
            self.confirm_order_value += delta * 75
            if self.confirm_order_value >= 100:
                # CONFIRMED !
                self.check_items()
                self.holding_confirm = False
        else:
            if self.confirm_order_value > 0:
                self.confirm_order_value -= 800 * delta
            else:
                self.confirm_order_value = 0.0

        self.confirmorder_hbox.rect_rotation = self.confirm_order_value * \
            math.sin(self.confirm_order_value) * 0.075
        self.confirmorder.rect_scale = Vector2(
            lerp(1.0, 1.5, self.confirm_order_value / 100.0),
            lerp(1.0, 1.5, self.confirm_order_value / 100.0)
        )

        if self.dialogue_animating_chars:
            self.dialogue_richtext.percent_visible += 0.25 / \
                max(0.1, self.dialogue_richtext.bbcode_text.length())
            if self.dialogue_richtext.percent_visible == 1.0:
                # STOP
                self.dialogue_animating_chars = False
                self.adv_hint.show()

        sun = self.worldspawn.get("sun")
        clock_hand_root = self.worldspawn.get("clock_hand_root")

        if clock_hand_root.rotation.z < math.pi * -2.0 :
            self.go_endday()
        else :
            sun.rotate_x(delta * self.tscale)
            clock_hand_root.rotate_z(-delta * 2.0 * self.tscale)

    def check_items(self):
        """ Check items on the counter """
        items = self.get_all_item_objects()
        clone_list = self.order["items"].copy()
        added : list = []
        total: int = 0

        for c in clone_list:
            total += clone_list[c][1]

        item_on_counter: int = 0

        for item in items:
            if item.name == "clock":
                # NO CLOCKS !
                continue
            in_good = self.worldspawn.get("counter_good").overlaps_body(item)

            if not in_good:
                # the item still around in the shop bruh
                continue

            # if it's in the list. mark them
            if item.filename in clone_list:
                clone_list[item.filename][1] -= 1
                if clone_list[item.filename][1] == 0:
                    del clone_list[item.filename]  # no more...
                added.append(item)
            item_on_counter += 1

        if item_on_counter > total + 2:
            self.dialogue_lines = dialogue.order_too_many_items

        if clone_list:
            # not complete shit
            self.dialogue_lines = dialogue.order_not_complete
            clone_list = self.order["items"].copy()
        else:
            # YES
            for a in added:
                self.update_balance(self.balance + (a.price * 1.2))
                a.queue_free()
                self.day_counter_item += 1
            self.dialogue_lines = dialogue.order_ok
            self.order["completed"] = True
        self.dialogue_lines = self.dialogue_lines.copy()
        self.show_dialogue()

    def _input_proxy(self, event):
        """ Proxy for the input event """
        if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
            return

        if event.is_action_pressed("ui_select"):
            self.confirmorder.modulate = Color(1, 1, 0, 1)
            if self.dialogue_animating_chars:
                # animating ? skip it
                self.dialogue_richtext.percent_visible = 1.0
                self.dialogue_animating_chars = False
                self.adv_hint.show()
            else:
                if self.feed_dialogue():
                    return
                self.holding_confirm = True and self.order != None
        elif event.is_action_pressed("repeat"):
            # repeat the dialogue
            self.repeat_dialogue()
            # >:(

        if event.is_action_released("ui_select"):
            self.confirmorder.modulate = Color(1, 1, 1, 1)
            self.holding_confirm = False

        if Input.is_mouse_button_pressed(BUTTON_LEFT):
            self.pick.modulate = Color(1, 1, 0, 1)
        else:
            self.pick.modulate = Color(1, 1, 1, 1)

        self.player._input_proxy(event)

    def repeat_dialogue(self):
        """ Repeat the dialogue """
        if self.dialogue_panel.visible:
            return
        self.dialogue_lines = self.dialogue_repeat.copy()
        self.show_dialogue()

    def _on_player_look_front(self) :
        """ when the player turns away from the shelf """
        if self.player.get("is_look_front") :
            return
        items = self.get_all_item_objects()
        if items.size() < 10 :
            self.prepare_items()

    def go_endday(self):
        """ Emit the end day screen """
        pass # TODO