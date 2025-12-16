Hand Sign Detection and Sign to Speech Translator

📌 Project Overview

A real-time hand gesture recognition system that detects hand signs using computer vision and converts them to speech output. The system uses MediaPipe for hand landmark detection and pyttsx3 for text-to-speech conversion.

🎯 Features

· Real-time hand gesture detection using laptop camera
· Support for multiple gestures (Fist, Open Hand, Thumbs Up, Point, Victory, etc.)
· Text-to-speech output for detected gestures
· 1280x720 resolution for both capture and display
· Consistent speech output for every gesture change
· Visual feedback with landmark overlays

🏗️ Project Structure

```
hand_sign_translator/
├── phase1_laptop_cam/
│   ├── main_laptop_cam.py              # Main application
│   ├── video_preview.py                # Basic camera test
│   ├── test_hand_detector.py           # Hand detection test
│   ├── requirements.txt                # Dependencies
│   ├── hand_detection/
│   │   ├── __init__.py
│   │   ├── detector.py                 # Hand detection logic
│   │   ├── landmark_utils.py           # Landmark extraction
│   │   └── gesture_classifier.py       # Gesture classification
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── tts_engine.py              # Text-to-speech engine
│   │   └── tts_engine_bulletproof.py  # Robust TTS alternative
│   └── config/
│       ├── __init__.py
│       └── gesture_map.py             # Gesture to text mapping
└── README.md                          # This file
```

🚀 Installation & Setup

Prerequisites

· Python 3.8 or higher
· VS Code installed
· Webcam connected to your computer

Step 1: Clone and Setup in VS Code

1. Open VS Code
2. Open Command Palette (Ctrl+Shift+P or Cmd+Shift+P on Mac)
3. Type and select: "Git: Clone"
4. Enter the repository URL
5. Choose where to save the project
6. Click "Open" when prompted

Step 2: Create Virtual Environment in VS Code

1. Open Terminal in VS Code:
   · View → Terminal or `Ctrl+`` (backtick)
2. Create virtual environment:
   ```bash
   # Windows
   python -m venv venv
   
   # macOS/Linux
   python3 -m venv venv
   ```
3. Activate virtual environment:
   · Windows (Command Prompt):
     ```bash
     venv\Scripts\activate
     ```
   · Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     If you get an execution policy error, run this first:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```
   · macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   You'll see (venv) in the terminal prompt when activated.
4. Install dependencies:
   ```bash
   cd phase1_laptop_cam
   pip install -r requirements.txt
   ```

Step 3: Configure Python Interpreter in VS Code

1. Open Command Palette (Ctrl+Shift+P)
2. Type and select: "Python: Select Interpreter"
3. Choose the virtual environment:
   · ./venv/Scripts/python.exe (Windows)
   · ./venv/bin/python (macOS/Linux)

🎮 How to Run the Project

Option 1: Run from VS Code Terminal

1. Ensure virtual environment is activated (you should see (venv) in terminal)
2. Navigate to project directory:
   ```bash
   cd phase1_laptop_cam
   ```
3. Run the main application:
   ```bash
   python main_laptop_cam.py
   ```

Option 2: Use VS Code Run Configuration

1. Open main_laptop_cam.py in VS Code
2. Click the Run button (▶️) in the top-right corner
3. Select "Python File" from the dropdown

Or press F5 to run with debugging

Option 3: Run Test Files

1. Test camera only:
   ```bash
   python video_preview.py
   ```
2. Test hand detection:
   ```bash
   python test_hand_detector.py
   ```
3. Test advanced hand detection with values:
   ```bash
   python test_hand_detector_advanced.py
   ```

🎯 Available Gestures

The system recognizes these gestures:

Gesture Display Name Speech Output
✊ Fist "Stop please!"
👋 Open Hand "Hello there!"
👍 Thumbs Up "Yes, good job!"
👆 Point "You are pointing!"
✌️ Victory "Victory! Well done!"
🤟 Three Fingers "Number three!"
🤘 Rock Sign "Rock and roll!"
🖖 Pinky Up "Pinky promise!"
🤙 Shaka Sign "Shaka, hang loose!"

🖥️ Using the Application

1. Position your hand clearly in front of the camera
2. Hold the gesture steady for 1 second
3. Wait for the system to confirm with green text
4. Speech will automatically play for the detected gesture
5. Change gesture to trigger new speech

Controls:

· q - Quit application
· t - Test TTS manually

🔧 Troubleshooting

Issue: Camera not opening

· Ensure no other application is using the camera
· Check camera permissions
· Try changing camera index in code (0 → 1)

Issue: No sound output

1. Check system volume
2. Verify speakers/headphones are connected
3. Test TTS directly:
   ```bash
   python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Test'); engine.runAndWait()"
   ```

Issue: Gestures not detected

· Ensure good lighting
· Keep hand clearly visible
· Avoid complex backgrounds
· Try different distances from camera

Issue: Import errors in VS Code

1. Select correct interpreter (see Step 3 above)
2. Reload VS Code window: Ctrl+Shift+P → "Developer: Reload Window"
3. Reinstall dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

📝 VS Code Extensions (Recommended)

Install these extensions for better development experience:

1. Python (Microsoft) - Python language support
2. Python Indent - Correct Python indentation
3. Pylance - Python language server
4. Python Docstring Generator - Auto-generate docstrings
5. Code Runner - Run code snippets quickly

To install extensions:

1. Click Extensions icon in sidebar (or Ctrl+Shift+X)
2. Search for extension name
3. Click Install

🐛 Debugging in VS Code

1. Set breakpoints by clicking left gutter next to line numbers
2. Press F5 to start debugging
3. Use debug toolbar:
   · Continue (F5)
   · Step Over (F10)
   · Step Into (F11)
   · Step Out (Shift+F11)
   · Restart (Ctrl+Shift+F5)
   · Stop (Shift+F5)
4. Watch variables in Debug sidebar
5. Check Debug Console for output

📊 Understanding the Output

When running the application, you'll see:

1. Visual Feedback:
   · Green landmarks on detected hands
   · Gesture name and status
   · Progress bar for gesture hold time
   · Speech output text
2. Console Output:
   · System initialization status
   · TTS engine status
   · Gesture detection logs
   · Speech queue information

🔄 Updating the Project

To add new gestures:

1. Edit config/gesture_map.py:
   ```python
   GESTURE_TO_TEXT = {
       # Add new gesture here
       "NEW_GESTURE": "Speech output text",
   }
   ```
2. Update hand_detection/gesture_classifier.py to recognize the new gesture pattern

📁 Git Commands for Project Management

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to repository
git push origin main

# Pull latest changes
git pull origin main
```

🚨 Common Errors & Solutions

Error Solution
ModuleNotFoundError: No module named 'mediapipe' Run pip install mediapipe
AttributeError: module 'cv2' has no attribute 'VideoCapture' Reinstall OpenCV: pip install opencv-python
No camera detected Check camera connection and permissions
TTS not working after first speech Use tts_engine_bulletproof.py instead
Import errors in VS Code Select correct Python interpreter

📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure Python interpreter is set correctly in VS Code
4. Check camera and audio device connections

📄 License

This project is for educational purposes. Feel free to modify and extend it for your needs.

---

Happy Coding! 🚀
