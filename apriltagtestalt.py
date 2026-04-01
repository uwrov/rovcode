import cv2
import numpy as np
from pupil_apriltags import Detector

# Initialize the AprilTag detector
# family is tag36h11
# quad_decimate: controls resolution. higher resolution = more accurate, but slower
# quad_sigma: lower values allow for more noise (0.0 disables blurring),
# something like 0.8 is good for noisy images

STREAM_URL="http://172.25.250.1:8555"
fx, fy, cx, cy = 512.5608552870717, 505.05020962867684, 442.9676688612543, 464.9402391507723
K = np.array([[512.5608552870717, -20.208512975877564, 442.9676688612543], [0.0, 505.05020962867684, 464.9402391507723], [0.0, 0.0, 1.0]])
D = np.array([0.5476455013303632, -4.347333382354809, 6.853708125546365, -3.118622861035556])

tag_size = 0.127 #meter
camera_params = (fx, fy, cx, cy)

at_detector = Detector(
    families="tag36h11"
)

cap = cv2.VideoCapture(STREAM_URL)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (1024, 768), np.eye(3))
    undistorted_img = cv2.fisheye.undistortImage(gray, K, D, Knew=new_K)
    
    # Detect AprilTags in the frame
    tags = at_detector.detect(
        img=undistorted_img,
        estimate_tag_pose=True,
        camera_params=camera_params,
        tag_size=tag_size,  # Tag size in meters (adjust as needed)
    )
    if tags != []:
        for tag in tags:
            if (tag.tag_id != 0) and (tag.tag_id != 1) and (tag.tag_id != 49):
                continue
            print(tag)
            # Low margin is okay because we only use valid tags, and none are similar
            if tag.decision_margin > 42:
                # Draw a rectangle around the detected tag
                cv2.polylines(
                    frame,
                    [tag.corners.astype(int)],
                    isClosed=True,
                    color=(0, 255, 0),
                    thickness=2,
                )
                # Print the tag ID in the bottom-right corner
                cv2.putText(
                    frame,
                    f"Tag ID: {tag.tag_id}",
                    (frame.shape[1] - 150, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    2,
                )
                # Print the decision margin in the bottom-left corner
                cv2.putText(
                    frame,
                    f"Margin: {tag.decision_margin:.2f}",
                    (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    f"Distance: {np.linalg.norm(tag.pose_t)}",
                    (200, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2,
                )
                # Display the frame with detected tags
                cv2.imshow("Detected Tags", frame)

    # # Display the frame in a window
    cv2.imshow("Live Feed", undistorted_img)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()