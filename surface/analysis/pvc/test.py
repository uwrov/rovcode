from ultralytics import YOLO
import cv2
import numpy as np

# Load model
model = YOLO("runs/segment/train4/weights/best.pt")

# Class names
names = model.names

# Run inference
results = model("videos/live2.mp4", stream=True)

for result in results:
    frame = result.orig_img.copy()

    if result.masks is not None:
        masks = result.masks.data.cpu().numpy()
        boxes = result.boxes

        for i, mask in enumerate(masks):

            cls_id = int(boxes.cls[i])
            conf = float(boxes.conf[i])
            label = f"{names[cls_id]} {conf:.2f}"

            # stable color based on class id
            color = tuple(
                int(x)
                for x in np.random.default_rng(cls_id).integers(0, 255, 3)
            )

            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

            # overlay mask
            frame[mask > 0.5] = frame[mask > 0.5] * 0.5 + np.array(color) * 0.5

            # get bounding box for label placement
            x1, y1, x2, y2 = map(int, boxes.xyxy[i])

            # draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # draw label
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA,
            )

    cv2.imshow("YOLOv8 Segmentation", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
