"""
JARVIS Autonomous Agent Main Entry Point
Integration of agent loop with tool system
"""

import os
import sys
from agent_loop import AgentLoop
from tool_registry import ToolRegistry
from datetime import datetime
from typing import Dict, Any

# Import utility functions from existing modules
from system_control import SystemController
from web_search import WebSearch
from notes import NotesManager
from file_manager import FileManager
from tasks import TaskManager
from clipboard_manager import ClipboardManager
from memory import Memory

class JARVISAgent:
    """JARVIS Autonomous Agent with integrated tools"""
    
    def __init__(self):
        print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  🤖  JARVIS - Autonomous Agent System                   ║
║                                                           ║
║  Powered by Groq API & Autonomous Loop                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        self.agent = AgentLoop()
        self.setup_tools()
    
    def setup_tools(self):
        """Register all available tools with the agent"""
        print("\n🔧 Setting up tool registry...\n")
        
        # ============================================
        # SYSTEM TOOLS
        # ============================================
        
        self.agent.register_tool(
            name="open_app",
            func=lambda app_name: SystemController.open_app(app_name),
            description="Open an application by name",
            parameters={"app_name": "string"},
            required=["app_name"],
            returns="Status message",
            category="system"
        )
        
        self.agent.register_tool(
            name="close_app",
            func=lambda app_name: SystemController.close_app(app_name),
            description="Close an application",
            parameters={"app_name": "string"},
            required=["app_name"],
            returns="Status message",
            category="system"
        )
        
        self.agent.register_tool(
            name="system_info",
            func=lambda: SystemController.get_system_info(),
            description="Get system information",
            parameters={},
            required=[],
            returns="System info report",
            category="system"
        )
        
        self.agent.register_tool(
            name="control_volume",
            func=lambda action, amount=5: SystemController.control_volume(action, amount),
            description="Control system volume",
            parameters={"action": "string", "amount": "integer"},
            required=["action"],
            returns="Status message",
            category="system"
        )
        
        # ============================================
        # WEB TOOLS
        # ============================================
        
        web = WebSearch()
        
        self.agent.register_tool(
            name="search_web",
            func=lambda query: web.search(query),
            description="Search the web for information",
            parameters={"query": "string"},
            required=["query"],
            returns="List of search results",
            category="web"
        )
        
        self.agent.register_tool(
            name="get_weather",
            func=lambda location="current": web.get_weather(location),
            description="Get weather information",
            parameters={"location": "string"},
            required=[],
            returns="Weather description",
            category="web"
        )
        
        self.agent.register_tool(
            name="get_news",
            func=lambda topic="general": web.get_news_briefing(topic),
            description="Get news briefing on a topic",
            parameters={"topic": "string"},
            required=[],
            returns="News summary",
            category="web"
        )
        
        # ============================================
        # FILE TOOLS
        # ============================================
        
        self.agent.register_tool(
            name="list_files",
            func=lambda path=None: FileManager.list_files(path),
            description="List files in a directory",
            parameters={"path": "string"},
            required=[],
            returns="File listing",
            category="file"
        )
        
        self.agent.register_tool(
            name="search_files",
            func=lambda query, path=None: FileManager.search_files(query, path),
            description="Search for files",
            parameters={"query": "string", "path": "string"},
            required=["query"],
            returns="Search results",
            category="file"
        )
        
        self.agent.register_tool(
            name="write_file",
            func=lambda path, content: self._write_file(path, content),
            description="Write content to a file",
            parameters={"path": "string", "content": "string"},
            required=["path", "content"],
            returns="Success status",
            category="file"
        )
        
        self.agent.register_tool(
            name="read_file",
            func=lambda path: self._read_file(path),
            description="Read content from a file",
            parameters={"path": "string"},
            required=["path"],
            returns="File content",
            category="file"
        )
        
        # ============================================
        # NOTES TOOLS
        # ============================================
        
        notes = NotesManager()
        
        self.agent.register_tool(
            name="create_note",
            func=lambda title, content, tags=[]: notes.create_note(title, content, tags),
            description="Create a note",
            parameters={"title": "string", "content": "string", "tags": "list"},
            required=["title", "content"],
            returns="Note ID",
            category="note"
        )
        
        self.agent.register_tool(
            name="search_notes",
            func=lambda query: notes.search_notes(query),
            description="Search notes",
            parameters={"query": "string"},
            required=["query"],
            returns="Search results",
            category="note"
        )
        
        self.agent.register_tool(
            name="list_notes",
            func=lambda tag=None: notes.list_notes(tag),
            description="List all notes",
            parameters={"tag": "string"},
            required=[],
            returns="Notes list",
            category="note"
        )
        
        # ============================================
        # TASK TOOLS
        # ============================================
        
        tasks = TaskManager()
        
        self.agent.register_tool(
            name="set_timer",
            func=lambda duration, name="Timer": f"Timer set for {duration}s",
            description="Set a timer",
            parameters={"duration": "integer", "name": "string"},
            required=["duration"],
            returns="Timer confirmation",
            category="task"
        )
        
        self.agent.register_tool(
            name="set_alarm",
            func=lambda time_str, name="Alarm": f"Alarm set for {time_str}",
            description="Set an alarm",
            parameters={"time_str": "string", "name": "string"},
            required=["time_str"],
            returns="Alarm confirmation",
            category="task"
        )
        
        # ============================================
        # CLIPBOARD TOOLS
        # ============================================
        
        clipboard = ClipboardManager()
        
        self.agent.register_tool(
            name="copy_to_clipboard",
            func=lambda text: clipboard.set_clipboard(text),
            description="Copy text to clipboard",
            parameters={"text": "string"},
            required=["text"],
            returns="Success status",
            category="utility"
        )
        
        self.agent.register_tool(
            name="get_clipboard",
            func=lambda: clipboard.get_clipboard(),
            description="Get clipboard content",
            parameters={},
            required=[],
            returns="Clipboard content",
            category="utility"
        )
        
        # ============================================
        # SUMMARIZATION TOOLS
        # ============================================
        
        self.agent.register_tool(
            name="summarize_text",
            func=lambda text: self._summarize_text(text),
            description="Summarize text content",
            parameters={"text": "string"},
            required=["text"],
            returns="Summary",
            category="utility"
        )
        
        print(f"✅ Registered {len(self.agent.tool_registry.tools)} tools\n")
    
    def _write_file(self, path: str, content: str) -> str:
        """Helper to write file safely"""
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return f"✅ File written: {path}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def _read_file(self, path: str) -> str:
        """Helper to read file safely"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"❌ Error: {e}"
    
    def _summarize_text(self, text: str) -> str:
        """Helper to summarize text"""
        from brain import JarvisBrain
        brain = JarvisBrain()
        prompt = f"Summarize this text in 2-3 sentences:\n\n{text[:1000]}"
        return brain.query(prompt)
    
    def run_interactive(self):
        """Run interactive agent mode"""
        print("\n🤖 JARVIS Autonomous Agent - Interactive Mode")
        print("="*60)
        print("Commands:")
        print("  'goal: <goal>' - Execute a goal")
        print("  'plan: <goal>' - View plan without executing")
        print("  'status' - Show agent status")
        print("  'tools' - List available tools")
        print("  'history' - Show completed goals")
        print("  'auto <minutes>' - Run autonomous mode")
        print("  'quit' - Exit\n")
        
        while True:
            try:
                user_input = input("\n🤖 JARVIS > ").strip()
                
                if user_input.lower() == "quit":
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == "status":
                    print(self.agent.get_system_status())
                
                elif user_input.lower() == "tools":
                    print(self.agent.tool_registry.list_tools())
                
                elif user_input.lower() == "history":
                    print(f"\n✅ Completed Goals ({len(self.agent.completed_goals)}):")
                    for goal in self.agent.completed_goals:
                        print(f"  • {goal}")
                    
                    if self.agent.failed_goals:
                        print(f"\n❌ Failed Goals ({len(self.agent.failed_goals)}):")
                        for goal in self.agent.failed_goals:
                            print(f"  • {goal}")
                
                elif user_input.lower().startswith("goal:"):
                    goal = user_input[5:].strip()
                    success, output = self.agent.execute_goal(goal)
                    print(f"\n{'='*60}")
                    print(f"Result: {output}")
                
                elif user_input.lower().startswith("plan:"):
                    goal = user_input[5:].strip()
                    plan = self.agent.planner.plan(goal)
                
                elif user_input.lower().startswith("auto"):
                    parts = user_input.split()
                    duration = int(parts[1]) if len(parts) > 1 else 5
                    self.agent.run_autonomous_mode(duration)
                
                else:
                    print("Unknown command. Type your goal as 'goal: <your goal>'")
            
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_menu(self):
        """Show main menu"""
        print("""
