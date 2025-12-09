import pyttsx3
import threading
import time
import queue

class TTSEngine:
    def __init__(self, rate=180, volume=0.9):
        print("🔄 TTS Engine: Starting initialization...")
        
        self.speech_queue = queue.Queue()
        self.is_ready = True
        self.last_speech_time = 0
        self.speech_cooldown = 2.0
        
        # Initialize engine in a separate thread to avoid blocking
        self.init_thread = threading.Thread(target=self._initialize_engine, daemon=True)
        self.init_thread.start()
        
        # Start speech processing thread
        self.speech_thread = threading.Thread(target=self._speech_processor, daemon=True)
        self.speech_thread.start()
        
        print("✅ TTS Engine: Initialization started in background...")

    def _initialize_engine(self):
        """Initialize engine in background thread"""
        try:
            print("🔧 TTS: Creating new engine instance...")
            self.engine = pyttsx3.init()
            
            # Configure engine
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.9)
            
            # Get voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                print(f"🔊 TTS: Using voice: {voices[0].name}")
            
            # Test the engine works
            print("🔧 TTS: Testing engine with quick phrase...")
            self.engine.say("Ready")
            self.engine.runAndWait()
            
            self.is_ready = True
            print("✅ TTS Engine: Fully initialized and tested!")
            
        except Exception as e:
            print(f"❌ TTS Engine initialization failed: {e}")
            self.engine = None

    def _speech_processor(self):
        """Process speech requests - creates new engine for each speech"""
        print("🎯 TTS Processor: Speech processor started")
        
        while True:
            try:
                # Wait for speech request
                text = self.speech_queue.get(timeout=1)
                
                if not text or not text.strip():
                    self.speech_queue.task_done()
                    continue
                
                # Check cooldown
                current_time = time.time()
                if current_time - self.last_speech_time < self.speech_cooldown:
                    print(f"⏳ TTS: Cooldown active, skipping: '{text}'")
                    self.speech_queue.task_done()
                    continue
                
                # Speak using FRESH engine instance each time
                self._speak_with_fresh_engine(text)
                self.last_speech_time = time.time()
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ TTS Processor error: {e}")
                try:
                    self.speech_queue.task_done()
                except:
                    pass

    def _speak_with_fresh_engine(self, text):
        """Create a fresh engine instance for each speech to avoid freezing"""
        print(f"🔊 TTS: Attempting to speak: '{text}'")
        
        engine = None
        try:
            # Create NEW engine instance
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.9)
            
            # Get voices and set first available
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            
            # Speak
            print(f"🎯 TTS: START speaking: '{text}'")
            engine.say(text)
            engine.runAndWait()
            print(f"✅ TTS: FINISHED speaking: '{text}'")
            
        except Exception as e:
            print(f"❌ TTS Speech error: {e}")
        finally:
            # Always clean up the engine
            if engine:
                try:
                    engine.stop()
                    del engine
                except:
                    pass

    def speak(self, text: str):
        """Add text to speech queue"""
        if not text or not text.strip():
            return
            
        print(f"📨 TTS: Queueing speech: '{text}'")
        self.speech_queue.put(text)

    def stop(self):
        """Cleanup"""
        print("🛑 TTS: Stopping engine...")
        try:
            # Clear queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except:
                    break
        except:
            pass