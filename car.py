import random

import math
import pygame

from consts import CAR_WIDTH, CAR_HEIGHT, MAX_TICK, GasState, TurnState, MAX_SKID_POINTS, MAX_ANGLE, INCREMENT, SC_X, \
    DEGREES_IN_CIRCLE
from driver import Driver
from point import Point
from position import Position
from sensor import Sensor
from util import rotate_around_point_highperf


def get_rect(me, my_new_pos):
    transform = pygame.transform.rotate(me.image, my_new_pos.r.pos)
    rect = transform.get_rect()
    rect.centerx = my_new_pos.x.pos + (CAR_WIDTH / 2.0)
    rect.centery = my_new_pos.y.pos + (CAR_HEIGHT / 2.0)
    return rect, transform


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
        self.rect, self.transform = get_rect(self, self.pos)
        self.rl_skid_list = []
        self.rr_skid_list = []
        self.driver = Driver(self)
        self.sensors = [
            Sensor(self, rotation_offset=i)
            for i in range(-MAX_ANGLE, MAX_ANGLE + (INCREMENT - 1), INCREMENT)
        ]
        self.sensors += [
            Sensor(self, rotation_offset=i)
            for i in range(-DEGREES_IN_CIRCLE//2, DEGREES_IN_CIRCLE//2, DEGREES_IN_CIRCLE//6)
        ]
        self.waypoints = [
            (int(x + CAR_WIDTH), -CAR_HEIGHT * 10) for x in range(0, SC_X, CAR_WIDTH * 2)
        ]

        # self.waypoints = [
        #     (SC_X//2, SC_Y//2)
        # ]

    def perform_collision_checks(self, other_car):
        return_val = False
        if self.rect.colliderect(other_car.rect):
            self.position_correction(other_car)
            self.impulse_resolution(other_car)

            self.crash_timer = self.default_crash_timer
            other_car.crash_timer = other_car.default_crash_timer
            return_val = True
        return return_val

    def position_correction(self, other):
        x_incest = ((self.rect.width / 2.0) + (other.rect.width / 2.0)) - abs(self.pos.x.pos - other.pos.x.pos)
        y_not_incest = ((self.rect.height / 2.0) + (other.rect.height / 2.0)) - abs(self.pos.y.pos - other.pos.y.pos)

        if x_incest < y_not_incest:
            if self.pos.x.pos > other.pos.x.pos:
                self.pos.x.pos += x_incest / 2.0
                other.pos.y.pos -= x_incest / 2.0
            else:
                self.pos.x.pos -= x_incest / 2.0
                other.pos.x.pos += x_incest / 2.0
        else:
            if self.pos.y.pos > other.pos.y.pos:
                self.pos.y.pos += y_not_incest / 2.0
                other.pos.y.pos -= y_not_incest / 2.0
            else:
                self.pos.y.pos -= y_not_incest / 2.0
                other.pos.y.pos += y_not_incest / 2.0

    def impulse_resolution(self, other):
        speed_diff = Position(
            Point(vel=self.pos.x.vel - other.pos.x.vel),
            Point(vel=self.pos.y.vel - other.pos.y.vel),
            Point(vel=self.pos.r.vel - other.pos.r.vel)
        )
        self.pos -= speed_diff
        other.pos += speed_diff

    def sensor_update(self, cars: list):
        new_list = [c.rect for c in cars if c != self]
        for s in self.sensors:
            s.reset()
            s.update()
            s.intersects = True if s.rect.collidelist(new_list) > 0 else False

    def update(self, tick):
        tick = min(tick, MAX_TICK)

        self.gas_state, self.turn_state = self.driver.infer(self.gas_state, self.turn_state)
        self.crash_check()

        self.gas_fsm()
        self.turning_fsm()

        self.pos = self.pos.update(tick)
        self.apply_resistance()
        self.rect, self.transform = get_rect(self, self.pos)

        self.add_to_skid_list()

    def add_to_skid_list(self):
        l_rear_wheel_location = (
            CAR_WIDTH / 4,
            CAR_HEIGHT - (CAR_HEIGHT / 4)
        )
        l_rotated_wheel_pos = rotate_around_point_highperf(
            l_rear_wheel_location, math.radians(self.pos.r.pos), (CAR_WIDTH / 2, CAR_HEIGHT / 2)
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
            CAR_WIDTH / 4 + CAR_WIDTH / 2,
            CAR_HEIGHT - (CAR_HEIGHT / 4)
        )
        r_rotated_wheel_pos = rotate_around_point_highperf(
            r_rear_wheel_location, math.radians(self.pos.r.pos), (CAR_WIDTH / 2, CAR_HEIGHT / 2)
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
        pos = self.pos * Position(
            x=Point(None, self.inv_resistance, None),
            y=Point(None, self.inv_resistance, None),
            r=Point(None, self.inv_resistance, None)
        )
        self.pos = pos

    def draw_car(self, screen, debug):
        screen.blit(self.transform, self.rect)
        if debug:
            color = pygame.Color(0, 0, 0, a=1)
            points = [
                self.rect.topleft,
                self.rect.topright,
                self.rect.bottomright,
                self.rect.bottomleft,
            ]
            pygame.draw.lines(
                screen, color, True, points, 1
            )
            [s.draw(screen) for s in self.sensors]
            for w in self.waypoints:
                pygame.draw.circle(screen, (0, 0, 0), w, 5, 1)

    def draw_skids(self, screen):
        # todo: alpha
        color = pygame.Color(0, 0, 0, a=1)
        if len(self.rl_skid_list) > 1:
            pygame.draw.lines(
                screen, color,
                False, self.rl_skid_list, 3
            )
        if len(self.rr_skid_list) > 1:
            pygame.draw.lines(
                screen, color,
                False, self.rr_skid_list, 3
            )

    def get_closest_waypoint(self):
        closest_distance = SC_X
        closest_waypoint = None
        for w in self.waypoints:
            distance = abs(w[0] - self.pos.x.pos)
            if distance < closest_distance:
                closest_distance = distance
                closest_waypoint = w
        return closest_waypoint

    def __str__(self) -> str:
        return f"pos: {self.pos}"
