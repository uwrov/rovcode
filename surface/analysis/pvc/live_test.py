import cv2
from ultralytics import YOLO


model = YOLO("models/best_augment_60_room_gpt.pt")

# Open the webcam
cap = cv2.VideoCapture(1)

while cap.isOpened():
    success, frame = cap.read()
    if success:
        # Run inference
        results = model(frame, conf=0.3)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the frame
        cv2.imshow("YOLO Live Inference", annotated_frame)

        # Break loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
