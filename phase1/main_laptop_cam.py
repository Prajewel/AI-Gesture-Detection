import cv2
import time
import numpy as np

from hand_detection.detector import HandDetector
from hand_detection.landmark_utils import extract_landmarks
from hand_detection.gesture_classifier import GestureClassifier
from config.gesture_map import GESTURE_TO_TEXT, GESTURE_DISPLAY_NAMES
from tts.tts_engine_bulletproof import BulletproofTTSEngine as TTSEngine

def main():
    # Camera configuration
    CAPTURE_WIDTH = 720
    CAPTURE_HEIGHT = 680

    # 1. Open laptop camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"📷 Camera resolution: {actual_width} x {actual_height}")

    if not cap.isOpened():
        print("❌ Error: Cannot open camera")
        return

    # 2. Initialize components
    print("🔄 Initializing Hand Detector...")
    detector = HandDetector(max_hands=1, detection_conf=0.8, tracking_conf=0.6)
    
    print("🔄 Initializing Gesture Classifier...")
    classifier = GestureClassifier()
    
    print("🔄 Initializing Bulletproof TTS Engine...")
    tts = TTSEngine()
    
    # Wait a moment for TTS to initialize
    time.sleep(2)
    
    # Test TTS immediately
    print("🔊 Testing TTS with startup message...")
    tts.speak("Hand sign translator started successfully")

    # State variables for gesture tracking
    current_gesture = None
    last_spoken_gesture = None
    gesture_start_time = 0
    gesture_hold_required = 1.0  # Hold gesture for 1 second
    
    print("🚀 Starting RELIABLE Hand Sign Translator")
    print("🎯 Every gesture change will trigger speech")
    print("⏱️  Hold gesture for 1 second to activate")

    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break

            frame_count += 1
            current_time = time.time()

            # 3. Detect hand
            processed_frame, hands = detector.find_hands(frame, draw=True)

            detected_text = None
            gesture_label = None

            # 4. Process hand detection
            if hands:
                lm_list = extract_landmarks(hands[0], processed_frame.shape)
                
                if classifier.is_hand_present(lm_list):
                    # Get gesture classification
                    gesture_label = classifier.classify(lm_list, current_time)
                    hold_progress = classifier.get_hold_progress(current_time)

                    if gesture_label and gesture_label != "UNKNOWN":
                        display_name = GESTURE_DISPLAY_NAMES.get(gesture_label, gesture_label)
                        
                        # Check if this is a new confirmed gesture
                        if gesture_label != last_spoken_gesture:
                            # Gesture changed - reset timing
                            gesture_start_time = current_time
                            last_spoken_gesture = gesture_label
                            print(f"🔄 Gesture changed to: {gesture_label}")
                        
                        # Check if gesture has been held long enough
                        hold_duration = current_time - gesture_start_time
                        hold_percent = min(hold_duration / gesture_hold_required, 1.0)
                        
                        if hold_duration >= gesture_hold_required:
                            # Gesture confirmed - trigger speech
                            detected_text = GESTURE_TO_TEXT.get(gesture_label, "Unknown gesture")
                            status_color = (0, 255, 0)  # Green
                            status_text = f"CONFIRMED: {display_name}"
                            
                            # Reset timing for next speech (but keep same gesture)
                            gesture_start_time = current_time
                            
                        else:
                            # Still holding gesture
                            status_color = (0, 165, 255)  # Orange
                            progress_pct = int(hold_percent * 100)
                            status_text = f"HOLDING: {display_name} ({progress_pct}%)"

                        # Display gesture information
                        cv2.putText(
                            processed_frame,
                            status_text,
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            status_color,
                            2,
                        )
                        
                        # Progress bar
                        bar_width = 300
                        bar_height = 20
                        bar_x = 30
                        bar_y = 90
                        filled_width = int(bar_width * hold_percent)
                        
                        cv2.rectangle(processed_frame, (bar_x, bar_y), 
                                     (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
                        cv2.rectangle(processed_frame, (bar_x, bar_y), 
                                     (bar_x + filled_width, bar_y + bar_height), status_color, -1)
                        cv2.rectangle(processed_frame, (bar_x, bar_y), 
                                     (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 1)
                        
                        cv2.putText(
                            processed_frame,
                            f"Hold {gesture_hold_required}s to speak",
                            (bar_x + bar_width + 10, bar_y + 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1,
                        )

            else:
                # No hand detected - reset state
                current_gesture = None
                last_spoken_gesture = None
                gesture_start_time = 0
                
                cv2.putText(
                    processed_frame,
                    "👋 Show your hand to the camera",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            # 5. Handle speech output - THIS IS THE KEY PART
            if detected_text:
                cv2.putText(
                    processed_frame,
                    f"🔊: {detected_text}",
                    (30, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2,
                )
                
                # FORCE SPEECH - this will work every time with bulletproof engine
                print(f"🎯 TRIGGERING SPEECH: {detected_text}")
                tts.speak(detected_text)

            # 6. Display debug information
            cv2.putText(
                processed_frame,
                f"Frame: {frame_count} | TTS Queue: {tts.speech_queue.qsize()}",
                (30, processed_frame.shape[0] - 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            
            cv2.putText(
                processed_frame,
                "Press 'q' to quit | 't' to test TTS | Change gesture for speech",
                (30, processed_frame.shape[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
            )

            # 7. Display frame
            cv2.imshow("🎯 RELIABLE Hand Sign Translator - Speech EVERY Time", processed_frame)

            # 8. Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('t'):
                # Manual TTS test
                test_text = f"Manual test at frame {frame_count}"
                print(f"🔊 MANUAL TEST: {test_text}")
                tts.speak(test_text)

    except Exception as e:
        print(f"❌ Main loop error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tts.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Application closed successfully")

if __name__ == "__main__":
    main()
    