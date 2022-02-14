SPRITE_SIZE = 80

MAP = """
    ##.##
    MMoMM
    M#o#M
    #MMo#
    ##MM#
    #MMo#
    M#M#M
    #Mo#M
    #MM##
    ####o
"""

VOID = '#'
START = '.'
GEM = 'o'
METEOR =  'M'

NOTHING = 'N'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = [NOTHING, LEFT, RIGHT]

REWARD_OUT = -100
REWARD_METEOR = -50
REWARD_GEM = 20
REWARD_NOTHING = 0
