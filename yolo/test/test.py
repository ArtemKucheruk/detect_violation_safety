from ultralytics import YOLO
import cvzone
import cv2
import math

# Running from video
cap = cv2.VideoCapture('Work without a protective mask.mp4')
model = YOLO('C:/Users/tamsee/PycharmProjects/detect_violation_safety/output/train8/weights/best.pt')

# Define class names
classnames = ['Helmet', 'Mask', 'No Helmet', 'No Mask', 'Person']

# Define colors for each class (BGR format)
colors = {
    'Helmet': (0, 255, 0),        # Green
    'Mask': (0, 255, 0),          # Green
    'No Helmet': (0, 0, 255),     # Red
    'No Mask': (0, 0, 255),       # Red
    'Person': (255, 0, 0)         # Blue
}

# Define thickness for the block
thicknesses = {
    'Helmet': 1,
    'Mask': 1,
    'No Helmet': 1,
    'No Mask': 1,
    'Person': 1
}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    #frame = cv2.resize(frame, (640, 480))
    results = model(frame, stream=True, conf=0.25)

    for result in results:
        boxes = result.boxes
        print(f"Detected {len(boxes)} objects")
        for box in boxes:
            conf = float(box.conf[0])
            if conf > 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                class_name = classnames[cls_id]
                confidence = math.ceil(conf * 100)

                # Get color and thickness based on class
                color = colors.get(class_name, (255, 255, 255))  # default white
                thickness = thicknesses.get(class_name, 1)

                # Draw rectangle and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                cvzone.putTextRect(frame, f'{class_name} {confidence}%', [x1 + 5, y1 + 20],
                                   scale=0.7, thickness=1, colorR=color)

    cv2.imshow('Detection Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
