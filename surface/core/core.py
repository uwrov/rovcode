import random
from .rov_config import thruster_config

from .motor_power_translator import convert_force_and_torque_to_motor_powers
from .pwm_translator import convert_motor_powers_to_pwms

accelerometer, gyroscope = None, None
translate_x = 0.0

translation = [0.0, 0.0, 0.0]
rotation = [0.0, 0.0, 0.0]

direct_motors = False

pin_pwms = None

# pin_ids = [20, 25, 24, 23, 12, 16]
pin_ids = [20, 25, 23, 24, 12, 16] # switch E and F to work around E's old ESC being broken


def init(_interface, _task):
    global interface, task
    interface, task = _interface, _task


async def update_sensors(summary_data):
    global accelerometer, gyroscope
    accelerometer = summary_data['accelerometer']
    gyroscope = summary_data['gyroscope']
    await interface.notify_sensor_update()


async def update_controls():
    global pin_pwms

    if direct_motors:
        powers = [translation[0], translation[1], translation[2], rotation[0], rotation[1], rotation[2]]
    else:
        powers = convert_force_and_torque_to_motor_powers(
            [translation[0], translation[1], translation[2], rotation[0], rotation[1], rotation[2]]
        )
    powers[4] = -powers[4]
    pwms = convert_motor_powers_to_pwms(powers)
    
    pin_pwms = [{
        'number': pin_ids[i],
        'value': pwms[i]
    } for i in range(len(pwms))]
