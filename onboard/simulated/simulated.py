import random

accelerometer, gyroscope = None, None

pin_hack = 1500

def init():
    print('initializing simulated ROV')
    # TODO start Godot simulation and ensure cameras are connected


def set_pin_pwm(number, value):
    print(f'setting pwm: {number} {value}')
    if number == 10:
        global pin_hack
        pin_hack = value
    # TODO: implement


async def flush_pin_pwms():
    pass
    # TODO: implement sending to simulation


async def poll_sensors():
    global accelerometer, gyroscope
    accelerometer = [(1500-pin_hack) * 0.01, 0.0, round(-9.81 + random.randint(-5, 5) * 0.01, 2)]
    gyroscope = [0.0, 0.0, 0.0]
    # TODO implement retrieving from simulation
