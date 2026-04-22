import cv2
from pathlib import Path
from ultralytics import YOLO

_SCRIPT_DIR = Path(__file__).resolve().parent
# Godot writes this file to request a clean shutdown (see interface.gd).
STOP_FLAG = _SCRIPT_DIR / ".egc_stop"

# Settings
#video_file = "/Users/chasecarson/Desktop/UWROV/CrabStuff/TestVideos/poolCrab1.mp4"  # Local video file
#stream_url = "" 
camera_id = 0  # Camera index (0 = default webcam, 1, 2, etc. for other cameras)

source = camera_id  # Change to camera_id for camera, stream_url for stream

conf_threshold = 0.9
iou_threshold = 0.25 # NMS IoU threshold (lower = more aggressive suppression)
egc_class_id = 0

# Load model (next to this script so cwd does not matter when launched from Godot)
model = YOLO(str(_SCRIPT_DIR / "Model4Best.pt"))

print("Model loaded! Press 'q' to quit, or use Stop in Godot.")

if STOP_FLAG.exists():
    try:
        STOP_FLAG.unlink()
    except OSError:
        pass

# Main loop with tracking
for result in model.track(source=source, stream=True, tracker="bytetrack.yaml", persist=True, verbose=False, iou=iou_threshold):
    if STOP_FLAG.exists():
        print("EGC detector: stop requested from Godot.")
        try:
            STOP_FLAG.unlink()
        except OSError:
            pass
        break
    frame = result.orig_img
    boxes = result.boxes
    current_crab_count = 0

    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        track_id = int(box.id[0]) if box.id is not None else None

        if cls == egc_class_id and conf >= conf_threshold:
            current_crab_count += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            label = f"egc id={track_id} {conf:.2f}" if track_id else f"egc {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    # Crab count: top-left, bold readable font (TRIPLEX + thick stroke)
    crab_text = f"Crabs detected: {current_crab_count}"
    crab_font = cv2.FONT_HERSHEY_TRIPLEX
    crab_scale = 1.35
    crab_thickness = 3
    crab_margin_x, crab_margin_y = 16, 48
    crab_x = crab_margin_x
    crab_y = crab_margin_y
    # Dark outline for contrast on any background
    outline_color = (0, 0, 0)
    fill_color = (0, 255, 0)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        cv2.putText(
            frame,
            crab_text,
            (crab_x + dx, crab_y + dy),
            crab_font,
            crab_scale,
            outline_color,
            crab_thickness + 2,
            cv2.LINE_AA,
        )
    cv2.putText(
        frame,
        crab_text,
        (crab_x, crab_y),
        crab_font,
        crab_scale,
        fill_color,
        crab_thickness,
        cv2.LINE_AA,
    )
    cv2.imshow("ROV EGC Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting...")
        break

cv2.destroyAllWindows()
