def mul_attr(attr1, attr2):
    if attr1 is not None and attr2 is not None:
        pos = attr1 * attr2
    elif attr1 is not None:
        pos = attr1
    elif attr2 is not None:
        pos = attr2
    else:
        pos = None
    return pos


class Point:
    def __init__(self, pos=0, vel=0, acc=0):
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def update(self, tick):
        acc = self.acc
        vel = self.vel + self.acc * tick
        pos = self.pos + (self.vel + vel) * tick
        return Point(acc=acc, vel=vel, pos=pos)

    def __str__(self):
        return f"(pos: {self.pos}, vel: {self.vel}, acc: {self.acc})"

    def __mul__(self, other):
        other_type = type(other)
        if other_type == Point:
            pos = mul_attr(self.pos, other.pos)
            vel = mul_attr(self.vel, other.vel)
            acc = mul_attr(self.acc, other.acc)
            return Point(pos, vel, acc)
        raise Exception(f"Unknown type: {other_type}")

    def __add__(self, other):
        other_type = type(other)
        if other_type == Point:
            pos = self.pos + other.pos
            vel = self.vel + other.vel
            acc = self.acc + other.acc
            return Point(pos, vel, acc)
        raise Exception(f"Unknown type: {other_type}")

    def __sub__(self, other):
        other_type = type(other)
        if other_type == Point:
            pos = self.pos - other.pos
            vel = self.vel - other.vel
            acc = self.acc - other.acc
            return Point(pos, vel, acc)
        raise Exception(f"Unknown type: {other_type}")
