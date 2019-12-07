from threading import Thread, Lock

import pygame

from car import CAR_WIDTH, CAR_HEIGHT
from car_factory import factory, get_random_car, cleanup
from consts import SC_X, SC_Y, FPS, GasState, TurnState, DEBUG

GAME_DISPLAY = pygame.display.set_mode((SC_X, SC_Y))
lock = Lock()


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, (SC_X, SC_Y))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def main():
    pygame.init()
    pygame.display.set_caption('A bit Racey')
    clock = pygame.time.Clock()
    window_quit = False

    cars = []
    running = [True]
    factory_thread = Thread(target=factory, args=(cars, running))
    cleanup_thread = Thread(target=cleanup, args=(cars, lock, running))
    factory_thread.start()
    cleanup_thread.start()
    gas_state = GasState.accelerate
    turn_state = TurnState.none
    background = Background('background_image.png', [0, 0])

    while not window_quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                window_quit = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                c = get_random_car(pos[0] - (CAR_WIDTH / 2), pos[1] - (CAR_HEIGHT / 2))
                cars.append(c)
            if DEBUG:
                gas_state, turn_state = keyboard_states(event, gas_state, turn_state)

        GAME_DISPLAY.blit(background.image, background.rect)
        if DEBUG:
            for c in cars:
                c.turn_state = turn_state
                c.gas_state = gas_state
        with lock:
            car_len = len(cars)
            tick = clock.get_time()
            for i in range(car_len):
                cars[i].sensor_update()
                for j in range(i + 1, car_len):
                    cars[i].perform_collision_checks(cars[j])
                cars[i].update(tick, cars)
        [c.draw_car(GAME_DISPLAY) for c in cars]

        pygame.display.update()
        clock.tick(FPS)
    running[0] = False
    pygame.quit()
    quit()


def keyboard_states(event, gas_state, turn_state):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT or event.key == ord('a'):
            turn_state = TurnState.left
        if event.key == pygame.K_RIGHT or event.key == ord('d'):
            turn_state = TurnState.right
        if event.key == pygame.K_UP or event.key == ord('w'):
            gas_state = GasState.accelerate
        if event.key == pygame.K_DOWN or event.key == ord('s'):
            gas_state = GasState.brake
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT or event.key == ord('a'):
            turn_state = TurnState.none
        if event.key == pygame.K_RIGHT or event.key == ord('d'):
            turn_state = TurnState.none
        if event.key == pygame.K_UP or event.key == ord('w'):
            gas_state = GasState.coast
        if event.key == pygame.K_DOWN or event.key == ord('s'):
            gas_state = GasState.coast
    return gas_state, turn_state


if __name__ == '__main__':
    main()
