""" Utility functions for the project. """

# Most of them are implemented like Godot's built-in functions.

def clamp(value, min_value, max_value):
    """ Clamp a value between a minimum and maximum value. """
    return max(min_value, min(max_value, value))