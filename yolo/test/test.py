from ultralytics import YOLO
import cvzone
import cv2
import math

# Load video
cap = cv2.VideoCapture('Work without a protective mask.mp4')

# Load trained YOLO model
model = YOLO('C:/Users/tamsee/PycharmProjects/detect_violation_safety/output/train10/weights/best.pt')

# Class names (must match model's training order)
classnames = ['Helmet', 'Mask', 'No Helmet', 'No Mask', 'Person']

# Colors for each class (BGR format)
colors = {
    'Helmet': (0, 255, 0),        # Green
    'Mask': (0, 255, 0),          # Green
    'No Helmet': (0, 0, 255),     # Red
    'No Mask': (0, 0, 255),       # Red
    'Person': (255, 0, 0)         # Blue
}

# Box thickness per class
thicknesses = {name: 1 for name in classnames}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference with confidence threshold
    results = model(frame, stream=True, conf=0.25)

    for result in results:
        boxes = result.boxes
        print(f"Detected {len(boxes)} objects")

        for box in boxes:
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cls_id = int(box.cls[0])
            if 0 <= cls_id < len(classnames):
                class_name = classnames[cls_id]
            else:
                class_name = f"Unknown({cls_id})"

            confidence = math.ceil(conf * 100)

            # Get color and thickness
            color = colors.get(class_name, (255, 255, 255))  # Default: white
            thickness = thicknesses.get(class_name, 1)

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            cvzone.putTextRect(frame, f'{class_name} {confidence}%', [x1 + 5, y1 + 20],
                               scale=0.7, thickness=1, colorR=color)

    # Display the frame
    cv2.imshow('Detection Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
