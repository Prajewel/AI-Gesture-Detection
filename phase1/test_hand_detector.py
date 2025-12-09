# Test script for the HandDetector class from hand_detection/detector.py
# This script captures video from the laptop camera, detects hands,
# and displays the video with hand landmarks drawn.

import cv2
import mediapipe as mp
import numpy as np
from hand_detection.detector import HandDetector
from hand_detection.landmark_utils import extract_landmarks

def main():
    cap = cv2.VideoCapture(0)
    
    # Set resolution for better visibility
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize detector for 2 hands
    detector = HandDetector(max_hands=2, detection_conf=0.8, tracking_conf=0.5)

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    print("🎯 Hand Detection Test Started")
    print("📊 Displaying landmark coordinates for BOTH hands")
    print("👐 Show 0, 1, or 2 hands to the camera")
    print("📝 Values shown: (x, y) coordinates")
    print("🚫 Press 'q' to quit | Press 's' to save current frame")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        frame, hands = detector.find_hands(frame, draw=True)

        # Display hand count
        cv2.putText(frame, f"Hands Detected: {len(hands)}", (30, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Process each hand
        for hand_idx, hand in enumerate(hands):
            # Extract landmarks
            lm_list = extract_landmarks(hand, frame.shape)
            
            # Draw hand label (Left/Right)
            if hand_idx == 0:
                hand_label = "Hand 1 (First)"
                color = (255, 0, 0)  # Blue
            else:
                hand_label = "Hand 2 (Second)"
                color = (0, 255, 255)  # Yellow
            
            # Draw hand label
            cv2.putText(frame, hand_label, (30, 80 + hand_idx * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Display key landmarks with their indices
            key_landmarks = {
                0: "WRIST",
                4: "THUMB_TIP",
                5: "THUMB_IP",
                6: "THUMB_MCP",
                8: "INDEX_TIP",
                12: "MIDDLE_TIP",
                16: "RING_TIP",
                20: "PINKY_TIP",
                9: "INDEX_PIP",
                13: "MIDDLE_PIP",
                17: "RING_PIP",
                21: "PINKY_PIP"
            }

            # Display coordinates for key landmarks
            y_offset = 120 + hand_idx * 160
            for i, landmark_name in key_landmarks.items():
                if i < len(lm_list):
                    x, y = lm_list[i]
                    
                    # Draw circle on the landmark
                    cv2.circle(frame, (x, y), 8, color, -1)
                    cv2.putText(frame, str(i), (x-10, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Display coordinate on screen
                    coord_text = f"{landmark_name}: ({x}, {y})"
                    cv2.putText(frame, coord_text, (30, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                    y_offset += 25

            # Display all 21 landmarks in a compact format
            if hand_idx == 0:  # Only show for first hand to avoid clutter
                cv2.putText(frame, "All 21 Landmarks (x,y):", (30, y_offset + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display landmarks in rows
                for row in range(7):  # 7 rows of 3 landmarks each
                    start_idx = row * 3
                    landmarks_row = []
                    for i in range(start_idx, min(start_idx + 3, 21)):
                        if i < len(lm_list):
                            x, y = lm_list[i]
                            landmarks_row.append(f"{i}:({x:3d},{y:3d})")
                    
                    if landmarks_row:
                        row_text = "  ".join(landmarks_row)
                        cv2.putText(frame, row_text, (30, y_offset + 45 + row * 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Display instructions and frame info
        cv2.putText(frame, "Instructions:", (30, frame.shape[0] - 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "1. Show open hand for OPEN_HAND gesture", (30, frame.shape[0] - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "2. Make fist for FIST gesture", (30, frame.shape[0] - 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "3. Show thumbs up for THUMBS_UP", (30, frame.shape[0] - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "Press 'q' to quit | 's' to save frame | 'c' to clear", (30, frame.shape[0] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # Show frame
        cv2.imshow("Hand Detection - Landmark Values Display", frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save current frame
            filename = f"hand_detection_frame_{frame_count}.png"
            cv2.imwrite(filename, frame)
            print(f"💾 Frame saved as {filename}")
        elif key == ord('c'):
            # Print landmark data to console
            if hands:
                print(f"\n📊 Frame {frame_count} - Landmark Data:")
                for hand_idx, hand in enumerate(hands):
                    lm_list = extract_landmarks(hand, frame.shape)
                    print(f"  Hand {hand_idx + 1} - 21 Landmarks:")
                    for i, (x, y) in enumerate(lm_list):
                        print(f"    {i:2d}: ({x:4d}, {y:4d})")
                print("-" * 50)

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Hand detection test completed")

if __name__ == "__main__":
    main()



# To run this test, ensure you have OpenCV and MediaPipe installed:
# pip install opencv-python mediapipe
# Then execute: python test_hand_detector.py
