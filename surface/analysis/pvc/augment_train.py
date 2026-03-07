from ultralytics import YOLO
import multiprocessing


def main():
    model = YOLO("yolov8n-seg.pt")

    model.train(
        data="pvc.yml",
        epochs=80,
        imgsz=640,

        hsv_h=0.005,
        hsv_s=0.3,
        hsv_v=0.2,

        degrees=3,
        translate=0.03,
        scale=0.15,

        fliplr=0.5,

        mosaic=0.1,
        mixup=0.0,
        copy_paste=0.1,

        box=7.5,
        cls=1.0,
        dfl=1.5,

        patience=10,
    )

    model.export()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()