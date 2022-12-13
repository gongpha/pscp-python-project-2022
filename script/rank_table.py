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
    1: 30, # 14
    2: 28, # 13
    3: 26, # 12
    4: 24, # 11
    5: 22, # 10
    6: 21, # 9
    7: 21, # 8
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

DAY_DELAY = {
    1: 0.25,
    2: 0.5,
    3: 0.75,
    4: 1.5,
    5: 1.75,
    6: 2.0,
    7: 4.0,
}
