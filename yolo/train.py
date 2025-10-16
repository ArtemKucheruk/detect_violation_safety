from ultralytics import YOLO

def main():
    model = YOLO('yolo11s.pt')
    model.train(
        data='dataset.yaml',
        epochs=70,
        imgsz=640,
        batch=48,
        project = 'C:/Users/tamsee/PycharmProjects/detect_violation_safety/output'
    )

if __name__ == '__main__':
    main()
