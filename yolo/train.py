from ultralytics import YOLO

def main():
    # model = YOLO('yolo11s.pt')
    # model.train(
    #     data='dataset.yaml',
    #     epochs=70,
    #     imgsz=640,
    #     batch=16,  # 48 before, I have 4GB VRAM:(
    #     # TalTech's PC address
    #     # project = 'C:/Users/tamsee/PycharmProjects/detect_violation_safety/output'
    #     # default output
    #     project='../output',
    #     augment=True,
    # )

    model = YOLO('../output/tuning6/weights/best.pt')
    model.train(
        data='dataset.yaml',
        epochs=20,
        imgsz=640,
        batch=16,  # 48 before, I have 4GB VRAM:(
        lr0=0.0001,
        freeze=20,
        project='../output',
        augment=True,
        name='tuning'
    )

if __name__ == '__main__':
    main()
