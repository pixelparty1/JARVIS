"""
JARVIS Launcher - Start the complete AI system with futuristic UI

Starts:
- Orchestrator backend
- PyQt6 UI
- Signal bridge for integration
"""

import asyncio
import sys
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal, QObject

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_os import Orchestrator, InputType, SystemMode
from ui.jarvis_ui import create_app, Status


class OrchestratorWorker(QObject):
    """Worker thread for orchestrator operations"""
    
    task_started = pyqtSignal(str)
    task_completed = pyqtSignal(str, str)  # task_id, result
    status_changed = pyqtSignal(str)  # status
    
    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self.running = True
    
    async def process_input(self, input_type: InputType, text: str):
        """Process user input"""
        try:
            result = await self.orchestrator.process_input(input_type, text)
            self.task_completed.emit("input", str(result))
        except Exception as e:
            self.task_completed.emit("input", f"Error: {str(e)}")
    
    def run_autonomous(self, duration: int = 60):
        """Run in autonomous mode"""
        try:
            asyncio.run(self.orchestrator.run_autonomously(duration))
        except Exception as e:
            print(f"Error: {e}")


class JarvisLauncher:
    """Main launcher for JARVIS system"""
    
    def __init__(self):
        self.orchestrator = None
        self.app = None
        self.window = None
    
    async def initialize_orchestrator(self):
        """Initialize JARVIS orchestrator"""
        print("🧠 Initializing JARVIS Orchestrator...")
        self.orchestrator = Orchestrator()
        success = await self.orchestrator.initialize()
        
        if success:
            print("✅ Orchestrator initialized")
            
            # Set interactive mode for UI
            self.orchestrator.set_mode(SystemMode.INTERACTIVE)
            
            # Register callbacks
            self._register_callbacks()
            
            return True
        else:
            print("❌ Orchestrator initialization failed")
            return False
    
    def _register_callbacks(self):
        """Register orchestrator callbacks"""
        
        def on_task_started(data):
            if self.window:
                self.window.set_status(Status.EXECUTING)
                self.window.add_log(f"Task started: {data.get('title')}")
        
        def on_task_completed(data):
            if self.window:
                self.window.set_status(Status.IDLE)
                result = data.get('result', 'Completed')
                if result:
                    self.window.add_message(str(result), sender="jarvis")
                self.window.add_log(f"Task completed")
        
        def on_decision_made(data):
            if self.window:
                action = data.get('action', 'Unknown')
                confidence = data.get('confidence', 0)
                self.window.add_log(f"Decision: {action} ({confidence:.0%})")
        
        if self.orchestrator:
            self.orchestrator.register_callback("task_started", on_task_started)
            self.orchestrator.register_callback("task_completed", on_task_completed)
            self.orchestrator.register_callback("decision_made", on_decision_made)
    
    def launch(self):
        """Launch JARVIS system"""
        print("""
        ╔════════════════════════════════════════════╗
        ║  JARVIS AI OPERATING SYSTEM                ║
        ║  Launching Futuristic UI...               ║
        ╚════════════════════════════════════════════╝
        """)
        
        # Initialize orchestrator
        try:
            asyncio.run(self.initialize_orchestrator())
        except Exception as e:
            print(f"❌ Error initializing orchestrator: {e}")
            return False
        
        # Create UI
        print("🎨 Creating user interface...")
        self.app, self.window = create_app(self.orchestrator)
        
        # Setup UI callbacks
        self._setup_ui_callbacks()
        
        print("✅ JARVIS ready!")
        print("💬 Type commands in the chat interface or use voice input")
        print("📊 Monitor tasks, notes, and logs in the side panel")
        
        return True
    
    def _setup_ui_callbacks(self):
        """Setup UI signal callbacks"""
        if self.window:
            # Chat input → Orchestrator
            def on_chat_input(text):
                if self.orchestrator:
                    import threading
                    def run_async():
                        asyncio.run(
                            self.orchestrator.process_input(InputType.TEXT, text)
                        )
                    thread = threading.Thread(target=run_async, daemon=True)
                    thread.start()
            
            self.window.chat_panel.message_submitted.connect(on_chat_input)
    
    def run(self):
        """Run the application"""
        if not self.launch():
            return 1
        
        return self.app.exec()


def main():
    """Main entry point"""
    launcher = JarvisLauncher()
    exit_code = launcher.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
