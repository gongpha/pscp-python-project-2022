from godot import exposed, signal
from godot import *

from .mainmenu import MainMenu
from .utils import GDPORT

@exposed
class PauseMenu(MainMenu):
    """ Pause menu """

    on_resume = signal()

    def layout(self):
        # Customize this to change the menu list
        self.item_list = {
            "Resume": {
                'description': "Resume the game",
                'callback': self.resume
            },
            "Settings": {
                'description': "Change the game settings",
                'callback': self.option_settings
            },
            "Exit to title": {
                'description': "Back to the mainmenu",
                'callback': self.option_back
            },
            "Exit": {
                'description': "Exit to the desktop",
                'callback': self.option_exit
            }
        }

    def resume(self, i):
        """ Resume the game """
        self.call("emit_signal", "on_resume")
        self.reset()

    def option_back(self, item_that_was_clicked):
        """ Back to the mainmenu """
        self.go_to({
            "Yes": {
                'description': "Back to the mainmenu",
                'callback': self.option_back_confirmed
            },
            "No": {
                'description': "Go back to the pause menu",
                'callback': -1
            }
        }, item_that_was_clicked)

    def option_back_confirmed(self, _):
        """ Exit (REAL) """
        self.get_tree().paused = False
        GDPORT(self).call("go_to_mainmenu")
        
    def reset(self):
        self.go_to(self.item_list)

    def option_exit(self, item_that_was_clicked):
        """ Exit """
        self.go_to({
            "Yes": {
                'description': "Close the game",
                'callback': self.option_exit_confirmed
            },
            "No": {
                'description': "Go back to the pause menu",
                'callback': -1
            }
        }, item_that_was_clicked)

    def option_exit_confirmed(self, _):
        """ Exit (REAL) """
        self.get_tree().quit()