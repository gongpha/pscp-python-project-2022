from godot import exposed, Vector3, Array
from godot import *

from .worldspawn import Worldspawn
from . import dialogue

# THE GAME LOGIC


@exposed
class Game(Control):
    worldspawn: Worldspawn
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
    dialogue_lines : list = ["hello"]
    dialogue_repeat : list

    def _ready(self):
        # Get the nodes
        self.worldspawn = self.get_node("worldspawn")
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

        order_dialogue = []
        for vvv in order_item.values() :
            order_dialogue.append("%s x%d" % vvv)

        self.dialogue_repeat = [', '.join(order_dialogue)]
        self.dialogue_lines = dialogue.greeting + self.dialogue_repeat

        print(self.dialogue_lines)
        self.show_dialogue()

    def show_dialogue(self):
        """ Show the dialogue """
        # TODO : Show the dialogue
        pass
