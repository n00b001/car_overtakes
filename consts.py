from enum import Enum

FPS = 75
SC_X = 800
SC_Y = 800
WHITE = (255, 255, 255)

# CAR_WIDTH = 6
# CAR_HEIGHT = 12

CAR_WIDTH = 25
CAR_HEIGHT = 50

MAX_TICK = 16

# MAX_SKID_POINTS = 500
MAX_SKID_POINTS = 0
DEGREES_IN_CIRCLE = 360

DEBUG = False
# DEBUG = True


class GasState(Enum):
    accelerate = 1
    brake = 2
    coast = 3


class TurnState(Enum):
    left = 1
    none = 2
    right = 3
