import cv2
import os
import time

# Create a directory to save images if it doesn't exist
output_folder = "captured_frames"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: {output_folder}")

# Initialize video capture object (0 for default camera)
cap = cv2.VideoCapture("http://172.25.250.1:8555/")

if not cap.isOpened():
    print("Cannot open camera")
    exit()

frame_count = 0
print("Press 'c' to capture a frame, or 'q' to quit.")

while True:
    # Read frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Display the resulting frame
    cv2.imshow('Live Feed', frame)

    # Wait for a key press for 1ms
    key = cv2.waitKey(1) & 0xFF

    # Check if 'q' key is pressed to quit
    if key == ord('q'):
        break
    # Check if 'c' key is pressed to save the current frame
    elif key == ord('c'):
        # Generate a unique filename using a timestamp or counter
        img_name = os.path.join(output_folder, f"frame_{frame_count}.jpg")
        
        # Save the frame
        cv2.imwrite(img_name, frame)
        print(f"Saved image: {img_name}")
        frame_count += 1

# When everything done, release the capture and destroy windows
cap.release()
cv2.destroyAllWindows()
