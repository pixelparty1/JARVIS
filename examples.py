"""
JARVIS Advanced Usage Examples
Programmatic usage of JARVIS components
"""

from main import JARVIS
from brain import JarvisBrain
from memory import Memory
from notes import NotesManager
from tasks import TaskManager
from system_control import SystemController
from file_manager import FileManager
import time

def example_1_basic_chat():
    """Example 1: Basic conversational chat"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Conversational Chat")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    questions = [
        "What is artificial intelligence?",
        "Tell me about machine learning",
        "What's the future of AI?",
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        response = jarvis.process_text_input(question)
        print(f"A: {response}")
        time.sleep(1)


def example_2_task_automation():
    """Example 2: Automated task scheduling"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Task Automation")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    # Schedule multiple tasks
    print("\n📅 Scheduling tasks...")
    jarvis.process_text_input("Set timer for 3 seconds named 'task1'")
    time.sleep(0.5)
    jarvis.process_text_input("Set timer for 5 seconds named 'task2'")
    time.sleep(0.5)
    
    print("\n⏰ Active timers:")
    jarvis.process_text_input("List timers")
    
    # Wait for timers to complete
    print("\n⏳ Waiting for tasks to complete...")
    time.sleep(6)
    
    print("\n✅ Tasks completed!")


def example_3_memory_notes_integration():
    """Example 3: Memory and notes integration"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Memory & Notes Integration")
    print("="*60)
    
    memory = Memory()
    notes = NotesManager()
    
    # Add user preferences
    print("\n📝 Setting user preferences...")
    memory.set_preference("favorite_language", "Python")
    memory.set_preference("work_time", "9-5")
    memory.set_preference("timezone", "UTC")
    
    # Create notes
    print("\n📓 Creating notes...")
    notes.create_note(
        title="Python Best Practices",
        content="Use type hints, write docstrings, follow PEP 8",
        tags=["python", "coding"]
    )
    
    notes.create_note(
        title="Project Ideas",
        content="Build chatbot, create CLI tool, write library",
        tags=["ideas", "projects"]
    )
    
    # Retrieve and display
    print("\n🔍 Retrieving data...")
    prefs = memory.get_all_preferences()
    print(f"Preferences: {prefs}")
    
    print(f"\nAll notes: {notes.list_notes()}")
    print(f"\nNotes tagged 'python': {notes.list_notes(tag='python')}")


def example_4_system_control():
    """Example 4: System control operations"""
    print("\n" + "="*60)
    print("EXAMPLE 4: System Control")
    print("="*60)
    
    print("\n🖥️ Getting system information...")
    info = SystemController.get_system_info()
    print(info)
    
    print("\n📂 Listing running applications...")
    apps = SystemController.list_running_apps()
    print(apps)
    
    print("\n🔊 Volume control simulation...")
    print(SystemController.control_volume("increase", 5))


def example_5_file_operations():
    """Example 5: File operations"""
    print("\n" + "="*60)
    print("EXAMPLE 5: File Operations")
    print("="*60)
    
    print("\n📂 Current directory contents:")
    print(FileManager.list_files())
    
    print("\n🔍 Searching for Python files...")
    print(FileManager.search_files("*.py"))
    
    print("\n📋 File information:")
    import __file__ as f
    try:
        print(FileManager.get_file_info(__file__))
    except:
        print("Couldn't get file info for this script")


def example_6_direct_brain_usage():
    """Example 6: Using brain directly for custom tasks"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Direct Brain (Groq API) Usage")
    print("="*60)
    
    brain = JarvisBrain()
    
    # Regular query
    print("\n💭 Regular query:")
    response = brain.query("Write a haiku about AI")
    print(response)
    
    # Intent parsing
    print("\n\n🎯 Intent parsing:")
    intent = brain.parse_intent("Open Spotify and play music loudly")
    print(f"Parsed Intent: {intent['intent']}")
    print(f"Parameters: {intent['parameters']}")
    print(f"Confidence: {intent['confidence']}")
    
    # Conversation history
    print("\n\n💬 Conversation History:")
    history = brain.get_history()
    print(f"Messages: {len(history)}")
    for msg in history[-2:]:
        print(f"  {msg['role']}: {msg['content'][:100]}...")


