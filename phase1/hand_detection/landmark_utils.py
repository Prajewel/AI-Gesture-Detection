# Utility functions for processing hand landmarks
# This module provides functions to convert MediaPipe hand landmarks
# into more usable formats such as pixel coordinates.

def extract_landmarks(handLms, frame_shape):
    """
    Convert MediaPipe landmarks to list of (x, y) pixel coordinates.

    handLms: mediapipe hand landmarks
    frame_shape: frame.shape from OpenCV (h, w, c)
    """
    h, w, _ = frame_shape
    lm_list = []
    for lm in handLms.landmark:
        x, y = int(lm.x * w), int(lm.y * h)
        lm_list.append((x, y))
    return lm_list
