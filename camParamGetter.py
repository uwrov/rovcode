import numpy as np
data = np.load("charuco_calibration.npz")
K = data["camera_matrix"]
dist = data["dist_coeffs"]
fx = K[0,0]
fy = K[1,1]
cx = K[0,2]
cy = K[1,2]
print(fx)
print(fy)
print(cx)
print(cy)

print(tuple([float(fx), float(fy), float(cx), float(cy)]))