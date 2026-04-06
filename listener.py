"""
JARVIS Listener Module
Handles voice input and wake word detection
"""

import speech_recognition as sr
from typing import Optional
from config import WAKE_WORD, SPEECH_RECOGNITION_TIMEOUT, SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
import threading

class VoiceListener:
    """Voice input handler with wake word detection"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.wake_word = WAKE_WORD.lower()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def listen_for_wake_word(self) -> bool:
        """
        Listen continuously for wake word
        Returns True when wake word is detected
        """
        print(f"🎤 Listening for wake word: '{self.wake_word}'...")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=SPEECH_RECOGNITION_TIMEOUT,
                    phrase_time_limit=SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
                )
            
            text = self.recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}")
            
            if self.wake_word in text:
                print(f"✅ Wake word detected!")
                return True
            
            return False
            
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def listen_for_command(self) -> Optional[str]:
        """
        Listen for user command after wake word detected
        Returns the recognized text or None
        """
        print("🎤 Listening for command...")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=SPEECH_RECOGNITION_TIMEOUT,
                    phrase_time_limit=SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
                )
            
            text = self.recognizer.recognize_google(audio)
            print(f"✅ Command received: {text}")
            return text
            
        except sr.UnknownValueError:
            print("❌ Could not understand command")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def continuous_listen(self, callback, wake_word_callback=None):
        """
        Continuously listen for wake word and commands
        
        Args:
            callback: Function to call with recognized command text
            wake_word_callback: Optional function to call when wake word detected
        """
        self.listening = True
        print(f"🎤 Started continuous listening")
        
        while self.listening:
            # Listen for wake word
            if self.listen_for_wake_word():
                if wake_word_callback:
                    wake_word_callback()
                
                # Listen for command
                command = self.listen_for_command()
                if command:
                    callback(command)
            
            # Brief pause before next attempt
            import time
            time.sleep(0.5)
    
    def start_continuous_listen_thread(self, callback, wake_word_callback=None):
        """Start continuous listening in a background thread"""
        thread = threading.Thread(
            target=self.continuous_listen,
            args=(callback, wake_word_callback),
            daemon=True
        )
        thread.start()
        return thread
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False
        print("🎤 Stopped listening")
    
    def get_input_with_timeout(self, timeout: int = 30) -> Optional[str]:
        """Get voice input with timeout fallback"""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
            return self.recognizer.recognize_google(audio)
        except Exception as e:
            print(f"Voice input failed: {e}")
            return None
