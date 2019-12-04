import random

import math
import pygame

from consts import CAR_WIDTH, CAR_HEIGHT, MAX_TICK, GasState, TurnState, MAX_SKID_POINTS
from point import Point
from position import Position

MINUS_ONE = Position(
    x=Point(None, -1, 0),
    y=Point(None, -1, 0),
    r=Point(None, -1, 0)
)


def get_rect(me, my_new_pos):
    transform = pygame.transform.rotate(me.image, my_new_pos.r.pos)
    rect = transform.get_rect()
    rect.centerx = my_new_pos.x.pos + (CAR_WIDTH / 2.0)
    rect.centery = my_new_pos.y.pos + (CAR_HEIGHT / 2.0)
    return rect, transform


def rotate_around_point_highperf(xy, radians, origin=(0, 0)):
    """Rotate a point around a given point.

    I call this the "high performance" version since we're caching some
    values that are needed >1 time. It's less readable than the previous
    function but it's faster.
    """
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy


class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, inv_resistance=0.99, power=0, r=Point(0), braking_inv_resistance=0.9):
        pygame.sprite.Sprite.__init__(self)
        self.pos = Position(x=x, y=y, r=r)
        self.power = power
        self.default_inv_resistance = inv_resistance
        self.braking_inv_resistance = braking_inv_resistance
        self.inv_resistance = self.default_inv_resistance
        self.gas_state = GasState.accelerate
        self.turn_state = TurnState.none
        self.crash_timer = 0
        self.default_crash_timer = random.randrange(0, 200)

        self.image = pygame.image.load("car.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (CAR_WIDTH, CAR_HEIGHT))
        self.transform = self.image
        self.rect = self.image.get_rect()
        self.rl_skid_list = []
        self.rr_skid_list = []

    def collide(self, other):
        if self.rect.colliderect(other.rect):
            x = Point(vel=self.pos.x.vel - other.pos.x.vel)
            y = Point(vel=self.pos.y.vel - other.pos.y.vel)
            r = Point(vel=self.pos.r.vel - other.pos.r.vel)
            speed_diff = Position(x=x, y=y, r=r)

            self.pos -= speed_diff
            other.pos += speed_diff

            self.crash_timer = self.default_crash_timer
            other.crash_timer = other.default_crash_timer
            return True
        return False

    def update(self, tick):
        tick = min(tick, MAX_TICK)
        self.crash_check()

        self.gas_fsm()
        self.turning_fsm()

        self.pos = self.pos.update(tick)
        self.apply_resistance()
        self.rect, self.transform = get_rect(self, self.pos)

        self.add_to_skid_list()

    def add_to_skid_list(self):
        l_rear_wheel_location = (
            CAR_WIDTH/4,
            CAR_HEIGHT - (CAR_HEIGHT/4)
        )
        l_rotated_wheel_pos = rotate_around_point_highperf(
            l_rear_wheel_location, math.radians(self.pos.r.pos), (CAR_WIDTH/2, CAR_HEIGHT/2)
        )
        l_curr_pos = (
            l_rotated_wheel_pos[0] + self.pos.x.pos,
            l_rotated_wheel_pos[1] + self.pos.y.pos
        )

        if len(self.rl_skid_list) > 0:
            last_pos = self.rl_skid_list[-1]
            if l_curr_pos[0] != last_pos[0] or l_curr_pos[1] != last_pos[1]:
                self.rl_skid_list.append(l_curr_pos)
            if len(self.rl_skid_list) > MAX_SKID_POINTS:
                self.rl_skid_list.pop(0)
        else:
            self.rl_skid_list.append(l_curr_pos)

        r_rear_wheel_location = (
            CAR_WIDTH/4 + CAR_WIDTH/2,
            CAR_HEIGHT - (CAR_HEIGHT/4)
        )
        r_rotated_wheel_pos = rotate_around_point_highperf(
            r_rear_wheel_location, math.radians(self.pos.r.pos), (CAR_WIDTH/2, CAR_HEIGHT/2)
        )
        r_curr_pos = (
            r_rotated_wheel_pos[0] + self.pos.x.pos,
            r_rotated_wheel_pos[1] + self.pos.y.pos
        )
        if len(self.rr_skid_list) > 0:
            last_pos = self.rr_skid_list[-1]
            if r_curr_pos[0] != last_pos[0] or r_curr_pos[1] != last_pos[1]:
                self.rr_skid_list.append(r_curr_pos)
            if len(self.rr_skid_list) > MAX_SKID_POINTS:
                self.rr_skid_list.pop(0)
        else:
            self.rr_skid_list.append(r_curr_pos)

    def crash_check(self):
        if self.crash_timer > 0:
            self.gas_state = GasState.brake
            self.turn_state = GasState.coast
            self.crash_timer -= 1

    def gas_fsm(self):
        if self.gas_state == GasState.accelerate:
            acc = rotate_around_point_highperf(
                xy=(0, self.power),
                radians=math.radians(self.pos.r.pos),
            )
            self.pos.x.acc = acc[0]
            self.pos.y.acc = acc[1]
            self.inv_resistance = self.default_inv_resistance
        elif self.gas_state == GasState.brake:
            self.pos.x.acc = 0
            self.pos.y.acc = 0
            self.inv_resistance = self.braking_inv_resistance
        else:
            self.pos.x.acc = 0
            self.pos.y.acc = 0
            self.inv_resistance = self.default_inv_resistance

    def turning_fsm(self):
        if self.turn_state == TurnState.left:
            self.pos.r.acc = -self.power
        elif self.turn_state == TurnState.right:
            self.pos.r.acc = self.power
        else:
            self.pos.r.acc = 0

    def apply_resistance(self):
        car_nose = (
            CAR_WIDTH/2,
            0
        )
        rotated_car_nose = rotate_around_point_highperf(
            car_nose, math.radians(self.pos.r.pos)
        )

        slip = rotated_car_nose


        pos = self.pos * Position(
            x=Point(None, self.inv_resistance, None),
            y=Point(None, self.inv_resistance, None),
            r=Point(None, self.inv_resistance, None)
        )
        self.pos = pos

    def draw(self, screen):
        if len(self.rl_skid_list) > 1:
            pygame.draw.lines(screen, (0, 0, 0), False, self.rl_skid_list, 3)
        if len(self.rr_skid_list) > 1:
            pygame.draw.lines(screen, (0, 0, 0), False, self.rr_skid_list, 3)
        #     last_point = self.skid_list[-1]
        #     for i in range(0, len(self.skid_list), 2):
        #         cur_point = self.skid_list[i]
        #         pygame.draw.line(screen, (0, 0, 0), last_point, cur_point)
        #         last_point = cur_point
        screen.blit(self.transform, self.rect)

    def __str__(self) -> str:
        return f"pos: {self.pos}"
