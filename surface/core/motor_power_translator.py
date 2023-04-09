import numpy as np
from .rov_config import thruster_config
from .rov_config import rov_center_of_mass

# from geometry_msgs.msg import Wrench

# thruster order: ['forward_left', 'forward_right', 'forward_top', 'sideways_top', 'up_left', 'up_right']
# looks like a reasonable max on motor power is 3.87757526

control_mat = np.zeros((6, 6))

# first three rows of matrix are x, y, z force contributions
for i in range(6):
    control_mat[0:3, i] = thruster_config[i]['orientation']

# last three rows of matrix are x, y, z torque vector
for i in range(6):
    displacement = np.subtract(thruster_config[i]['location'], rov_center_of_mass)
    force = thruster_config[i]['orientation']
    control_mat[3:6, i] = np.cross(displacement, force)

control_inv = np.linalg.inv(control_mat)

def convert_force_and_torque_to_motor_powers(vector) -> np.array:
    input_vector = np.array([vector]).T
    motor_powers = control_inv @ input_vector
    return motor_powers