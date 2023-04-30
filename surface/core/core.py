import random
import numpy as np
from .rov_config import thruster_config

from .motor_power_translator import convert_force_and_torque_to_motor_powers
from .pwm_translator import convert_motor_powers_to_pwms

accelerometer, gyroscope = None, None
translate_x = 0.0

translation = [0.0, 0.0, 0.0]
rotation = [0.0, 0.0, 0.0]

direct_motors = False

servo_pin = 26
servo_pwm = 1500

pin_pwms = None

# pin_ids = [20, 25, 24, 23, 12, 16]
# pin_ids = [20, 25, 23, 24, 12, 16] # switch E and F to work around E's old ESC being broken

prev_pwms = [1500, 1500, 1500, 1500, 1500, 1500]

# pin_ids = []
# motor_directions = []
# for motor in thruster_config:   
#     pin_ids.append(motor.get('pin'))
#     if motor.get('run_reversed'):
#         motor_directions.append(-1)
#     else:
#         motor_directions.append(1)
# print(pin_ids)
# print(motor_directions)
# thruster_config[0]['pin'] 

time_to_ramp = 0.3
time_per_cycle = 0.01
amplitude = 400

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

    for i in range(len(powers)):
        powers[i] = powers[i] * thruster_config[i]['direction']

    pwms = convert_motor_powers_to_pwms(powers)
    
    global prev_pwms
    ramp_limit = (time_per_cycle / time_to_ramp) * amplitude

    delta_pwms = np.subtract(pwms, prev_pwms)
    delta_pwms = np.clip(delta_pwms, -ramp_limit, +ramp_limit)

    pwms = np.add(prev_pwms, delta_pwms).astype(int).tolist()
    prev_pwms = pwms

    pin_pwms = [{
        'number': thruster_config[i]['pin'],
        'value': pwms[i]
    } for i in range(len(pwms))]

    pin_pwms.append({
        'number': servo_pin,
        'value': servo_pwm,
    })
