from godot import exposed, Vector2, Array, Color, Vector3
from godot import *

from .worldspawn import Worldspawn
from . import dialogue
from .player import Player
from .utils import lerp

import math
import random

# THE GAME LOGIC

ITEM_PATHS = [
    "res://scene/item/carton1.tscn",
    "res://scene/item/carton2.tscn",
    "res://scene/item/carton3.tscn",
    "res://scene/item/tin1.tscn",
    "res://scene/item/tin2.tscn",
    "res://scene/item/tin3.tscn",
    "res://scene/item/sachet1.tscn",
    "res://scene/item/sachet2.tscn",
    "res://scene/item/sachet3.tscn"
]

MAX_EACH_ITEM_COUNT = 3
MIN_CUSTOMERS = 10
MAX_CUSTOMERS = 30
CUSTOMER_TIMER = 15.0

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

    sun : DirectionalLight
    clock_hand_root : Spatial

    player: Player

    # The number generator for randomizing the item spawn points and more
    rng: RandomNumberGenerator

    ani: AnimationPlayer  # Play animations that defined inside the editor

    motd: ColorRect  # MOTD (Message of the day) Black screen
    endday: ColorRect  # End day black transparent screen
    endday_day: Label  # The current day text

    won_left: Label
    won_right: Label
    streak_left: Label
    streak_right: Label
    rank: Label

    motd_day: Label  # The current day in MOTD (THE BIG TEXT)

    hint_day: Label  # Day text
    balance_text: Label  # Balance Text (used $ as a placeholder)
    customer_counter: Label # Customer Label

    sold: Label
    add_bal: Label
    streak_label: Label

    counting : bool = False
    #tscale: float = 0.04  # Time scale
    current_day: int = 1
    balance: int = 1000

    ###########################

    order = None  # Order
    dialogue_lines: list = ["hello"]
    dialogue_repeat: list

    dialogue_animating_chars: bool = False
    holding_confirm: bool = False
    confirm_order_value: float = 0.0

    day_counter_item : int = 0

    customer_count : int = 0

    who : int = 0
    streak : int = 0

    pausemenu : Control

    def _ready(self):
        self.pause_mode = Node.PAUSE_MODE_PROCESS

        # Get the nodes
        self.worldspawn = self.get_node("worldspawn")

        self.sun = self.worldspawn.get("sun")
        self.clock_hand_root = self.worldspawn.get("clock_hand_root")

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
        #self.player.connect("look_front", self, "_on_player_look_front")
        self.player.pause_mode = Node.PAUSE_MODE_STOP

        self.ani = self.get_node("ani")
        self.ani.connect("animation_finished", self, "_on_ani_finished")
        self.ani.pause_mode = Node.PAUSE_MODE_STOP

        self.motd = self.get_node("motd")
        self.endday = self.get_node("endday")

        self.endday_day = self.get_node("endday/endday/vbox/hbox/day")
        self.won_left = self.get_node("endday/endday/vbox/won/a")
        self.won_right = self.get_node("endday/endday/vbox/won/b")
        self.streak_left = self.get_node("endday/endday/vbox/streak/a")
        self.streak_right = self.get_node("endday/endday/vbox/streak/b")
        self.rank = self.get_node("endday/endday/vbox/rank/b")

        self.sold = self.get_node("endday/endday/vbox/sold")
        self.add_bal = self.get_node("endday/endday/vbox/add_bal")
        self.streak_label = self.get_node("ui/vbox/streak")

        self.motd_day = self.get_node("motd/day")

        self.hint_day = self.get_node("ui/vbox/day")
        self.balance_text = self.get_node("ui/vbox/balance")
        self.customer_counter = self.get_node("ui/vbox/customer_counter")

        customer = self.get_node("customer")
        customer.pause_mode = Node.PAUSE_MODE_STOP

        self.pausemenu = self.get_node("pausemenu")
        self.pausemenu.connect("on_resume", self, "toggle_pausemenu")
        self.pausemenu.hide()
        self.pausemenu.pause_mode = Node.PAUSE_MODE_PROCESS

        input_node: Node = self.get_node("input")
        input_node.connect("input", self, "_input_proxy",
                           Array(), Object.CONNECT_DEFERRED)

        next_button = self.get_node("endday/endday/vbox/continue")
        next_button.connect("pressed", self, "_on_next_button_pressed")

        # Then, let's initialize the random number generator
        self.rng = RandomNumberGenerator()

        # Now, LET'S GOOOOOOOOOOOOOOOOO
        self.newday()

    def toggle_pausemenu(self):
        if self.get_tree().paused:
            self.get_tree().paused = False
            self.pausemenu.reset()
            self.pausemenu.hide()
            if self.is_processing():
                Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
        else:
            self.pausemenu.show()
            Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
            self.get_tree().paused = True

    def newday(self):
        """ Called when a game day starts """

        # Reset these
        #self.sun.rotation = Vector3()
        self.reset_clock()

        # Random its seed by the current time
        self.rng.randomize()

        # Prepare items on the shelf
        self.prepare_items()

        self.update_customer_count(0)
        self.update_streak_count(0)
        self.won = 0

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
                if self.order["status"] != "pending":
                    self.ani.play("customer_exit")
                    self.order = None
                    self.dialogue_repeat = []
                else :
                    self.counting = True
        elif ani_name == "customer_exit":
            # NEXT
            self.update_customer_count(self.customer_count + 1)
            if self.customer_count >= MAX_CUSTOMERS:
                self.go_endday() # end
            else :
                self.feed_customer() # NEXT !

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
            'status': "pending",
        }

        available = {}

        for item in items:
            ttt = available.get(item.filename, [item.item_name, 0])
            ttt[1] += 1
            available[item.filename] = ttt

        keyshuffled = list(available.keys())
        random.shuffle(keyshuffled)
        item_count = self.rng.randi_range(1, len(keyshuffled) // 2)
        keyshuffled = keyshuffled[:item_count]
        
        for kkk in keyshuffled:
            order_item[kkk] = [
                available[kkk][0],
                self.rng.randi_range(1, available[kkk][1])
            ]

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

    def update_customer_count(self, ccc : int):
        self.customer_count = ccc
        self.customer_counter.text = "Encountered %d Customers" % ccc

    def update_streak_count(self, ccc : int):
        self.streak = ccc
        self.streak_label.text = "%d STREAK" % ccc

    def _process(self, delta: float):
        """ Called every frame """

        if self.get_tree().paused:
            return

        if self.holding_confirm:
            self.confirm_order_value += delta * 125
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

        self.update_clock(delta)

    def reset_clock(self):
        self.clock_hand_root.rotation = Vector3()

    def update_clock(self, delta: float):
        """ clock """
        if 0.001 < self.clock_hand_root.rotation.z < 0.01 :
            # when the clock hand is about to reach the 12 o'clock
            # TIMEOUT !!!
            self.counting = False
            self.reset_clock()
            self.force_timeout()
            #self.go_endday()
        else :
            if self.counting :
                add = (delta / CUSTOMER_TIMER)
                #self.sun.rotate_x(delta * inv)
                self.clock_hand_root.rotate_z(-add * 2 * math.pi)

    def copy_order_items(self):
        """ handmade dict deepcopy """
        clone = {}
        iii = self.order["items"]
        for kkk in iii:
            eee = iii[kkk]
            clone[kkk] = eee.copy()
        return clone

    def check_items(self):
        """ Check items on the counter """
        items = self.get_all_item_objects()
        clone_list = self.copy_order_items()
        added : list = []
        total: int = 0

        for c in clone_list:
            total += clone_list[c][1]

        item_on_counter: int = 0

        for item in items:
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
            # not completed
            self.dialogue_lines = dialogue.order_not_complete
            self.update_streak_count(0)
        else:
            # YES
            for a in added:
                self.update_balance(self.balance + (a.price * 1.2))
                a.queue_free()
                self.day_counter_item += 1
            self.update_streak_count(self.streak + 1)
            self.won += 1
            self.dialogue_lines = dialogue.order_ok
            self.order["status"] = "completed"
            self.counting = False
            self.reset_clock()
            self.prepare_items()
        self.dialogue_lines = self.dialogue_lines.copy()
        self.show_dialogue()

    def _input_proxy(self, event):
        """ Proxy for the input event """
        if event.is_action_released("ui_cancel"):
            self.toggle_pausemenu()
            self.confirmorder.modulate = Color(1, 1, 1, 1)
            self.holding_confirm = False

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
                self.holding_confirm = self.order != None
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

    def force_timeout(self):
        """ Repeat the dialogue """
        # push the dialogue
        if self.order:
            self.order["status"] = "failed"
            self.update_streak_count(0)
        self.dialogue_lines = dialogue.order_timeout.copy()
        self.show_dialogue()

    # def _on_player_look_front(self) :
    #     """ when the player turns away from the shelf """
    #     return
    #     if self.player.get("is_look_front") :
    #         return
    #     items = self.get_all_item_objects()
    #     if items.size() < 6 :
    #         self.prepare_items()

    def go_endday(self):
        """ Emit the end day screen """
        self.endday_day.text = str(self.current_day)
        Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

        self.endday_day.text = str(self.current_day)
        self.won_left.text = "Won : %d/%d" % (
            self.won, self.customer_count
        )
        self.won_right.text = "%d x 50 = %d" % (
            self.won, self.won * 50
        )
        self.streak_left.text = "Longest Streak : %d" % (
            self.streak
        )
        self.streak_right.text = "%d x 50 = %d" % (
            self.streak, self.streak * 50
        )
        self.rank.text = '?'
        
        self.sold.text = "%d items sold" % self.day_counter_item
        
        diff = self.balance - self.day_start_balance
        if diff > 0:
            self.add_bal.text = "+$%d" % diff
            self.add_bal.add_color_override("font_color", Color(0.5, 1, 0.5, 1))
            self.add_bal.show()
        elif diff < 0:
            self.add_bal.text = "-$%d" % diff
            self.add_bal.add_color_override("font_color", Color(1, 0.5, 0.5, 1))
            self.add_bal.show()
        else:
            self.add_bal.hide()

        self.endday.show()
        self.set_process(False)

    def _on_next_button_pressed(self):
        """ Go to the next day """
        self.current_day += 1
        self.ani.play("RESET")
        self.get_tree().create_timer(0.001).connect("timeout", self, "newday")