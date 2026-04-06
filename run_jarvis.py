#!/usr/bin/env python3
"""
JARVIS - Main Entry Point

Start the entire JARVIS system with:
- Groq reasoning engine
- Voice recognition
- Speech synthesis
- Command routing
- Wake word detection

Usage:
    python run_jarvis.py              # Start with voice
    python run_jarvis.py --text-only  # Start with text input only
    python run_jarvis.py --debug      # Debug mode
"""

import logging
import sys
import random
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import components
try:
    from config import (
        WAKE_WORD, GREETING_RESPONSES, 
        WAKE_WORD_TIMEOUT, ENABLE_VOICE, DEBUG_MODE
    )
    from brain import JarvisBrain
    from listener import VoiceListener
    from speaker import VoiceSpeaker
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files exist in the project root")
    sys.exit(1)


class JARVIS:
    """Main JARVIS system orchestrator"""
    
    def __init__(self, text_only: bool = False, debug: bool = False):
        """
        Initialize JARVIS system
        
        Args:
            text_only: Force text-only mode (no voice)
            debug: Enable debug mode
        """
        print("""
        ╔════════════════════════════════════════════╗
        ║  J.A.R.V.I.S. - AI OPERATING SYSTEM      ║
        ║  Initializing...                         ║
        ╚════════════════════════════════════════════╝
        """)
        
        # Validate configuration
        try:
            from config import validate_config
            validate_config()
        except (ValueError, ImportError) as e:
            print(f"❌ Configuration Error: {e}")
            sys.exit(1)
        
        # Initialize components
        logger.info("Initializing JARVIS components...")
        self.brain = JarvisBrain()
        self.listener = VoiceListener() if ENABLE_VOICE and not text_only else None
        self.speaker = VoiceSpeaker() if ENABLE_VOICE else None
        self.text_only = text_only or not ENABLE_VOICE
        self.debug = debug
        
        logger.info("✅ JARVIS initialization complete")
        print("✅ JARVIS is online and ready\n")
    
    def get_input(self, prompt: str = "> ") -> str:
        """Get input from user (voice or text)"""
        try:
            if self.listener and not self.text_only:
                # Try voice input first
                text = self.listener.listen_for_command()
                if text:
                    return text
            
            # Fallback to text input
            print(f"{prompt}", end="", flush=True)
            return input().strip()
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error getting input: {e}")
            print(f"\n{prompt}", end="", flush=True)
            return input().strip()
    
    def listen_for_wake_word(self) -> bool:
        """Wait for wake word to be detected"""
        if self.listener and not self.text_only:
            print(f"\n😴 Sleeping... Say '{WAKE_WORD}' to wake me up\n")
            while True:
                try:
                    if self.listener.listen_for_wake_word():
                        logger.info(f"📢 Wake word detected!")
                        greeting = random.choice(GREETING_RESPONSES)
                        self.speaker.speak(greeting)
                        print(f"🤖 JARVIS: {greeting}\n")
                        return True
                except Exception as e:
                    logger.error(f"Error listening: {e}")
                    continue
        else:
            print(f"\n💤 Ready for input (type '{WAKE_WORD}' or your command):\n")
            return True
    
    def run(self) -> None:
        """Main JARVIS loop"""
        try:
            while True:
                # Wait for wake word
                if not self.listen_for_wake_word():
                    break
                
                # Listen for command with timeout
                start_time = time.time()
                command_received = False
                
                print(f"🎤 Listening for command (timeout in {WAKE_WORD_TIMEOUT}s)...\n")
                
                while time.time() - start_time < WAKE_WORD_TIMEOUT:
                    try:
                        # Get user input
                        user_input = self.get_input()
                        
                        if not user_input:
                            continue
                        
                        command_received = True
                        
                        if self.debug:
                            print(f"🎯 Processing: {user_input}")
                        
                        logger.info(f"User input: {user_input}")
                        
                        # Get response from brain
                        response = self.brain.query(user_input, stream=False)
                        
                        # Output response
                        print(f"\n🤖 JARVIS: {response}\n")
                        if self.speaker:
                            self.speaker.speak(response)
                        
                        # Go back to sleep after command
                        break
                        
                    except KeyboardInterrupt:
                        print("\n\n👋 JARVIS shutting down...")
                        return
                    except Exception as e:
                        logger.error(f"Error processing command: {e}")
                        error_msg = "I encountered an error. Please try again."
                        print(f"\n🤖 JARVIS: {error_msg}\n")
                        if self.speaker:
                            self.speaker.speak(error_msg)
                        break
                
                if not command_received:
                    print("⏱️ Command timeout - returning to sleep mode\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 JARVIS shutting down...")
            sys.exit(0)
        except Exception as e:
            logger.critical(f"Critical error: {e}")
            print(f"❌ Critical error: {e}")
            sys.exit(1)


def main():
    """Main entry point"""
    # Check command line arguments
    text_only = "--text-only" in sys.argv or "--no-voice" in sys.argv
    debug = "--debug" in sys.argv or "-d" in sys.argv
    
    try:
        jarvis = JARVIS(text_only=text_only, debug=debug)
        jarvis.run()
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
