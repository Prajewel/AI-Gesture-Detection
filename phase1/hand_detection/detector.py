import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, max_hands=2, detection_conf=0.8, tracking_conf=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.drawing_styles = mp.solutions.drawing_styles

    def find_hands(self, frame, draw=True):
        """
        Hand detection that preserves original frame resolution
        """
        # Flip frame for mirror-like viewing
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # To improve performance, mark the image as not writeable to pass by reference
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True
        
        hand_landmarks = []

        if results.multi_hand_landmarks:
            for hand_landmarks_mp in results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks_mp,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.drawing_styles.get_default_hand_landmarks_style(),
                        self.drawing_styles.get_default_hand_connections_style()
                    )
                hand_landmarks.append(hand_landmarks_mp)

        return frame, hand_landmarks