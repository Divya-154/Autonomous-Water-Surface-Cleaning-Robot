import cv2
import numpy as np

def detect_living_objects(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Detect green-ish (frog/plant or living objects avoidance simulation)
    lower = np.array([35, 50, 50])
    upper = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    return mask