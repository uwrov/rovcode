from ultralytics import YOLO
import multiprocessing


def main():
    model = YOLO("yolov8n-seg.pt")
    model.train(
        data="pvc.yml", epochs=30, imgsz=640, device=0  # use GPU explicitly
    )

    model.export()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
