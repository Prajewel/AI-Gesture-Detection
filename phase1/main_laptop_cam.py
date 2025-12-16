import cv2
import time
import numpy as np

from hand_detection.detector import HandDetector
from hand_detection.landmark_utils import extract_landmarks
from hand_detection.gesture_classifier import GestureClassifier
from config.gesture_map import GESTURE_TO_TEXT, GESTURE_DISPLAY_NAMES
from tts.tts_engine_bulletproof import BulletproofTTSEngine as TTSEngine

class AdaptiveDisplayWindow:
    """Manages adaptive display window with dynamic resizing"""
    
    def __init__(self, window_name="Hand Sign Translator"):
        self.window_name = window_name
        self.current_scale = 1.0
        self.target_width = 900  # Initial target width
        self.target_height = 700  # Initial target height
        self.is_fullscreen = False
        
        # Create resizable window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.target_width, self.target_height)
        
        # Set mouse callback for window interaction
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for window interaction"""
        if event == cv2.EVENT_RBUTTONDOWN:
            # Right click to toggle fullscreen
            self.toggle_fullscreen()
    
    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, self.target_width, self.target_height)
    
    
    def get_display_size(self, frame_shape):
        """Calculate display size based on current window size"""
        # Get current window size
        window_width = cv2.getWindowImageRect(self.window_name)[2]
        window_height = cv2.getWindowImageRect(self.window_name)[3]
        
        # If window size is invalid, use default targets
        if window_width <= 0 or window_height <= 0:
            window_width = self.target_width
            window_height = self.target_height
        
        # Apply current scale
        display_width = int(window_width * self.current_scale)
        display_height = int(window_height * self.current_scale)
        
        # Maintain aspect ratio of original frame
        frame_height, frame_width = frame_shape[:2]
        original_aspect = frame_width / frame_height
        display_aspect = display_width / display_height
        
        if display_aspect > original_aspect:
            # Window is wider than frame - adjust width
            display_width = int(display_height * original_aspect)
        else:
            # Window is taller than frame - adjust height
            display_height = int(display_width / original_aspect)
        
        # Ensure minimum size
        display_width = max(display_width, 320)
        display_height = max(display_height, 240)
        
        return display_width, display_height
    
    def add_window_controls_overlay(self, frame):
        """Add overlay with window control instructions"""
        overlay = frame.copy()
        overlay_height = 100
        overlay_y = frame.shape[0] - overlay_height
        
        # Create semi-transparent overlay
        cv2.rectangle(overlay, (0, overlay_y), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Add control instructions
        controls = [
            "WINDOW CONTROLS:",
            "Drag corners to resize window",
            f"Current zoom: {self.current_scale:.1f}x",
            "'Q': Quit"
        ]
        
        for i, text in enumerate(controls):
            y_pos = overlay_y + 20 + i * 15
            color = (0, 255, 255) if i == 0 else (200, 200, 200)
            font_size = 0.5 if i > 0 else 0.6
            cv2.putText(frame, text, (20, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 1)
        
        return frame

def main():
    # Camera configuration - Use native camera resolution
    CAPTURE_WIDTH = 1280
    CAPTURE_HEIGHT = 720

    # 1. Open laptop camera
    cap = cv2.VideoCapture(0)
    
    # Try to set desired resolution, but use what camera supports
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Get actual camera resolution
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Camera Info:")
    print(f"Resolution: {actual_width} x {actual_height}")
    print(f"FPS: {actual_fps:.1f}")

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    # 2. Initialize components
    print("Initializing components...")
    detector = HandDetector(max_hands=1, detection_conf=0.8, tracking_conf=0.6)
    classifier = GestureClassifier()
    tts = TTSEngine()
    
    # Initialize adaptive display window
    display_window = AdaptiveDisplayWindow("Hand Sign Translator - Adaptive Display")
    
    # Wait for TTS initialization
    time.sleep(2)
    print("Components initialized successfully")
    

    # State variables for gesture tracking
    current_gesture = None
    last_spoken_gesture = None
    gesture_start_time = 0
    gesture_hold_required = 1.0
    
    # Performance tracking
    fps_history = []
    last_fps_time = time.time()
    frame_count = 0

    print("\nAdaptive Display Hand Sign Translator Started!")
    print("Window automatically adjusts to your screen size")
    print("Use mouse controls: Right-click fullscreen, Scroll zoom")
    print("Hold gesture for 1 second to trigger speech")

    try:
        while True:
            # Start timing for FPS calculation
            frame_start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
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
                    gesture_label = classifier.classify(lm_list, current_time)
                    hold_progress = classifier.get_hold_progress(current_time)

                    if gesture_label and gesture_label != "UNKNOWN":
                        display_name = GESTURE_DISPLAY_NAMES.get(gesture_label, gesture_label)
                        
                        if gesture_label != last_spoken_gesture:
                            gesture_start_time = current_time
                            last_spoken_gesture = gesture_label
                        
                        hold_duration = current_time - gesture_start_time
                        hold_percent = min(hold_duration / gesture_hold_required, 1.0)
                        
                        if hold_duration >= gesture_hold_required:
                            detected_text = GESTURE_TO_TEXT.get(gesture_label, "Unknown gesture")
                            status_color = (0, 255, 0)
                            status_text = f"{display_name}"
                            gesture_start_time = current_time
                        else:
                            status_color = (82, 267, 54)
                            progress_pct = int(hold_percent * 100)
                            status_text = f"{display_name} ({progress_pct}%)"

                        # Calculate dynamic text size based on frame size
                        frame_height, frame_width = processed_frame.shape[:2]
                        base_text_scale = max(0.5, min(1.5, frame_width / 1280))
                        base_text_thickness = max(1, int(frame_width / 640))
                        
                        # Display gesture information with dynamic sizing
                        cv2.putText(
                            processed_frame,
                            status_text,
                            (int(30 * frame_width / 1280), int(50 * frame_height / 720)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            base_text_scale,
                            status_color,
                            base_text_thickness,
                        )
                        
                        # Dynamic progress bar
                        bar_width = int(300 * frame_width / 1280)
                        bar_height = int(20 * frame_height / 720)
                        bar_x = int(30 * frame_width / 1280)
                        bar_y = int(90 * frame_height / 720)
                        filled_width = int(bar_width * hold_percent)
                        
                        cv2.rectangle(processed_frame, (bar_x, bar_y), 
                                     (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
                        cv2.rectangle(processed_frame, (bar_x, bar_y), 
                                     (bar_x + filled_width, bar_y + bar_height), status_color, -1)
                        cv2.rectangle(processed_frame, (bar_x, bar_y), 
                                     (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 1)

            else:
                current_gesture = None
                last_spoken_gesture = None
                gesture_start_time = 0
                
                # Dynamic "no hand" text
                frame_height, frame_width = processed_frame.shape[:2]
                text_scale = max(0.8, min(2.0, frame_width / 800))
                
                cv2.putText(
                    processed_frame,
                    "Show your hand to the camera",
                    (int(30 * frame_width / 1280), int(50 * frame_height / 720)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    text_scale,
                    (0, 0, 255),
                    max(2, int(frame_width / 400)),
                )

            # 5. Handle speech output
            if detected_text:
                frame_height, frame_width = processed_frame.shape[:2]
                text_scale = max(0.6, min(1.2, frame_width / 1280))
                
                cv2.putText(
                    processed_frame,
                    f": {detected_text}",
                    (int(30 * frame_width / 1280), int(130 * frame_height / 720)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    text_scale,
                    (255, 255, 0),
                    max(1, int(frame_width / 640)),
                )
                
                print(f"TRIGGERING SPEECH: {detected_text}")
                tts.speak(detected_text)

            # 6. Calculate and display FPS
            frame_end_time = time.time()
            fps = 1.0 / (frame_end_time - frame_start_time)
            fps_history.append(fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            
            avg_fps = sum(fps_history) / len(fps_history)
            
            # Dynamic FPS display
            frame_height, frame_width = processed_frame.shape[:2]
            fps_text_scale = max(0.4, min(0.8, frame_width / 1600))
            
            fps_color = (0, 255, 0) if avg_fps > 20 else (0, 165, 255) if avg_fps > 10 else (0, 0, 255)
            cv2.putText(
                processed_frame,
                f"FPS: {avg_fps:.1f} | Zoom: {display_window.current_scale:.1f}x",
                (frame_width - 300, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                fps_text_scale,
                fps_color,
                1,
            )

            # 7. Add window controls overlay
            processed_frame = display_window.add_window_controls_overlay(processed_frame)

            # 8. Adaptive display resizing
            display_width, display_height = display_window.get_display_size(processed_frame.shape)
            
            # Resize frame for display (maintain aspect ratio)
            display_frame = cv2.resize(processed_frame, (display_width, display_height), 
                                      interpolation=cv2.INTER_AREA if display_width < processed_frame.shape[1] 
                                      else cv2.INTER_LINEAR)

            # 9. Display frame
            cv2.imshow(display_window.window_name, display_frame)

            # 10. Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('t'):
                # Manual TTS test
                test_text = f"Manual test at frame {frame_count}"
                print(f"MANUAL TEST: {test_text}")
                tts.speak(test_text)
            elif key == ord('f'):
                # Toggle fullscreen with keyboard
                display_window.toggle_fullscreen()
                print(f"Fullscreen: {display_window.is_fullscreen}")
    except Exception as e:
        print(f"Main loop error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        tts.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("\nAdaptive Display Application closed successfully")

if __name__ == "__main__":
    main()