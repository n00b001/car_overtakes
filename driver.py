import random
import sys

import math

from consts import GasState, TurnState, DEGREES_IN_CIRCLE, ATAN2_OFFSET


class Driver:
    def __init__(self, car):
        self.target_speed = 0.0
        self.car = car
        self.favorite_direction = TurnState.left if random.random() < 0.5 else TurnState.right

    def infer(self, gas_state, turn_state):
        offsets = [s.rotation_offset for s in self.car.sensors if s.intersects]
        amount_of_detections = len(offsets)
        if amount_of_detections > 0:
            total_offset = sum(offsets)
            avr_offset = total_offset / amount_of_detections

            abs_offset = abs(avr_offset)
            if abs_offset < 25:
                # gas_state = GasState.brake
                self.target_speed = 0
            elif abs_offset < 45:
                # gas_state = GasState.coast
                pass
            else:
                # gas_state = GasState.accelerate
                if self.target_speed < sys.maxsize:
                    self.target_speed += 1

            if avr_offset > 0:
                turn_state = TurnState.right
            elif avr_offset < 0:
                turn_state = TurnState.left
            else:
                turn_state = TurnState.none
                if 0 not in offsets:
                    if self.target_speed < sys.maxsize:
                        self.target_speed += 1
                else:
                    # gas_state = GasState.brake
                    self.target_speed = 0

        else:
            closest_waypoint = self.car.get_closest_waypoint()
            desired_angle = math.degrees(math.atan2(
                self.car.pos.y.pos - closest_waypoint[1],
                self.car.pos.x.pos - closest_waypoint[0]
            ))
            desired_angle = DEGREES_IN_CIRCLE - ((desired_angle - ATAN2_OFFSET) % DEGREES_IN_CIRCLE)

            diff = desired_angle - self.car.pos.r.pos

            temp_diff_desired = (desired_angle + DEGREES_IN_CIRCLE) - self.car.pos.r.pos
            temp_diff_actual = desired_angle - (self.car.pos.r.pos + DEGREES_IN_CIRCLE)
            abs_diff = abs(diff)
            if abs(temp_diff_desired) < abs_diff:
                diff = temp_diff_desired
            elif abs(temp_diff_actual) < abs_diff:
                diff = temp_diff_actual

            if diff > 0:
                turn_state = TurnState.left
            else:
                turn_state = TurnState.right

            abs_diff = abs(diff)
            if abs_diff < 5:
                # gas_state = GasState.accelerate
                self.target_speed += 1
            elif abs_diff < 45:
                # gas_state = GasState.coast
                pass
            else:
                # gas_state = GasState.brake
                self.target_speed += 1
        gas_state = self.get_gas_state()

        return gas_state, turn_state

    def get_gas_state(self):
        return_state = GasState.coast
        sqr_speed = (self.car.pos.x.vel * self.car.pos.x.vel) + (self.car.pos.y.vel * self.car.pos.y.vel)
        diff = (self.target_speed * self.target_speed) - sqr_speed
        if diff > 5:
            return_state = GasState.accelerate
        elif diff < -5:
            return_state = GasState.brake
        return return_state
