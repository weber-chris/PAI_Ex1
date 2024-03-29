#[General_Constants]
FIELD_WIDTH = 19
FIELD_HEIGHT = 15

#[Game_Constants]
NO_ITERATIONS = 100
MAX_CALC_TIME = 10000000 #1 TODO increased for debug reason

#[Field_Constants]
CELL_EMPTY = '.'
CELL_SHEEP_1 = 'S'
CELL_SHEEP_1_d = 'U'
CELL_WOLF_1 = 'W'
CELL_SHEEP_2 = 's'
CELL_SHEEP_2_d = 'u'
CELL_WOLF_2 = 'w'
CELL_GRASS = 'g'
CELL_RHUBARB = 'r'
CELL_FENCE = '#'


#[Movements]
MOVE_NONE = 0
MOVE_UP = -1
MOVE_DOWN = 1
MOVE_LEFT = -2
MOVE_RIGHT = 2

#[Awards]
AWARD_RHUBARB = 5
AWARD_GRASS = 1