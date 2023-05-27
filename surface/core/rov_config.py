# coordinate system is Onshape coordinates, i.e.:
# 'forward'/front is towards -y, 'up'/top is towards +z, and the 'right' side of
# the ROV (i.e. to the left of its forward path of motion) is +x

# thruster locations and center of mass of ROV retrieved by Alnis (@alnis#0001)
# on 2023-01-22 from microversion:
# https://cad.onshape.com/documents/6eb1d47ad2b5b4b375c60fae/w/ea628258f7d101b3908e2cdb/m/b570a4dfd98f63d60f72d441/e/46f26314ed97b202b6e45902

# pin configuration guessed by Alnis (@alnis#0001) on 2023-01-22 from old code:
# https://github.com/uwrov/nautilus_pi/blob/main/src/uwrov_auto/scripts/motor_driver.py

# it's possible that something is left-right mirrored...

rov_center_of_mass = [
    -0.001485,
    -0.173302,
    0.009533
]

# TODO: ROV mass moments of inertia

# name: human-readable name
# location: position in ROV's coordinate system, units meters
# orientation: unit vector representing forward direction of thruster
# pin: raspberry pi pin on which thruster is connected
# model: 't-100' or 't-200' depending on which Blue Robotics thruster it is

thruster_config = [
    {
        'name': 'forward_left',
        'location': [0.15320, -0.28866, -0.04400],
        'orientation': [0.0, -1.0, 0.0],
        'pin': 20,
        'model': 't-100',
        'direction': -1,
        'letter': 'A',
    },
    {
        'name': 'forward_right',
        'location': [-0.15320, -0.28866, -0.04400],
        'orientation': [0.0, -1.0, 0.0],
        'pin': 25,
        'model': 't-100',
        'direction': -1,
        'letter': 'D',
    },
    {
        'name': 'forward_top',
        'location': [-0.00000, -0.02334, 0.14370],
        'orientation': [0.0, -1.0, 0.0],
        'pin': 26,
        # 'pin': 24,
        'model': 't-200',
        # 'direction': -1,
        # 'direction': 1,
        'direction': -1,
        'letter': 'E',
    },
    {
        'name': 'sideways_top',
        'location': [0.00066, -0.33600, 0.14370],
        'orientation': [1.0, 0.0, 0.0],
        'pin': 19,
        # 'pin': 23,
        'model': 't-100',
        # 'direction': 1,
        'direction': -1,
        'letter': 'F',
    },
    {
        'name': 'up_left',
        'location': [0.15320, -0.14400, 0.04466],
        'orientation': [0.0, 0.0, 1.0],
        'pin': 12,
        'model': 't-100',
        'direction': -1,
        'letter': 'C',
    },
    {
        'name': 'up_right',
        'location': [-0.15320, -0.14400, 0.04466],
        'orientation': [0.0, 0.0, 1.0],
        'pin': 16,
        'model': 't-100',
        'direction': 1,
        'letter': 'B',
    },
]