""" Utility functions for the project. """

# Most of them are implemented like Godot's built-in functions.

import math

def GDPORT(self):
    """ Get the GDScript PORT node. """
    return self.get_node("/root/GDPORT")


def PYPORT(self):
    """ Get the Python PORT node. """
    return self.get_node("/root/PYPORT")


def clamp(value: float, min_value: float, max_value: float) -> float:
    """ Clamp a value between a minimum and maximum value. """
    return max(min_value, min(max_value, value))

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the value. """
    return (1 - t) * a + t * b

def linear2db(volume : float) -> float:
    """ Convert linear volume to decibel. """
    return math.log(volume, 10) * 8.6858896380650365530225783783321