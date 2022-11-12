""" Utility functions for the project. """

# Most of them are implemented like Godot's built-in functions.


def GDPORT(self):
    """ Get the GDScript PORT node. """
    return self.get_node("/root/GDPORT")


def PYPORT(self):
    """ Get the Python PORT node. """
    return self.get_node("/root/PYPORT")


def clamp(value, min_value, max_value):
    """ Clamp a value between a minimum and maximum value. """
    return max(min_value, min(max_value, value))
