import os # use for creating directories
import random # use for validation split
from PIL import Image
import matplotlib.pyplot as plt
import cv2 # use for image loading
import numpy as np
from nucleus import Point, PolygonAnnotation

SOURCE_DIR = "./frames/"
OUTPUT_DIR = "./pvc_dataset/"
IMG_SIZE = 897
VAL_SPLIT = 0.2
CAM_ID = 1

train_img_dir = os.path.join(OUTPUT_DIR, "images", "train")
val_img_dir = os.path.join(OUTPUT_DIR, "images", "val")
train_label_dir = os.path.join(OUTPUT_DIR, "labels", "train")
val_label_dir = os.path.join(OUTPUT_DIR, "labels", "val")
drawn_img_dir = os.path.join(OUTPUT_DIR, "ref")

os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(train_label_dir, exist_ok=True)
os.makedirs(val_label_dir, exist_ok=True)
os.makedirs(drawn_img_dir, exist_ok=True)

points = []

def load_image(frame):
    """
    Loads image and resizes with globally set restraints
    """
    frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    return frame

def annotate_image(image_path, id):
    """
    Allows user to mark up image with points to draw polygons
    'q' to quit
    's' to skip frame
    'enter' to complete all polygons in frame
    'n' to complete a polygon

    Returns:
        boolean, polygon_arr: annotation complete, polygon array
    """
    points = []

    def onclick(event, x, y, flags, param):
        # allow user to click on the image to define the vertices to add to the polygon annotation
        nonlocal points
        img = param
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print("Adding point ", points[-1])
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
            if len(points) > 1:
                # draw a line between the last point and the "just clicked" point
                cv2.line(
                    img,
                    points[-2],
                    points[-1],
                    (255, 0, 0),
                    2
                )

            cv2.imshow("Image", img)

    # reset points for each image
    points = []
    polygon_arr = []
    img = last_img = load_image(image_path)
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", onclick, param=img)
    while(1):
        key = cv2.waitKey(1) & 0xFF
        # 'enter' key
        if key == 13:
            # all polygons have been drawn
            if len(polygon_arr) == 0:
                print("no objects in this frame.")
                cv2.destroyAllWindows()
                return False, polygon_arr

            # run through to draw polygon for last pvc piece
            vert = np.array(points, np.int32)
            pts = vert.reshape(-1, 1, 2)
            img = cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            drawn_path = os.path.join(drawn_img_dir, f"{id}_drawn.jpg")
            cv2.imwrite(drawn_path, img)
            break

        # 'n' key for nextd
        elif key == 110:
            if(len(points) < 3):
                print("insufficient points for a polygon")
                continue
            # next polygon to be drawn
            print("new polygon!")

            # draw the polygon
            vert = np.array(points, np.int32)
            pts = vert.reshape(-1, 1, 2)
            img = cv2.polylines(
                img, [pts], isClosed=True, color=(0, 255, 0), thickness=2
            )
            cv2.imshow("Image", img)

            polygon_arr.append(points)

            # reset points to nothing, prepped for next
            points = []

        # 'q' key for quit, peaceful shutdown
        elif key == 113:
            cv2.destroyAllWindows()
            quit()

        # 's' key for skip
        elif key == 115:
            cv2.destroyAllWindows()
            return False, polygon_arr

    cv2.destroyAllWindows()
    return True, polygon_arr

def polygon_to_yolo(polygon, class_id=0):
    """
    Convert polygon array of points to yolo string format.
    Normalize to IMG_SIZE.
    
    Returns:
        str: valid YOLO string, estimated floats to 3 figs
    """
    ret = f"{class_id}"
    for point in polygon:
        x = float(point[0]) / IMG_SIZE
        y = float(point[1]) / IMG_SIZE
        # grab floats up to 3 figs
        ret += f" {x:.3f} {y:.3f}"
    return ret


def save_label(filename, frame, label, flag):
    """
    Save label to file

    Args:
        flag (str): train/validation string
    """
    # following this format: https://docs.ultralytics.com/datasets/segment/#supported-dataset-formats
    if flag == "train":
        image_path = os.path.join(train_img_dir, f"{filename}.jpg")
        label_path = os.path.join(train_label_dir, f"{filename}.txt")
    else:
        image_path = os.path.join(val_img_dir, f"{filename}.jpg")
        label_path = os.path.join(val_label_dir, f"{filename}.txt")
    
    cv2.imwrite(image_path, frame)
    
    with open(label_path, "w") as f:
        for polygon in label:
            f.write(polygon_to_yolo(polygon))
            f.write('\n')
    print(f"saved image and labels to: {flag}")

def main():
    id = 0

    # TODO: instead of camera capture, use pre-recorded video for training
    video = cv2.VideoCapture(CAM_ID)
    ret, frame = video.read()

    while(ret):
        ret, frame = video.read()
        success, res = annotate_image(frame, id)
        if success:
            id += 1
            
            # add to the pvc_dataset folder based on val split
            flag = "train" if random.random() > VAL_SPLIT else "val"
            save_label(f"{id}_image", frame, res, flag)

if __name__ == "__main__":
    main()
