from consts import GasState


class Driver:
    def __init__(self, car):
        self.car = car

    def infer(self, gas_state, turn_state):

        if self.car.front_sensor.intersects:
            gas_state = GasState.brake
            print("Braking")
        else:
            gas_state = GasState.accelerate
            print("no Braking")
        return gas_state, turn_state
