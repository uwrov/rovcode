import random

from .motor_power_translator import convert_force_and_torque_to_motor_powers
from .pwm_translator import convert_motor_powers_to_pwms

accelerometer, gyroscope = None, None
translate_x = 0.0

translation = [0.0, 0.0, 0.0]
rotation = [0.0, 0.0, 0.0]

pin_pwms = None

pin_ids = [10, 11, 12, 13, 14, 15]


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
    powers = convert_force_and_torque_to_motor_powers(
        [translation[0], translation[1], translation[2], rotation[0], rotation[1], rotation[2]]
        # [translate_x, 0., 0., 0., 0., 0.]
    )
    pwms = convert_motor_powers_to_pwms(powers)
    pin_pwms = [{
        'number': pin_ids[i],
        'value': pwms[i]
    } for i in range(len(pwms))]
