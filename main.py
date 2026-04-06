"""
JARVIS - Advanced AI Assistant
Main entry point for the JARVIS system
"""

import os
import sys
from datetime import datetime
from command_router import CommandRouter
from brain import JarvisBrain
from listener import VoiceListener
from speaker import VoiceSpeaker
from memory import Memory
from tasks import TaskManager
from notes import NotesManager
from web_search import WebSearch
from system_control import SystemController
from clipboard_manager import ClipboardManager
from file_manager import FileManager
from config import DEBUG, VOICE_ENGINE

import time
import threading

class JARVIS:
    """Main JARVIS Assistant Class"""
    
    def __init__(self, use_voice: bool = False):
        print("🤖 Initializing JARVIS...")
        
        # Core components
        self.brain = JarvisBrain()
        self.router = CommandRouter()
        self.memory = Memory()
        self.tasks = TaskManager()
        self.notes = NotesManager()
        self.web = WebSearch()
        self.clipboard = ClipboardManager()
        self.file_manager = FileManager()
        
        # Voice components (optional)
        self.use_voice = use_voice
        if use_voice:
            try:
                self.listener = VoiceListener()
                self.speaker = VoiceSpeaker()
                print("✅ Voice components initialized")
            except Exception as e:
                print(f"⚠️ Voice initialization failed: {e}")
                self.use_voice = False
        
        # Register command handlers
        self._register_handlers()
        
        print("✅ JARVIS initialized successfully!\n")
    
    def _register_handlers(self):
        """Register all command handlers"""
        
        # System control handlers
        self.router.register_handler("open_app", self._handle_open_app)
        self.router.register_handler("close_app", self._handle_close_app)
        self.router.register_handler("system_info", self._handle_system_info)
        self.router.register_handler("control_volume", self._handle_volume)
        self.router.register_handler("shutdown", self._handle_shutdown)
        self.router.register_handler("restart", self._handle_restart)
        self.router.register_handler("list_apps", self._handle_list_apps)
        
        # Task handlers
        self.router.register_handler("set_timer", self._handle_set_timer)
        self.router.register_handler("set_alarm", self._handle_set_alarm)
        self.router.register_handler("list_timers", self._handle_list_timers)
        self.router.register_handler("list_alarms", self._handle_list_alarms)
        
        # Notes handlers
        self.router.register_handler("add_note", self._handle_add_note)
        self.router.register_handler("read_note", self._handle_read_note)
        self.router.register_handler("list_notes", self._handle_list_notes)
        self.router.register_handler("search_notes", self._handle_search_notes)
        
        # Web handlers
        self.router.register_handler("search_web", self._handle_web_search)
        self.router.register_handler("get_weather", self._handle_weather)
        self.router.register_handler("get_news", self._handle_news)
        
        # Clipboard handlers
        self.router.register_handler("copy_to_clipboard", self._handle_copy_clip)
        self.router.register_handler("get_clipboard", self._handle_get_clip)
        self.router.register_handler("clipboard_history", self._handle_clip_history)
        
        # File handlers
        self.router.register_handler("list_files", self._handle_list_files)
        self.router.register_handler("search_files", self._handle_search_files)
        self.router.register_handler("open_file", self._handle_open_file)
        self.router.register_handler("open_folder", self._handle_open_folder)
    
    # ============================================
    # SYSTEM CONTROL HANDLERS
    # ============================================
    
    def _handle_open_app(self, params, intent_data):
        app_name = params.get("app_name", "")
        if not app_name:
            return "❌ Please specify an app name"
        return SystemController.open_app(app_name)
    
    def _handle_close_app(self, params, intent_data):
        app_name = params.get("app_name", "")
        if not app_name:
            return "❌ Please specify an app name"
        return SystemController.close_app(app_name)
    
    def _handle_system_info(self, params, intent_data):
        return SystemController.get_system_info()
    
    def _handle_volume(self, params, intent_data):
        action = params.get("action", "increase")
        amount = params.get("amount", 5)
        return SystemController.control_volume(action, amount)
    
    def _handle_shutdown(self, params, intent_data):
        timeout = params.get("timeout", 60)
        return SystemController.shutdown(timeout)
    
    def _handle_restart(self, params, intent_data):
        timeout = params.get("timeout", 60)
        return SystemController.restart(timeout)
    
    def _handle_list_apps(self, params, intent_data):
        return SystemController.list_running_apps()
    
    # ============================================
    # TASK HANDLERS
    # ============================================
    
    def _handle_set_timer(self, params, intent_data):
        duration = params.get("duration", 300)  # Default 5 minutes
        name = params.get("name", "Timer")
        self.tasks.create_timer(duration, name)
        return f"⏱️ Timer set for {duration} seconds"
    
    def _handle_set_alarm(self, params, intent_data):
        time_str = params.get("time", "")
        name = params.get("name", "Alarm")
        if not time_str:
            return "❌ Please specify a time (HH:MM)"
        return self.tasks.create_alarm(time_str, name)
    
    def _handle_list_timers(self, params, intent_data):
        return self.tasks.list_timers()
    
    def _handle_list_alarms(self, params, intent_data):
        return self.tasks.list_alarms()
    
    # ============================================
    # NOTES HANDLERS
    # ============================================
    
    def _handle_add_note(self, params, intent_data):
        title = params.get("title", "Note")
        content = params.get("content", "")
        tags = params.get("tags", [])
        
        if not content:
            return "❌ Please provide note content"
        
        note_id = self.notes.create_note(title, content, tags)
        return f"✅ Note created (ID: {note_id})"
    
    def _handle_read_note(self, params, intent_data):
        note_id = params.get("note_id", "")
        
        if not note_id:
            # List notes if no specific ID
            return self.notes.list_notes()
        
        return self.notes.view_note(note_id)
    
    def _handle_list_notes(self, params, intent_data):
        tag = params.get("tag", None)
        return self.notes.list_notes(tag)
    
    def _handle_search_notes(self, params, intent_data):
        query = params.get("query", "")
        if not query:
            return "❌ Please provide a search query"
        return self.notes.search_notes(query)
    
    # ============================================
    # WEB HANDLERS
    # ============================================
    
    def _handle_web_search(self, params, intent_data):
        query = params.get("query", "")
        if not query:
            return "❌ Please provide a search query"
        
        results = self.web.search(query)
        return self.web.format_search_results(results)
    
    def _handle_weather(self, params, intent_data):
        location = params.get("location", "current")
        return self.web.get_weather(location)
    
    def _handle_news(self, params, intent_data):
        topic = params.get("topic", "general")
        return self.web.get_news_briefing(topic)
    
    # ============================================
    # CLIPBOARD HANDLERS
    # ============================================
    
    def _handle_copy_clip(self, params, intent_data):
        text = params.get("text", "")
        if not text:
            return "❌ No text to copy"
        
        success = self.clipboard.set_clipboard(text)
        return "✅ Copied to clipboard" if success else "❌ Failed to copy"
    
    def _handle_get_clip(self, params, intent_data):
        content = self.clipboard.get_clipboard()
        return content if content else "❌ Clipboard is empty"
    
    def _handle_clip_history(self, params, intent_data):
        limit = params.get("limit", 10)
        return self.clipboard.get_history(limit)
    
    # ============================================
    # FILE HANDLERS
    # ============================================
    
    def _handle_list_files(self, params, intent_data):
        path = params.get("path", None)
        return FileManager.list_files(path)
    
    def _handle_search_files(self, params, intent_data):
        query = params.get("query", "")
        path = params.get("path", None)
        
        if not query:
            return "❌ Please provide a search query"
        
        return FileManager.search_files(query, path)
    
    def _handle_open_file(self, params, intent_data):
        path = params.get("path", "")
        if not path:
            return "❌ Please provide a file path"
        return FileManager.open_file(path)
    
    def _handle_open_folder(self, params, intent_data):
        path = params.get("path", "")
        if not path:
            return "❌ Please provide a folder path"
        return FileManager.open_folder(path)
    
    # ============================================
    # MAIN INTERFACE METHODS
    # ============================================
    
    def process_text_input(self, user_input: str) -> str:
        """
        Process text input and return response
        
        Args:
            user_input: User's text input
            
        Returns:
            JARVIS response
        """
        print(f"\n👤 You: {user_input}")
        
        # Store in memory
        self.memory.add_command_to_history(user_input)
        
        # Route to handler or conversational AI
        response = self.router.route_command(user_input)
        
        print(f"\n🤖 JARVIS: {response}\n")
        
        return response
    
    def process_voice_input(self) -> str:
        """Process voice input"""
        if not self.use_voice:
            return "❌ Voice not enabled"
        
        command = self.listener.listen_for_command()
        
        if command:
            return self.process_text_input(command)
        else:
            return "❌ Could not understand voice input"
    
    def interactive_mode(self, voice_enabled: bool = False):
        """
        Interactive conversation mode
        
        Args:
            voice_enabled: Whether to use voice input
        """
        print("🎯 JARVIS Interactive Mode")
        print("=" * 50)
        print("Commands: 'help', 'quit', 'memory', 'history'\n")
        
        while True:
            try:
                if voice_enabled and self.use_voice:
                    print("🎤 Listening for wake word...")
                    
                    # Check for wake word
                    if self.listener.listen_for_wake_word():
                        self.speaker.speak("Yes, I'm listening")
                        response = self.process_voice_input()
                        
                        if self.use_voice and response:
                            self.speaker.speak(response)
                else:
                    user_input = input("\n📝 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() == "quit":
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == "help":
                        self._print_help()
                        continue
                    elif user_input.lower() == "memory":
                        print(self.memory.export_memory())
                        continue
                    elif user_input.lower() == "history":
                        print("\n📜 Command History:")
                        for cmd in self.memory.get_command_history():
                            print(f"  • {cmd}")
                        continue
                    
                    self.process_text_input(user_input)
            
            except KeyboardInterrupt:
                print("\n\n👋 JARVIS shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _print_help(self):
        """Print help information"""
        help_text = """
🎯 JARVIS Command Examples:
================================

🖥️  SYSTEM CONTROL:
  • "Open Chrome"
  • "Close Firefox"
  • "System info"
  • "Control volume increase 10"
  • "List running apps"
  • "Shutdown in 60 seconds"

⏰ TASKS:
  • "Set timer for 5 minutes"
  • "Set alarm for 14:30"
  • "List timers"
  • "List alarms"

📝 NOTES:
  • "Add note titled 'Ideas' with content 'Machine learning projects'"
  • "List notes"
  • "Search notes for 'python'"
  • "Read note"

🌐 WEB:
  • "Search web for python tutorials"
  • "What's the weather in New York"
  • "Tell me today's news"

📋 CLIPBOARD:
  • "Copy to clipboard: Hello World"
  • "Get clipboard"
  • "Clipboard history"

📂 FILES:
  • "List files in documents"
  • "Search files for pdf"
  • "Open file /path/to/file"
  • "Open folder ~/Downloads"

💬 GENERAL:
  • "quit" - Exit JARVIS
  • "help" - Show this help
  • "memory" - View memory data
  • "history" - Show command history
        """
        print(help_text)


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  🤖  JARVIS - Advanced AI Assistant                      ║
║                                                           ║
║  Powered by Groq API & Advanced NLP                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Ask user preferences
    print("\n⚙️ Configuration:")
    use_voice = input("Enable voice input/output? (y/n): ").lower() == 'y'
    
    # Initialize JARVIS
    jarvis = JARVIS(use_voice=use_voice)
    
    # Start interactive mode
    jarvis.interactive_mode(voice_enabled=use_voice)


if __name__ == "__main__":
    main()