🎯 JARVIS AUTONOMOUS AGENT MENU
================================
1. Run Interactive Mode
2. Execute Single Goal
3. View Agent Status
4. List Available Tools
5. Run Autonomous Mode
6. Planning Demo
7. Exit

Select option (1-7): """)


def demo_autonomous_task():
    """Demonstration of autonomous task execution"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🎬 AUTONOMOUS TASK DEMO                                 ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    agent = JARVISAgent()
    
    demo_tasks = [
        "Search for latest AI news and create a summary note",
        "Get system information and save it to a file",
        "Search web for Python documentation and summarize",
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n{'='*60}")
        print(f"DEMO TASK {i}: {task}")
        print(f"{'='*60}")
        
        success, output = agent.agent.execute_goal(task)
        print(f"\nTask Result: {output}")
        
        input("\n[Press Enter to continue to next task...]")


def main():
    """Main entry point"""
    agent = JARVISAgent()
    
    while True:
        print("""
╔═══════════════════════════════════════════════════════════╗
║  🤖 JARVIS AUTONOMOUS AGENT SYSTEM                       ║
╚═══════════════════════════════════════════════════════════╝

1. Interactive Mode (execute goals via commands)
2. Single Goal (execute one goal and exit)
3. Agent Status (view current status)
4. Available Tools (list all agent tools)
5. Autonomous Mode (run continuously)
6. View Memory  (see learned patterns)
7. Demo (run demo tasks)
8. Exit

Select option (1-8): """)
        
        choice = input().strip()
        
        if choice == "1":
            agent.run_interactive()
        
        elif choice == "2":
            goal = input("\n📝 Enter goal: ").strip()
            if goal:
                success, output = agent.agent.execute_goal(goal)
                print(f"\n{'='*60}")
                print(f"Result: {output}")
                print(f"{'='*60}")
        
        elif choice == "3":
            print(agent.agent.get_system_status())
        
        elif choice == "4":
            print(agent.agent.tool_registry.list_tools())
        
        elif choice == "5":
            minutes = input("Duration in minutes (default 10): ").strip()
            try:
                duration = int(minutes) if minutes else 10
                agent.agent.run_autonomous_mode(duration)
            except ValueError:
                print("Invalid time")
        
        elif choice == "6":
            print(agent.agent.memory.get_memory_insights())
        
        elif choice == "7":
            demo_autonomous_task()
        
        elif choice == "8":
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
