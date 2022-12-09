""" rank table """
from godot import Color

RANK_COLOR = {
    'E': Color(0.0, 0.0, 0.0),
    'D': Color(0.0, 0.0, 1.0),
    'C': Color(0.0, 1.0, 0.0),
    'B': Color(1.0, 0.5, 0.0),
    'A': Color(1.0, 0.0, 0.0),
    'P': Color(1.0, 1.0, 0.0),
}


def get_rank_by_score(score: int):
    """ Get rank by score """
    if score <= 80:
        return 'E'
    if score <= 100:
        return 'D'
    if score <= 120:
        return 'C'
    if score <= 160:
        return 'B'
    if score <= 174:
        return 'A'
    return 'P'


DAY_TIME = {
    1: 14,
    2: 13,
    3: 12,
    4: 11,
    5: 10,
    6: 9,
    7: 8,
}

DAY_CUSTOMER = {
    1: 10,
    2: 15,
    3: 20,
    4: 25,
    5: 30,
    6: 35,
    7: 40,
}
