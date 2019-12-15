import math
import pygame

from consts import CAR_WIDTH, CAR_HEIGHT
from util import rotate_around_point_highperf
INITIAL_OFFSET = 180


class Sensor:

    def __init__(self, car, rotation_offset, sensor_dist=CAR_HEIGHT / 1.2):
        self.rect = pygame.rect.Rect(0, 0, CAR_HEIGHT / 2.5, CAR_HEIGHT / 2.5)
        self.intersects = False
        self.car = car
        self.sensor_dist = sensor_dist
        self.rotation_offset = rotation_offset

    def update(self):
        trans = rotate_around_point_highperf(
            xy=[0, self.sensor_dist],
            radians=math.radians(self.car.pos.r.pos + self.rotation_offset + INITIAL_OFFSET),
        )

        self.rect.centerx = self.car.pos.x.pos + trans[0] + (CAR_WIDTH / 2.0)
        self.rect.centery = self.car.pos.y.pos + trans[1] + (CAR_HEIGHT / 2.0)

    def intersect(self, c):
        if self.rect.colliderect(c.rect):
            self.intersects = True

    def draw(self, screen):
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

    def reset(self):
        self.intersects = False
