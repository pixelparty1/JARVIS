"""
JARVIS Speaker Module
Handles voice output and text-to-speech
"""

import pyttsx3
from config import VOICE_ENGINE, VOICE_RATE, VOICE_VOLUME
import threading

class VoiceSpeaker:
    """Text-to-speech handler"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', VOICE_RATE)
        self.engine.setProperty('volume', VOICE_VOLUME)
        
        # Try to set voice (optional, falls back to default)
        try:
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[1].id)  # Use second voice if available
        except:
            pass
    
    def speak(self, text: str, wait: bool = True):
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to finish
        """
        try:
            print(f"🔊 Speaking: {text}")
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
            else:
                # Run in background
                threading.Thread(target=self.engine.runAndWait, daemon=True).start()
        
        except Exception as e:
            print(f"❌ Speech error: {e}")
    
    def speak_async(self, text: str):
        """Speak text asynchronously"""
        self.speak(text, wait=False)
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            self.engine.stop()
        except:
            pass
    
    def set_volume(self, volume: float):
        """
        Set speaker volume (0.0-1.0)
        
        Args:
            volume: Volume level
        """
        if 0.0 <= volume <= 1.0:
            self.engine.setProperty('volume', volume)
            self.speak(f"Volume set to {int(volume * 100)} percent", wait=False)
    
    def set_rate(self, rate: int):
        """
        Set speech rate (words per minute)
        
        Args:
            rate: Speed in words per minute
        """
        self.engine.setProperty('rate', rate)
        self.speak(f"Speech rate set to {rate} words per minute", wait=False)
    
    def feedback(self, message: str):
        """Quick feedback sound/message"""
        # For now, just print (can be enhanced with sound effects)
        print(f"📢 {message}")
