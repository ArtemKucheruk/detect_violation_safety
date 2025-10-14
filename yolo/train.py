from ultralytics import YOLO
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="yolo/dataset.yaml", help="Path to dataset config")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--name", default="custom_yolo")
    args = parser.parse_args()

    os.makedirs("yolo/runs", exist_ok=True)

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project="yolo/runs",
        name=args.name,
        exist_ok=True
    )

if __name__ == "__main__":
    main()