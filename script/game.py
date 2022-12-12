from godot import exposed, Vector2, Array, Color, Vector3
from godot import *

from .worldspawn import Worldspawn
from . import dialogue
from .player import Player
from .utils import lerp

from .rank_table import get_rank_by_score, DAY_TIME, DAY_CUSTOMER, RANK_COLOR
from .utils import GDPORT

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

CUSTOMER_SHEETS = [
    "res://resource/spritesheet/customer1.tres",
    "res://resource/spritesheet/customer2.tres",
    "res://resource/spritesheet/customer3.tres",
    "res://resource/spritesheet/customer4.tres",
]

MIN_CUSTOMERS = 10
MAX_CUSTOMERS = 30
CUSTOMER_TIMER = 15.0
STREAK_BONUS = 20
TRANSLATION_COUNT = 6

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
    endday_final : VBoxContainer

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
    customer_counter: Label # Customer Label

    customer_sprite3d: AnimatedSprite3D

    sold: Label
    streak_label: Label

    counting : bool = False
    #tscale: float = 0.04  # Time scale
    current_day: int = 1

    tv_raw : Label
    tv_arrow : Label
    tv_translated : Label
    tv_is_translated : bool = False

    ###########################

    order = None  # Order
    dialogue_lines: list = ["hello"]
    dialogue_repeat: list

    dialogue_animating_chars: bool = False
    holding_confirm: bool = False
    confirm_order_value: float = 0.0

    day_counter_item : int = 0

    customer_count : int = 0
    customer_count_total : int = 0

    won : int = 0
    streak : int = 0
    next_button : Button

    pausemenu : Control

    cheat_attempt : float = 0.0
    cheat_mode : bool = False
    cheat_label : Label
    cheatfx : AudioStreamPlayer
    clock_freezing : bool = False
    anicheat : AnimationPlayer

    confirm_fx : AudioStreamPlayer
    dialogue_fx : AudioStreamPlayer3D

    win_music : AudioStreamPlayer

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

        self.endday_final = self.get_node("endday/endday/vbox/vbox")
        self.endday_day = self.get_node("endday/endday/vbox/hbox/day")
        self.won_left = self.get_node("endday/endday/vbox/vbox/won/a")
        self.won_right = self.get_node("endday/endday/vbox/vbox/won/b")
        self.streak_left = self.get_node("endday/endday/vbox/vbox/streak/a")
        self.streak_right = self.get_node("endday/endday/vbox/vbox/streak/b")
        self.rank = self.get_node("endday/endday/vbox/vbox/rank/b")

        self.daystat = self.get_node("endday/endday/vbox/daystat")
        self.streak_label = self.get_node("ui/vbox/streak")

        self.motd_day = self.get_node("motd/day")

        self.hint_day = self.get_node("ui/vbox/day")
        self.customer_counter = self.get_node("ui/vbox/customer_counter")

        customer = self.get_node("customer")
        customer.pause_mode = Node.PAUSE_MODE_STOP

        self.customer_sprite3d = self.get_node("customer/customer")

        self.pausemenu = self.get_node("pausemenu")
        self.pausemenu.connect("on_resume", self, "toggle_pausemenu")
        self.pausemenu.hide()
        self.pausemenu.pause_mode = Node.PAUSE_MODE_PROCESS

        self.tv_raw = self.get_node("tv/screen/tvcontent/tvscreen/raw")
        self.tv_arrow = self.get_node("tv/screen/tvcontent/tvscreen/arrow")
        self.tv_translated = self.get_node("tv/screen/tvcontent/tvscreen/translated")

        input_node: Node = self.get_node("input")
        input_node.connect("input", self, "_input_proxy",
                           Array(), Object.CONNECT_DEFERRED)

        self.next_button = self.get_node("endday/endday/vbox/continue")
        self.next_button.connect("pressed", self, "_on_next_button_pressed")

        self.cheat_label = self.get_node("ui/cheat")
        self.cheat_label.hide()
        self.cheatfx = self.get_node("ui/cheatfx")
        self.anicheat = self.get_node("anicheat")

        self.confirm_fx = self.worldspawn.get_node("confirm")
        self.dialogue_fx = self.get_node("customer/dialogue_fx")
        
        self.win_music = self.get_node("endday/endday/endday")

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

    def remove_all_items(self):
        """ Remove all items in the world"""
        for item in self.get_all_item_objects():
            item.free()

    def newday(self):
        """ Called when a game day starts """

        self.rng.randomize()  # Randomize the seed

        # Reset these
        #self.sun.rotation = Vector3()
        self.reset_clock()

        # Random its seed by the current time
        self.rng.randomize()

        # Prepare items on the shelf
        self.remove_all_items()
        self.prepare_items()

        self.counting = False

        self.update_customer_count(0)
        self.customer_count_total += DAY_CUSTOMER[self.current_day]
        self.update_streak_count(0)
        self.day_counter_item = 0

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

            # Now, items are can emit impact sounds
            self.get_tree().set_group("item", "block_impacting", False)

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
                    self.tv_show_translation()
        elif ani_name == "customer_exit":
            # NEXT
            self.update_customer_count(self.customer_count + 1)
            if self.customer_count >= DAY_CUSTOMER[self.current_day]:
                self.go_endday(self.current_day == 7) # end
            else :
                self.feed_customer() # NEXT !

    def feed_customer(self):
        """ Summon the customer """

        self.reset_clock()

        # Randomize the customer's sprite
        self.customer_sprite3d.frames = ResourceLoader.load(CUSTOMER_SHEETS[
            self.rng.randi_range(0, len(CUSTOMER_SHEETS) - 1)
        ])
        
        self.ani.play("customer_enter")
        self.tv_clear()

    def get_all_item_objects(self) -> list:
        """ Get all item objects """
        return self.get_tree().get_nodes_in_group("item")

    def dialogue_pick(self, lll : list) -> str:
        """ Pick a random dialogue from a list """
        return lll[self.rng.randi_range(0, len(lll) - 1)]

    def fetch_order(self):
        """ Fetch the order from the customer """

        #
        items = self.get_all_item_objects()

        assert items, "No items in the world"

        order_item = {}

        self.order = {
            'items': order_item,
            'status': "pending",
            'repeat': 0,
        }

        available = {}

        for item in items:
            ttt = available.get(item.filename, [item.item_name, 0, item.item_conname])
            ttt[1] += 1
            available[item.filename] = ttt

        keyshuffled = list(available.keys())
        random.shuffle(keyshuffled)
        item_count = self.rng.randi_range(1, 3)
        keyshuffled = keyshuffled[:item_count]
        
        for kkk in keyshuffled:
            order_item[kkk] = [
                available[kkk][0],
                self.rng.randi_range(1, available[kkk][1]),
                available[kkk][2],
            ]

        # Prepare the texts
        order_dialogue = [self.dialogue_pick(dialogue.order_item).format(**{
            'translated' : vvv[0],
            'count' : vvv[1],
            'itemname' : vvv[2]
        })for vvv in order_item.values()]

        self.dialogue_repeat = ', '.join(order_dialogue)
        self.dialogue_lines = [
            self.dialogue_pick(dialogue.greeting),
            self.dialogue_pick(dialogue.order).format(self.dialogue_repeat)
        ]

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
        self.confirm_fx.stop()
        return True

    def prepare_items(self):
        """ Place items on the shelf """
        for area in self.worldspawn.get("itemspawnpoints"):
            # Check if there's an item on the area
            overlapping: Area = area.get_overlapping_bodies()
            if overlapping.size() > 0:
                continue  # Okay, there's an item on the area. SKIP

            is_in_fridge = str(area.name).startswith("f")

            while True:
                path = ITEM_PATHS[self.rng.randi_range(0, len(ITEM_PATHS) - 1)]
                item_scene: PackedScene = ResourceLoader.load(path)
                item: RigidBody = item_scene.instance()
                if item.get("fridge") != is_in_fridge:
                    # not match the area. retry
                    item.free()
                    continue
                self.add_child(item)  # Add the item to the world
                item.global_translation = area.global_translation
                item.home_place = area.global_translation
                break

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
                self.confirm_fx.stop()
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
            old_visible = self.dialogue_richtext.visible_characters
            self.dialogue_richtext.percent_visible += 0.25 / \
                max(0.1, self.dialogue_richtext.bbcode_text.length())
            if self.dialogue_richtext.visible_characters != old_visible:
                # play sound
                self.dialogue_fx.play()
            if self.dialogue_richtext.percent_visible == 1.0:
                # STOP
                self.dialogue_animating_chars = False
                self.adv_hint.show()

        self.update_clock(delta)

        if Input.is_action_pressed("cheat_mode"):
            self.cheat_attempt += delta
            if self.cheat_attempt >= 2.0:
                self.activate_cheat_mode()
        else:
            self.cheat_attempt = 0.0

    def reset_clock(self):
        self.clock_hand_root.rotation = Vector3()

    def update_clock(self, delta: float):
        """ clock """
        if self.clock_freezing:
            return

        if 0.001 < self.clock_hand_root.rotation.z < 0.01 :
            # when the clock hand is about to reach the 12 o'clock
            # TIMEOUT !!!
            self.counting = False
            self.reset_clock()
            self.force_timeout()
            #self.go_endday()
        else :
            if self.counting :
                add = (delta / DAY_TIME[self.current_day])
                #self.sun.rotate_x(delta * inv)
                self.clock_hand_root.rotate_z(-add * 2 * math.pi)

    def copy_order_items(self):
        """ handmade dict deepcopy """
        clone = {}
        iii = self.order["items"]
        for kkk in iii:
            clone[kkk] = iii[kkk].copy()
        return clone

    def check_items(self, force_complete: bool = False):
        """ Check items on the counter """
        if self.order is None:
            return
            
        clone_list = {}
        item_on_counter = 0
        added = []
        total = 0

        if not force_complete:
            items = self.get_all_item_objects()
            clone_list = self.copy_order_items()
            
            

            for c in clone_list:
                total += clone_list[c][1]

            

            for item in items:
                in_good = self.worldspawn.get("counter_good").overlaps_body(item)

                if not in_good:
                    # the item isn't placed on the counter
                    continue

                # if it's in the list. mark them
                if item.filename in clone_list:
                    clone_list[item.filename][1] -= 1
                    if clone_list[item.filename][1] == 0:
                        del clone_list[item.filename]  # no more...
                    added.append(item)
                item_on_counter += 1

        if item_on_counter > total:
            self.dialogue_lines = [self.dialogue_pick(dialogue.order_too_many_items)]
            self.update_streak_count(0)
        elif clone_list:
            # not completed
            self.dialogue_lines = [self.dialogue_pick(dialogue.order_not_complete)]
            self.update_streak_count(0)
        else:
            # YES
            for a in added:
                a.queue_free()
                self.day_counter_item += 1
            self.update_streak_count(self.streak + 1)
            self.won += 1
            self.dialogue_lines = [self.dialogue_pick(dialogue.order_ok)]
            self.order["status"] = "completed"
            self.counting = False
            self.prepare_items()
        self.dialogue_lines = self.dialogue_lines.copy()
        self.show_dialogue()

    def _input_proxy(self, event : InputEvent):
        """ Proxy for the input event """
        if event.is_action_released("ui_cancel"):
            self.toggle_pausemenu()
            self.confirmorder.modulate = Color(1, 1, 1, 1)
            self.holding_confirm = False
            self.confirm_fx.stop()

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
                if self.order != None:
                    self.holding_confirm = True
                    self.confirm_fx.play()
        elif event.is_action_pressed("repeat"):
            # repeat the dialogue
            self.repeat_dialogue()

        if event.is_action_released("ui_select"):
            self.confirmorder.modulate = Color(1, 1, 1, 1)
            self.holding_confirm = False
            self.confirm_fx.stop()

        if Input.is_mouse_button_pressed(BUTTON_LEFT):
            self.pick.modulate = Color(1, 1, 0, 1)
        else:
            self.pick.modulate = Color(1, 1, 1, 1)

        if self.cheat_mode :
            self.cheat_input(event)

        self.player._input_proxy(event)

    def repeat_dialogue(self, ignore_counting : bool = False):
        """ Repeat the dialogue """
        if self.dialogue_panel.visible or not self.order:
            return

        self.dialogue_lines = [self.dialogue_repeat]
        if ignore_counting:
            self.order["repeat"] += 1
        if self.order["repeat"] > 6:
            self.dialogue_lines = [self.dialogue_pick(dialogue.repeat_too_much_final)]
            self.order["status"] = "failed"
            self.update_streak_count(0)
            self.counting = False
        elif self.order["repeat"] == 3:
            self.dialogue_lines += [self.dialogue_pick(dialogue.repeat_too_much)]
        self.show_dialogue()

    def force_timeout(self):
        """ Repeat the dialogue """
        # push the dialogue
        if self.order:
            self.order["status"] = "failed"
            self.update_streak_count(0)
        self.dialogue_lines = [self.dialogue_pick(dialogue.order_timeout)]
        self.show_dialogue()

    # def _on_player_look_front(self) :
    #     """ when the player turns away from the shelf """
    #     return
    #     if self.player.get("is_look_front") :
    #         return
    #     items = self.get_all_item_objects()
    #     if items.size() < 6 :
    #         self.prepare_items()

    def go_endday(self, real_end : bool):
        """ Emit the end day screen """
        self.endday_final.visible = real_end
        Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
        self.endday_day.text = str(self.current_day)
        self.daystat.text = "%s\n%s" % (
            ("%d items sold" % self.day_counter_item) if self.day_counter_item > 0 else (
                "No items sold" # POSSBILE ?
            ),
            (
                "%d completed customers" % self.customer_count
            ) if self.customer_count > 0 else (
                "No completed customers"
            )
        )

        self.win_music.play()

        if real_end:
            self.won_left.text = "Won : %d/%d" % (
                self.won, self.customer_count_total
            )
            self.won_right.text = "%d x 50 = %d" % (
                self.won, self.won * 50
            )
            self.streak_left.text = "Current Streak : %d" % (
                self.streak
            )
            self.streak_right.text = "%d x 50 = %d" % (
                self.streak, self.streak * 50
            )
            final = self.won + (self.streak * STREAK_BONUS)
            self.rank.text = get_rank_by_score(final)
            self.rank.add_color_override("font_color", RANK_COLOR[str(self.rank.text)])
            self.next_button.text = "Back to the mainmenu"
        self.endday.show()
        self.set_process(False)

    def _on_next_button_pressed(self):
        """ Go to the next day """
        if self.current_day == 7:
            self.get_tree().paused = False
            GDPORT(self).call("go_to_mainmenu")
            return
        self.current_day += 1
        self.ani.play("RESET")
        self.get_tree().create_timer(0.001).connect("timeout", self, "newday")

    def tv_clear(self):
        """ Clear the text """
        self.tv_raw.text = '\n'.join(['...'] * TRANSLATION_COUNT)
        self.tv_arrow.text = '\n'.join(['->'] * TRANSLATION_COUNT)
        self.tv_translated.text = self.tv_raw.text
        self.tv_is_translated = False

    def tv_show_translation(self):
        """ Show the translation """

        if self.tv_is_translated : return

        other = ITEM_PATHS.copy()
        random.shuffle(other)

        texts = []
        
        for _, vvv in self.order["items"].items():
            texts.append((str(vvv[2]), str(vvv[0])))
        while len(texts) < TRANSLATION_COUNT:
            item_scene: PackedScene = ResourceLoader.load(other[0])
            item: RigidBody = item_scene.instance()
            tup = (
                str(item.item_conname),
                str(item.item_name)
            )
            if tup not in texts:
                texts.append(tup)
            item.free()
            other.pop(0)
        
        random.shuffle(texts)
        self.tv_raw.text = '\n'.join([t for t, _ in texts])
        self.tv_translated.text = '\n'.join([t for _, t in texts])
        self.tv_is_translated = True

    def activate_cheat_mode(self):
        """ Activate the cheat mode """
        if self.cheat_mode : return
        self.cheat_mode = True
        self.cheat_label.show()
        self.cheatfx.play()
        self.cheat_label.text = "!!! Cheat Mode Activated"
        self.anicheat.stop()
        self.anicheat.play("show")

    def cheat_input(self, event : InputEvent):
        """ CHEAT INPUT """
        if event.is_action_pressed("cheat_freeze_clock"):
            self.cheatfx.play()
            self.clock_freezing = not self.clock_freezing
            self.cheat_label.text = "!!! Clock Freezing : %s" % str(self.clock_freezing)
            self.anicheat.stop()
            self.anicheat.play("show")
        elif event.is_action_pressed("cheat_force_complete_order") and self.order:
            self.cheatfx.play()
            self.check_items(True)
            self.cheat_label.text = "!!! Order Completed"
            self.anicheat.stop()
            self.anicheat.play("show")
        elif event.is_action_pressed("cheat_repeat_ignore_counting") and self.order:
            self.cheatfx.play()
            self.repeat_dialogue()
            self.cheat_label.text = "!!! Dialogue Repeated without counting"
            self.anicheat.stop()
            self.anicheat.play("show")
        elif event.is_action_pressed("cheat_noclip"):
            self.cheatfx.play()
            self.player.set("noclip", not self.player.get("noclip"))
            self.cheat_label.text = "!!! Noclip : %s" % str(self.player.get("noclip"))
            self.anicheat.stop()
            self.anicheat.play("show")
        elif event.is_action_pressed("cheat_force_endday_god"):
            self.cheatfx.play()
            self.day_counter_item += 99999
            self.cheat_label.text = "!!! Day Completed (HAXXXXX)"
            self.won += DAY_CUSTOMER[self.current_day]
            self.go_endday(self.current_day == 7)
            self.anicheat.stop()
            self.anicheat.play("show")
        elif event.is_action_pressed("cheat_force_endday"):
            self.cheatfx.play()
            self.go_endday(self.current_day == 7)
            self.cheat_label.text = "!!! Day Completed"
            self.anicheat.stop()
            self.anicheat.play("show")