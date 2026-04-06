"""
Worker Threads for JARVIS Backend
Non-blocking execution of AI and voice operations
"""

from PyQt5.QtCore import QThread, pyqtSignal
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain import JarvisBrain
from command_router import CommandRouter
import traceback


class JarvisWorkerThread(QThread):
    """
    Worker thread for AI query processing
    Emits signals to update UI without blocking
    """
    
    # Signals
    response_ready = pyqtSignal(str)  # Response text
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self, user_input: str):
        super().__init__()
        self.user_input = user_input
        self.brain = None
        self.command_router = None
    
    def run(self):
        """Execute AI query in background thread"""
        try:
            # Initialize brain if not already done
            if self.brain is None:
                from config import GROQ_API_KEY, GROQ_MODEL
                self.brain = JarvisBrain()
            
            # Check if it's a command
            if self.command_router is None:
                self.command_router = CommandRouter()
            
            # Check for system commands first
            if any(cmd in self.user_input.lower() for cmd in ['time', 'date', 'open', 'close', 'execute']):
                result = self.command_router.route_command(self.user_input)
                if result and result != "Command not recognized":
                    self.response_ready.emit(result)
                    return
            
            # Send to Groq for AI response
            response = self.brain.query(self.user_input, stream=False)
            self.response_ready.emit(response)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)


class VoiceListenerThread(QThread):
    """
    Worker thread for voice recognition
    Listens for speech input without blocking UI
    """
    
    # Signals
    speech_recognized = pyqtSignal(str)  # Recognized text
    listening_started = pyqtSignal()     # UI indicator
    listening_stopped = pyqtSignal()     # UI indicator
    error_occurred = pyqtSignal(str)     # Error message
    
    def __init__(self):
        super().__init__()
        self.is_listening = True
        self.listener = None
    
    def run(self):
        """Listen for voice input in background thread"""
        try:
            from listener import VoiceListener
            from config import SPEECH_RECOGNITION_TIMEOUT
            
            self.listener = VoiceListener()
            self.listening_started.emit()
            
            # Listen for speech
            text = self.listener.listen_for_command(timeout=SPEECH_RECOGNITION_TIMEOUT)
            
            if text:
                self.speech_recognized.emit(text)
            else:
                self.error_occurred.emit("No speech detected")
            
            self.listening_stopped.emit()
            
        except Exception as e:
            error_msg = f"Voice Error: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.listening_stopped.emit()
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.quit()
        self.wait()


class VoiceOutputThread(QThread):
    """
    Worker thread for text-to-speech output
    Plays audio without blocking UI
    """
    
    # Signals
    speaking_started = pyqtSignal()
    speaking_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.speaker = None
    
    def run(self):
        """Speak text in background thread"""
        try:
            from speaker import VoiceSpeaker
            
            self.speaker = VoiceSpeaker()
            self.speaking_started.emit()
            
            # Speak the text
            self.speaker.speak(self.text, wait=True)
            
            self.speaking_finished.emit()
            
        except Exception as e:
            error_msg = f"TTS Error: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.speaking_finished.emit()
