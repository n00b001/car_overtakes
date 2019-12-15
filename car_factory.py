import random
from time import sleep

from car import Car
from consts import SC_X, SC_Y, CAR_WIDTH, CAR_HEIGHT
from point import Point


def factory(cars, running):
    while running[0]:
        if not running[1]:
            for x in range(0, SC_X, CAR_WIDTH * 2):
                c = get_random_car(x + CAR_WIDTH / 2, SC_Y - CAR_HEIGHT)
                if not any([True for car in cars if car.rect.colliderect(c.rect)]):
                    cars.append(c)
            sleep(5)


def cleanup(cars: list, lock, running):
    while running[0]:
        to_remove = []
        [
            to_remove.append(c)
            for c in cars
            if c.pos.x.pos < 0 or c.pos.x.pos > SC_X or c.pos.y.pos < 0 or c.pos.y.pos > SC_Y
        ]
        with lock:
            [cars.remove(c) for c in to_remove]
        sleep(10)


def get_random_car(x, y):
    x = Point(x)
    y = Point(y)
    inv_resistance = random.uniform(0.97, 0.99)
    # inv_resistance = 0.999
    power = random.uniform(-0.00005, -0.00008)
    # power = -0.0002
    r = Point(random.uniform(-1, 1))
    # r = Point(0)
    c = Car(
        x=x, y=y,
        inv_resistance=inv_resistance,
        power=power,
        r=r
    )
    return c