def example_7_advanced_intent_parsing():
    """Example 7: Advanced intent parsing for complex commands"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Advanced Intent Parsing")
    print("="*60)
    
    brain = JarvisBrain()
    
    complex_commands = [
        "Open Chrome, Google 'machine learning', and set a 30-minute timer",
        "Create a note about AI, then search the web for recent AI news",
        "Check system info and if CPU is high, close unnecessary apps",
        "Set two alarms - one for morning at 7am and evening at 6pm",
    ]
    
    for cmd in complex_commands:
        print(f"\n🎯 Parsing: {cmd}")
        intent = brain.parse_intent(cmd)
        print(f"   Intent: {intent['intent']}")
        print(f"   Confidence: {intent['confidence']:.2f}")
        print(f"   Parameters: {list(intent['parameters'].keys())}")


def example_8_custom_workflow():
    """Example 8: Building a custom workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Custom Workflow - Daily Briefing")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    print("\n📋 Generating Daily Briefing...")
    
    # Simulate a daily briefing workflow
    print("\n1️⃣ System Status:")
    jarvis.process_text_input("System information")
    
    time.sleep(1)
    
    print("\n2️⃣ Scheduled Tasks:")
    jarvis.process_text_input("List alarms")
    
    time.sleep(1)
    
    print("\n3️⃣ Recent Notes:")
    jarvis.process_text_input("List notes")
    
    time.sleep(1)
    
    print("\n4️⃣ Daily Insight:")
    jarvis.process_text_input("What should I focus on today for productivity?")
    
    print("\n✅ Daily briefing complete!")


def example_9_batch_operations():
    """Example 9: Batch operations"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Batch Operations")
    print("="*60)
    
    memory = Memory()
    notes = NotesManager()
    
    # Batch create notes
    print("\n📝 Creating batch of notes...")
    batch_notes = [
        ("Meeting Notes - Project Alpha", "Discussed timeline and budget", ["meetings", "alpha"]),
        ("Meeting Notes - Project Beta", "Reviewed design mockups", ["meetings", "beta"]),
        ("Research - AI Trends", "GPT models advancing rapidly", ["research", "ai"]),
        ("Research - Web3", "Blockchain becoming mainstream", ["research", "web3"]),
    ]
    
    for title, content, tags in batch_notes:
        notes.create_note(title, content, tags)
        print(f"  ✓ Created: {title}")
    
    # Batch query
    print("\n🔍 Searching batch results...")
    print(f"Meetings: {notes.list_notes(tag='meetings')}")
    print(f"Research: {notes.list_notes(tag='research')}")
    
    # Batch add preferences
    print("\n⚙️ Setting batch preferences...")
    preferences = {
        "theme": "dark",
        "language": "en",
        "notifications": "enabled",
        "auto_save": "true",
        "debug_mode": "false"
    }
    
    for key, value in preferences.items():
        memory.set_preference(key, value)
        print(f"  ✓ {key} = {value}")


def example_10_context_aware_responses():
    """Example 10: Context-aware responses using memory"""
    print("\n" + "="*60)
    print("EXAMPLE 10: Context-Aware Responses")
    print("="*60)
    
    brain = JarvisBrain()
    memory = Memory()
    
    # Set context in memory
    memory.set_preference("name", "John")
    memory.set_preference("role", "Software Engineer")
    memory.set_preference("interested_in", "AI and Machine Learning")
    
    # First interaction
    print("\n1️⃣ First interaction:")
    response = brain.query("Hi, I'd like to learn more about AI")
    print(f"Response: {response}")
    
    # Follow-up (uses conversation history)
    print("\n2️⃣ Follow-up (uses context):")
    response = brain.query("What should I study first?")
    print(f"Response: {response}")
    
    # Another follow-up
    print("\n3️⃣ Another follow-up:")
    response = brain.query("How long will it take?")
    print(f"Response: {response}")
    
    print("\n📊 Conversation history length:", len(brain.get_history()))


def main_menu():
    """Main menu for examples"""
    print("""
╔═════════════════════════════════════════════════════════════╗
║                                                             ║
║  🤖 JARVIS - Advanced Usage Examples                       ║
║                                                             ║
║  Learn how to use JARVIS programmatically                  ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
    """)
    
    examples = [
        ("Basic Conversational Chat", example_1_basic_chat),
        ("Task Automation", example_2_task_automation),
        ("Memory & Notes Integration", example_3_memory_notes_integration),
        ("System Control", example_4_system_control),
        ("File Operations", example_5_file_operations),
        ("Direct Brain (Groq API) Usage", example_6_direct_brain_usage),
        ("Advanced Intent Parsing", example_7_advanced_intent_parsing),
        ("Custom Workflow - Daily Briefing", example_8_custom_workflow),
        ("Batch Operations", example_9_batch_operations),
        ("Context-Aware Responses", example_10_context_aware_responses),
    ]
    
    print("\n📚 Available Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("11. Run All Examples")
    print("0. Exit")
    
    while True:
        choice = input("\nSelect example (0-11): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "11":
            for name, func in examples:
                try:
                    func()
                    time.sleep(2)
                except Exception as e:
                    print(f"Error running {name}: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            idx = int(choice) - 1
            try:
                examples[idx][1]()
            except Exception as e:
                print(f"Error running example: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main_menu()
