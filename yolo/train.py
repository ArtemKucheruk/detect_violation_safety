from ultralytics import YOLO

def main():
    model = YOLO('yolov8n.pt')
    model.train(
        data='C:/Users/tamse/PycharmProjects/detect_violation_safety/yolo/dataset.yaml',
        epochs=5,
        imgsz=640,
        batch=16
    )

if __name__ == '__main__':
    main()
