import math
import time

TIP_IDS = [4, 8, 12, 16, 20]

class GestureClassifier:
    def __init__(self):
        self.last_gesture = None
        self.gesture_start_time = 0
        self.min_hold_time = 1.0  # Minimum time to hold gesture before recognition
        
    def _calculate_distance(self, point1, point2):
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

    def _get_finger_states(self, lm_list):
        """
        Reliable finger state detection
        """
        if len(lm_list) != 21:
            return [0, 0, 0, 0, 0]

        fingers = []

        # Thumb detection - compare with wrist and MCP
        thumb_tip = lm_list[4]
        thumb_ip = lm_list[3]
        wrist = lm_list[0]
        
        # Thumb is extended if tip is significantly left of IP joint (right hand)
        if thumb_tip[0] < thumb_ip[0] - 15:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers: compare tip with PIP joint
        for tip_id, pip_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            tip = lm_list[tip_id]
            pip = lm_list[pip_id]
            
            # Finger is up if tip is above PIP joint with margin
            if tip[1] < pip[1] - 25:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def classify(self, lm_list, current_time):
        """
        Gesture classification with hold-time requirement
        """
        if not lm_list or len(lm_list) != 21:
            return None

        fingers = self._get_finger_states(lm_list)

        # Determine current gesture
        if fingers == [0, 0, 0, 0, 0]:
            new_gesture = "FIST"
        elif fingers == [1, 1, 1, 1, 1]:
            new_gesture = "OPEN_HAND"
        elif fingers == [1, 0, 0, 0, 0]:
            new_gesture = "THUMBS_UP"
        elif fingers == [0, 1, 0, 0, 0]:
            new_gesture = "POINT"
        elif fingers == [0, 1, 1, 0, 0]:
            new_gesture = "VICTORY"
        elif fingers == [0, 1, 1, 1, 0]:
            new_gesture = "THREE"
        elif fingers == [0, 0, 1, 1, 1]:
            new_gesture = "AWESOME"
        elif fingers == [0, 1, 1, 1, 1]:
            new_gesture = "FOUR"
        elif fingers == [1, 1, 0, 0, 1]:
            new_gesture = "LOVE_YOU"
        elif fingers == [0, 0, 0, 0, 1]:
            new_gesture = "PINKY_UP"
        elif fingers == [1, 0, 0, 0, 1]:
            new_gesture = "SHAKA"
        else:
            new_gesture = "UNKNOWN"

        # Check if gesture has changed
        if new_gesture != self.last_gesture:
            self.last_gesture = new_gesture
            self.gesture_start_time = current_time
            return None  # Don't recognize immediately on change
        
        # Check if gesture has been held long enough
        hold_duration = current_time - self.gesture_start_time
        if hold_duration >= self.min_hold_time:
            return new_gesture
        
        return None

    def is_hand_present(self, lm_list, min_landmark_distance=40):
        """
        Check if a valid hand is present
        """
        if not lm_list or len(lm_list) != 21:
            return False
        
        wrist = lm_list[0]
        middle_tip = lm_list[12]
        distance = self._calculate_distance(wrist, middle_tip)
        return distance > min_landmark_distance

    def get_hold_progress(self, current_time):
        """Get how long the current gesture has been held"""
        if not self.last_gesture:
            return 0
        hold_duration = current_time - self.gesture_start_time
        return min(hold_duration / self.min_hold_time, 1.0)