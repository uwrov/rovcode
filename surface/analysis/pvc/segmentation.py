import cv2
from ultralytics import YOLO

# load model
model = YOLO('yolov8n-seg.pt')

# open video
cap = cv2.VideoCapture(0)

# loopity loop
while cap.isOpened():
    ret, frame = cap.read()
    
    if(ret):
        # run inference
        results = model(frame)
        annotated = results[0].plot()
        
        cv2.imshow("frame", annotated)
        
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break