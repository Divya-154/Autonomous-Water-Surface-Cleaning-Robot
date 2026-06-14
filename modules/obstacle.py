import cv2
import numpy as np

def detect_obstacles(image):
    image = cv2.resize(image, (500, 500))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect dark objects
    _, mask = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)

    # Remove noise
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    display = image.copy()

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area > 3000:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 0, 255), 2)

    return mask