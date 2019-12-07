import math
import pygame

from consts import CAR_WIDTH, CAR_HEIGHT


class Sensor:

    def __init__(self, car, sensor_dist=50.0, rotation_offset=180):
        self.rect = pygame.rect.Rect(0, 0, 20, 20)
        self.intersects = False
        self.car = car
        self.sensor_dist = sensor_dist
        self.rotation_offset = rotation_offset

        # self.surface = pygame.Surface((10, 10))
        # self.surface.fill((0, 0, 0))
        # self.transform = pygame.transform.rotate(self.surface, self.car.pos.r.pos)
        # self.rect = self.surface.get_rect()

    def update(self):
        tranny_x = math.sin(math.radians(self.car.pos.r.pos + self.rotation_offset)) * self.sensor_dist
        tranny_y = math.cos(math.radians(self.car.pos.r.pos + self.rotation_offset)) * self.sensor_dist

        self.rect.centerx = self.car.pos.x.pos + tranny_x + (CAR_WIDTH / 2.0)  # + self.pos[0]
        self.rect.centery = self.car.pos.y.pos + tranny_y + (CAR_HEIGHT / 2.0)  # + self.pos[1]

        # self.transform = pygame.transform.rotate(self.surface, self.car.pos.r.pos)
        # self.intersects = self.rect.collidelist(cars)

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
        # screen.blit(self.transform, self.rect)
