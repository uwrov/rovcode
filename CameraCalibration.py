import cv2
import numpy as np
import time
import os
import cv2.aruco
import json
from typing import Generator, Tuple, Optional

STREAM_URL="http://172.25.250.1:8555"
Sx = 11
Sy = 8
Sl = 0.045 #meters (45mm) 
Ml = 0.03375
Dict = cv2.aruco.DICT_4X4_50
outfile = "charuco_calibration.npz"
save_dir = "scripts/Fisheye_ChArUco_Calibration/data/calibration/images"


minCorners = 12

def main():
    frame_num = 0
    aruco_dict = cv2.aruco.getPredefinedDictionary(Dict)
    board = cv2.aruco.CharucoBoard((Sx,Sy),Sl,Ml,aruco_dict)
    detector = cv2.aruco.CharucoDetector(board)
    cap = cv2.VideoCapture(STREAM_URL)
    all_charuco_corners=[]
    all_charuco_ids=[]
    image_size = None
    last_save_time = 0.0
    while True:
        ok, frame = cap.read()
        image_size = (frame.shape[1],frame.shape[0])
        vis = frame.copy()

        charuco_corners, charuco_ids, marker_corners, marker_ids = detector.detectBoard(frame)
        print(charuco_corners)
        if marker_ids is not None and len(marker_ids) > 0:
            cv2.aruco.drawDetectedMarkers(vis,marker_corners,marker_ids)
        n_charuco = 0 if charuco_ids is None else len(charuco_ids)
        if n_charuco > 0:
            cv2.aruco.drawDetectedCornersCharuco(vis, charuco_corners, charuco_ids)

        cv2.imshow("charucoCalibration", vis)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):

            now = time.time()
            if now - last_save_time < 0.5:
                continue #avoid capturing a bajillion while pressing s
            valid = (
                charuco_corners is not None and
                charuco_ids is not None and
                len(charuco_corners) == len(charuco_ids) and
                len(charuco_ids) >= minCorners
            )
            if valid:
                all_charuco_corners.append(charuco_corners.copy())
                all_charuco_ids.append(charuco_ids.copy())
                cv2.imwrite(f"{save_dir}/frame_{frame_num}.jpg", frame)
                frame_num = frame_num + 1
            last_save_time = now
        elif key == ord("c"):
            retval, cam_matrix, dist_coeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
                charucoCorners = all_charuco_corners,
                charucoIds = all_charuco_ids,
                board=board,
                imageSize=image_size,
                cameraMatrix=None,
                distCoeffs=None
            )
            np.savez(
                outfile,
                camera_matrix=cam_matrix,
                dist_coeffs=dist_coeffs,
                image_width=image_size[0],
                image_height=image_size[1],
                retval = retval,
                squares_x = Sx,
                squares_y = Sy,
                square_length=Sl,
                marker_length=Ml,
                dictionary=Dict
            )
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()