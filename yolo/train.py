from ultralytics import YOLO

def main():
    model = YOLO('yolo11s.pt')
    model.train(
        data='dataset.yaml',
        epochs=300,
        imgsz=640,
        batch=16
        name=train1
    )

if __name__ == '__main__':
    main()
