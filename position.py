from consts import DEGREES_IN_CIRCLE
from point import Point


class Position:
    def __init__(self, x=Point(), y=Point(), r=Point()):
        self.x = x
        self.y = y
        self.r = r

    def update(self, tick):
        x = self.x.update(tick)
        y = self.y.update(tick)
        rot = self.r.update(tick)
        rot.pos = rot.pos % DEGREES_IN_CIRCLE
        return Position(x=x, y=y, r=rot)

    def __str__(self):
        return f"(x: {self.x}, y: {self.y}, rot: {self.r})"

    def __mul__(self, other):
        other_type = type(other)
        if other_type == Position:
            return Position(self.x * other.x, self.y * other.y, self.r * other.r)
        raise Exception(f"Unknown type: {other_type}")

    def __add__(self, other):
        other_type = type(other)
        if other_type == Position:
            return Position(self.x + other.x, self.y + other.y, self.r + other.r)
        raise Exception(f"Unknown type: {other_type}")

    def __sub__(self, other):
        other_type = type(other)
        if other_type == Position:
            return Position(self.x - other.x, self.y - other.y, self.r - other.r)
        raise Exception(f"Unknown type: {other_type}")

    def vel(self):
        return Position(self.x.vel, self.y.vel, self.r.vel)

    def acc(self):
        return Position(self.x.acc, self.y.acc, self.r.acc)

    def pos(self):
        return Position(self.x.pos, self.y.pos, self.r.pos)

