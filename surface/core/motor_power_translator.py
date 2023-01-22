import numpy as np
# from geometry_msgs.msg import Wrench

# thruster order: ['forward_left', 'forward_right', 'forward_top', 'sideways_top', 'up_left', 'up_right']
# looks like a reasonable max on motor power is 3.87757526

tweak_roll = 0.66
transform_mat = np.array([[0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000012e+00,  0.00000000e+00,  0.00000000e+00],
                                [-1.00000012e+00, -1.00000012e+00, -1.00000012e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
                                [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00,  1.00000000e+00],
                                [-7.90000111e-02, -7.90000111e-02,  1.14700019e-01, -0.00000000e+00,  2.35999823e-02,  2.35999823e-02],
                                [ 0.00000000e+00, -0.00000000e+00,  0.00000000e+00,  1.14700019e-01,  1.47949994e-01 * tweak_roll, -1.48149997e-01 * tweak_roll],
                                [ 1.47950009e-01, -1.48150012e-01,  4.99950984e-05,  1.68400049e-01,  -0.00000000e+00,  0.00000000e+00]])

transform_inv = np.linalg.inv(transform_mat)

motor_scalars = [0.25, 0.25, 0.25, 0.25, 0.25, 0.25]


def wrench_to_col(vector) -> np.array:
    return np.array([vector]).T

def convert_vector_to_pwms(vector) -> np.array:
    # Calculate motor powers
    input_vector = wrench_to_col(vector)
    motor_powers = transform_inv @ input_vector
    return motor_powers