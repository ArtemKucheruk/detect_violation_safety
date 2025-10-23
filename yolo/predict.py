from ultralytics import YOLO
import cvzone
import cv2
import os
import math
########################################################################################################################################
# Config
MODEL_PATH = '../../output/tuning7/weights/best.pt'
VIOLATION_CLASSES = ['No Helmet', 'No Mask', 'Broken Cable']
OUTPUT_DIR = 'violation_frames'

# Load model once
model = YOLO(MODEL_PATH)

# Class names must match the run file
CLASSNAMES = ['Broken Cable', 'Cable', 'Helmet', 'Machine', 'Mask', 'No Helmet', 'No Mask', 'Person']

# Colors and thickness
colors = {
    'Helmet': (0, 255, 0),
    'Mask': (0, 255, 0),
    'Cable': (0, 255, 0),
    'No Helmet': (0, 0, 255),
    'No Mask': (0, 0, 255),
    'Broken Cable': (0, 255, 0),
    'Person': (255, 0, 0),
    'Machine': (255, 0, 0)
}
thicknesses = {name: 1 for name in CLASSNAMES}

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Video input
video_path = 'RunModel/Hand in the rotating mechanism zone at 05_14_06.mp4'
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
video_name = os.path.basename(video_path)

# Tracking violations
first_violation_recorded = {}
violations_log = []
frame_num = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.5)

    for result in results:
        boxes = result.boxes

        for box in boxes:
            cls_id = int(box.cls[0])
            class_name = CLASSNAMES[cls_id]
            conf = float(box.conf[0])

            # Log violation if relevant
            if class_name in VIOLATION_CLASSES:
                time_sec = frame_num / fps
                record = {
                    'video': video_name,
                    'frame': frame_num,
                    'time_sec': round(time_sec, 2),
                    'violation': class_name,
                    'confidence': round(conf, 2)
                }
                violations_log.append(record)
                print(f"[{video_name}] Frame {frame_num} | {time_sec:.2f}s | Violation: {class_name} | Conf: {conf:.2f}")

                # Save first frame
                if class_name not in first_violation_recorded:
                    img_path = os.path.join(OUTPUT_DIR, f"{video_name}_{class_name}_frame{frame_num}.jpg")
                    cv2.imwrite(img_path, frame)
                    first_violation_recorded[class_name] = img_path
                    print(f"→ Saved first frame of '{class_name}' at {img_path}")

            # Draw bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = colors.get(class_name, (255, 255, 255))
            thickness = thicknesses.get(class_name, 1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            cvzone.putTextRect(frame, f'{class_name} {math.ceil(conf*100)}%', [x1 + 5, y1 + 20],
                               scale=0.7, thickness=1, colorR=(0, 0, 0))

    # Show live detection
    cv2.imshow('Detection Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_num += 1

# Cleanup
cap.release()
cv2.destroyAllWindows()

# Summary
print("\n--- Violation Summary ---")
for v in violations_log:
    print(v)
print("\nFirst frames saved:")
for k, p in first_violation_recorded.items():
    print(f"{k}: {p}")


