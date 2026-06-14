import cv2
import numpy as np

#  Load YOLO
import os
import sys
import cv2

base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))

cfg_path = os.path.join(base_path, "modules", "yolo", "yolov3.cfg")
weights_path = os.path.join(base_path, "modules", "yolo", "yolov3.weights")
names_path = os.path.join(base_path, "modules", "yolo", "coco.names")

# Load YOLO
net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)

# Load class names
with open(names_path, "r") as f:
    classes = [line.strip() for line in f.readlines()]

#  Load image
def load_image(path):
    return cv2.imread(path)


#  BOX DETECTION (YOUR WORKING CODE)
def detect_trash_boxes(image):

    if image is None:
        return None

    h, w = image.shape[:2]

    # -------- YOLO DETECTION --------
    blob = cv2.dnn.blobFromImage(
        image, 1/255.0, (416, 416),
        swapRB=True, crop=False
    )

    net.setInput(blob)
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            confidence = max(scores)

            if confidence > 0.3:
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                bw = int(detection[2] * w)
                bh = int(detection[3] * h)

                x = int(center_x - bw / 2)
                y = int(center_y - bh / 2)

                cv2.rectangle(image, (x, y), (x + bw, y + bh), (0, 0, 255), 2)

    # -------- COLOR DETECTION --------
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 60, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    lower_brown = np.array([10, 100, 20])
    upper_brown = np.array([20, 255, 200])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)

    mask = cv2.bitwise_or(mask_white, mask_brown)

    edges = cv2.Canny(image, 50, 150)
    mask = cv2.bitwise_or(mask, edges)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for cnt in contours:
        if cv2.contourArea(cnt) > 700:
            x, y, bw, bh = cv2.boundingRect(cnt)
            cv2.rectangle(image, (x, y), (x + bw, y + bh), (0, 0, 255), 2)

    return image


#  MASK
def detect_trash_mask(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 60, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    lower_brown = np.array([10, 100, 20])
    upper_brown = np.array([20, 255, 200])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)

    mask = cv2.bitwise_or(mask_white, mask_brown)

    edges = cv2.Canny(image, 50, 150)
    mask = cv2.bitwise_or(mask, edges)

    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask