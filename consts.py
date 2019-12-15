from enum import Enum

FPS = 75
SC_X = 800
SC_Y = 800
WHITE = (255, 255, 255)

# CAR_WIDTH = 6
# CAR_HEIGHT = 12

CAR_HEIGHT = 50
CAR_WIDTH = int(CAR_HEIGHT/2.0)

MAX_ANGLE = 60
INCREMENT = 15

MAX_TICK = 16

# MAX_SKID_POINTS = 30
MAX_SKID_POINTS = 0
DEGREES_IN_CIRCLE = 360
ATAN2_OFFSET = 90


class GasState(Enum):
    accelerate = 1
    brake = 2
    coast = 3


class TurnState(Enum):
    left = 1
    none = 2
    right = 3
