# # TODO: implement "control core" - translate input into PWM values
# from keyboard_in import get_x, get_y

# is_keyboard = True
# # implement a way to see if keyboard or controller is being used for input

# if is_keyboard:
#     # set PWM to match keyboard values w/ get_x() & get_y()
#     tempx = get_x()
#     tempy = get_y()
# else:
#     is_keyboard = False
#     # set PWM to match controller values (not yet implemented)
import numpy as np
# from geometry_msgs.msg import Wrench


max_power = 3.87757526 # max of a vertical motor going up and rolling, seems reasonable for now?

def f(x):
    if x < 0:
        return int(np.interp(x, [-1, 0], [1100, 1475]))
    elif x > 0:
        return int(np.interp(x, [0, 1], [1525, 1900]))
    else:
        return 1500
    
map_power_to_pwm = np.vectorize(f)

def convert_mp_to_pwms(motor_powers):
    # convert motor powers into pwms
    motor_powers = motor_powers / max_power # normalize the power vector
    return map_power_to_pwm(motor_powers).flatten().tolist()

