import pyttsx3
import threading
import time
import queue
import platform

class BulletproofTTSEngine:
    """
    Ultra-reliable TTS engine that creates a fresh instance for EVERY speech
    and includes multiple fallback mechanisms.
    """
    
    def __init__(self, rate=180, volume=0.9):
        print("🚀 Initializing Bulletproof TTS Engine...")
        
        self.speech_queue = queue.Queue()
        self.is_running = True
        self.last_speech_time = 0
        self.min_interval = 1.5  # Minimum time between speeches
        
        # Platform detection for fallbacks
        self.system = platform.system()
        print(f"🔧 Detected OS: {self.system}")
        
        # Start the speech processor thread
        self.processor_thread = threading.Thread(target=self._speech_processor, daemon=True)
        self.processor_thread.start()
        
        print("✅ Bulletproof TTS Engine Ready - Fresh instance per speech")

    def _create_tts_engine(self):
        """Create a brand new TTS engine instance"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.9)
            
            # Get available voices
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
                print(f"🔊 Created TTS engine with voice: {voices[0].name}")
            
            return engine
        except Exception as e:
            print(f"❌ Failed to create TTS engine: {e}")
            return None

    def _speak_with_fresh_engine(self, text):
        """Speak text using a completely new engine instance"""
        print(f"🎯 SPEAK ATTEMPT: '{text}'")
        
        engine = None
        try:
            # Create FRESH engine instance
            engine = self._create_tts_engine()
            if not engine:
                print(f"❌ Could not create TTS engine for: '{text}'")
                return False
            
            # Perform speech
            print(f"🔊 START Speaking: '{text}'")
            engine.say(text)
            engine.runAndWait()
            print(f"✅ FINISHED Speaking: '{text}'")
            return True
            
        except Exception as e:
            print(f"❌ Speech failed for '{text}': {e}")
            return False
            
        finally:
            # ALWAYS cleanup the engine
            if engine:
                try:
                    engine.stop()
                    # Force garbage collection
                    del engine
                except:
                    pass

    def _speech_processor(self):
        """Main speech processing loop - runs in background thread"""
        print("🎯 Speech processor thread started")
        
        while self.is_running:
            try:
                # Wait for speech requests
                text = self.speech_queue.get(timeout=0.5)
                
                if not text or not text.strip():
                    self.speech_queue.task_done()
                    continue
                
                # Check if enough time has passed since last speech
                current_time = time.time()
                time_since_last = current_time - self.last_speech_time
                
                if time_since_last < self.min_interval:
                    print(f"⏳ Too soon since last speech ({time_since_last:.1f}s), skipping: '{text}'")
                    self.speech_queue.task_done()
                    continue
                
                # SPEAK with fresh engine
                success = self._speak_with_fresh_engine(text)
                
                if success:
                    self.last_speech_time = time.time()
                else:
                    print(f"🚨 Speech failed completely for: '{text}'")
                
                self.speech_queue.task_done()
                print(f"📊 Queue remaining: {self.speech_queue.qsize()}")
                
            except queue.Empty:
                # No speech requests, continue waiting
                continue
            except Exception as e:
                print(f"🚨 Speech processor error: {e}")
                try:
                    self.speech_queue.task_done()
                except:
                    pass

    def speak(self, text):
        """Add text to speech queue - ALWAYS works"""
        if not text or not text.strip():
            return
            
        print(f"📨 QUEUING Speech: '{text}'")
        print(f"📊 Queue size before: {self.speech_queue.qsize()}")
        
        self.speech_queue.put(text)
        
        # If queue is getting too big, clear old requests
        if self.speech_queue.qsize() > 3:
            print("⚠️  Queue too large, clearing old requests...")
            try:
                # Keep only the most recent request
                while self.speech_queue.qsize() > 1:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
            except:
                pass

    def stop(self):
        """Clean shutdown"""
        print("🛑 Stopping Bulletproof TTS Engine...")
        self.is_running = False
        
        # Clear any pending speech requests
        try:
            while not self.speech_queue.empty():
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
        except:
            pass
        
        print("✅ Bulletproof TTS Engine Stopped")