import cv2
import numpy as np
from pupil_apriltags import Detector

cap = cv2.VideoCapture(0)
detector = Detector("tag36h11")

fx, fy, cx, cy = 800, 800, 320, 240
tag_size = 0.1 #meter
camera_params = (fx, fy, cx, cy)

def pose_from_corners(corners, tag_size, fx, fy, cx, cy):
    s = tag_size

    obj_pts = np.array([
        [-s/2,  s/2, 0],   # top-left
        [ s/2,  s/2, 0],   # top-right
        [ s/2, -s/2, 0],   # bottom-right
        [-s/2, -s/2, 0],   # bottom-left
    ], dtype=np.float32)

    # apriltag gives: lb, rb, rt, lt
    img_pts = np.array([
        corners[3],  # lt
        corners[2],  # rt
        corners[1],  # rb
        corners[0],  # lb
    ], dtype=np.float32)

    K = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0,  0,  1],
    ], dtype=np.float32)

    dist = np.zeros((4, 1), dtype=np.float32)

    ok, rvec, tvec = cv2.solvePnP(
        obj_pts,
        img_pts,
        K,
        dist,
        flags=cv2.SOLVEPNP_IPPE_SQUARE
    )
    return ok, rvec, tvec


while True:
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = detector.detect(img=gray, 
                              estimate_tag_pose=True, 
                              tag_size=0.045, 
                              camera_params=camera_params)
    print(results)
    # for r in results:
    #     pts = r["lb-rb-rt-lt"].astype(int)
    #     ok, rvec, tvec = pose_from_corners(r["lb-rb-rt-lt"], tag_size, fx, fy, cx, cy)
    #     print(f"id={r["id"]} x={tvec[0][0]:.3f} y={tvec[1][0]:.3f} z={tvec[2][0]:.3f}")

    #     for i in range(4):
    #         cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % 4]), (0, 255, 0), 2)
    #     c = tuple(r["center"].astype(int))
    #     if ok:
    #         cv2.putText(frame, f'id {r["id"]} z={tvec[2][0]:.2f}m', c,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    for r in results:
        dist = np.linalg.norm(r.pose_t)
        print(dist)
        ok, rvec, tvec = pose_from_corners(r.corners, tag_size, fx, fy, cx, cy)
        print(f"id={r.tag_id} x={tvec[0][0]:.3f} y={tvec[1][0]:.3f} z={tvec[2][0]:.3f}")

        if ok:
            cv2.putText(frame, f'id {r.tag_id} z={tvec[2][0]:.2f}m', (100, 0) ,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("AprilTag", frame)
    if cv2.waitKey(1) == 27: #esc
        break


cap.release()
cv2.destroyAllWindows()