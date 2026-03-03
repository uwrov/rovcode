from ultralytics import YOLO
import cv2
import numpy as np

# Load model
model = YOLO("best.pt")

# Run inference on video (stream=True is IMPORTANT)
results = model("videos/1.mp4", stream=True)

# Loop through video frames
for result in results:
    frame = result.orig_img.copy()  # BGR image

    if result.masks is not None:
        masks = result.masks.data.cpu().numpy()  # (N, H, W)

        for mask in masks:
            color = np.random.randint(0, 255, (3,), dtype=np.uint8)

            # Resize mask if needed (safety)
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

            # Apply mask
            frame[mask > 0.5] = 0.5 * frame[mask > 0.5] + 0.5 * color

    # Show frame
    cv2.imshow("YOLOv8 Segmentation", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
