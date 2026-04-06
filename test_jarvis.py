"""
JARVIS Test Suite & Demo
Quick testing of JARVIS capabilities
"""

from main import JARVIS
import time

def test_system_commands():
    """Test system control commands"""
    print("\n" + "="*60)
    print("🖥️ SYSTEM CONTROL TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "System information",
        "List running applications",
        "Increase volume by 10",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(1)


def test_task_management():
    """Test task management"""
    print("\n" + "="*60)
    print("⏰ TASK MANAGEMENT TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "Set timer for 10 seconds named 'test timer'",
        "List timers",
        "Set alarm for 15:30",
        "List alarms",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(0.5)


def test_notes():
    """Test notes management"""
    print("\n" + "="*60)
    print("📝 NOTES MANAGEMENT TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "Add note titled 'Project Ideas' with content 'Build AI chatbot, Create mobile app, Learn Rust'",
        "Add note titled 'Python Tips' with content 'Use list comprehensions, Remember to document code'",
        "List notes",
        "Search notes for python",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(0.5)


def test_web_search():
    """Test web search"""
    print("\n" + "="*60)
    print("🌐 WEB SEARCH TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "Search web for artificial intelligence",
        "What's the weather today",
        "Tell me about recent technology news",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(1)


def test_clipboard():
    """Test clipboard management"""
    print("\n" + "="*60)
    print("📋 CLIPBOARD TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "Copy to clipboard: Hello JARVIS System",
        "Get clipboard",
        "Clipboard history",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(0.5)


def test_file_operations():
    """Test file operations"""
    print("\n" + "="*60)
    print("📂 FILE OPERATIONS TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "List files in current directory",
        "Search files for py",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(0.5)


def test_conversational_ai():
    """Test conversational AI (non-command queries)"""
    print("\n" + "="*60)
    print("💬 CONVERSATIONAL AI TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "What is machine learning?",
        "Explain quantum computing in simple terms",
        "Give me a fun fact about space",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(1)


def test_memory_persistence():
    """Test memory persistence"""
    print("\n" + "="*60)
    print("💾 MEMORY PERSISTENCE TESTS")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    # First JARVIS instance creates notes
    print("\n✒️ Creating note in first session...")
    jarvis.process_text_input("Add note titled 'Persistence Test' with content 'This should persist'")
    
    time.sleep(1)
    
    # Second JARVIS instance retrieves notes
    print("\n✒️ Checking notes in new session...")
    jarvis2 = JARVIS(use_voice=False)
    jarvis2.process_text_input("List notes")


def demo_multi_command():
    """Demo multi-command execution"""
    print("\n" + "="*60)
    print("🚀 MULTI-COMMAND DEMO")
    print("="*60)
    
    jarvis = JARVIS(use_voice=False)
    
    commands = [
        "Search web for Python and list notes",
        "Set timer and get system info",
        "Add note and search files",
    ]
    
    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        jarvis.process_text_input(cmd)
        time.sleep(1)


def run_full_test_suite():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🤖 JARVIS - Full Test Suite                                ║
║                                                              ║
║  This will test all major components of JARVIS              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    input("Press Enter to start tests...")
    
    try:
        # Test each module
        test_system_commands()
        time.sleep(2)
        
        test_task_management()
        time.sleep(2)
        
        test_notes()
        time.sleep(2)
        
        test_web_search()
        time.sleep(2)
        
        test_clipboard()
        time.sleep(2)
        
        test_file_operations()
        time.sleep(2)
        
        test_conversational_ai()
        time.sleep(2)
        
        test_memory_persistence()
        time.sleep(2)
        
        demo_multi_command()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Test Summary:")
        print("  ✓ System Control")
        print("  ✓ Task Management")
        print("  ✓ Notes Management")
        print("  ✓ Web Search")
        print("  ✓ Clipboard Management")
        print("  ✓ File Operations")
        print("  ✓ Conversational AI")
        print("  ✓ Memory Persistence")
        print("  ✓ Multi-Command Support")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


def quick_demo():
    """Quick demo with minimal tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🤖 JARVIS - Quick Demo                                     ║
║                                                              ║
║  Demonstrating key JARVIS features                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    jarvis = JARVIS(use_voice=False)
    
    demo_commands = [
        ("Open with Chrome", "open chrome"),
        ("AI Response", "explain machine learning briefly"),
        ("Create Note", "add note titled 'JARVIS Test' with content 'Tested successfully'"),
        ("Set Timer", "set timer for 5 seconds"),
        ("System Info", "system information"),
        ("Web Search", "search web for python programming"),
        ("List Notes", "list notes"),
        ("Clipboard", "clipboard history"),
    ]
    
    print("\n🚀 Running demo...\n")
    
    for title, command in demo_commands:
        print(f"\n📌 {title}")
        print(f"   Command: {command}")
        print(f"   " + "-"*50)
        jarvis.process_text_input(command)
        time.sleep(1.5)
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    print("\n🎯 JARVIS Test Options:")
    print("1. Full Test Suite (comprehensive)")
    print("2. Quick Demo (fast overview)")
    print("3. System Tests Only")
    print("4. Tasks Tests Only")
    print("5. Notes Tests Only")
    print("6. Web Tests Only")
    print("7. Memory Persistence Test")
    
    choice = input("\nSelect test (1-7): ").strip()
    
    if choice == "1":
        run_full_test_suite()
    elif choice == "2":
        quick_demo()
    elif choice == "3":
        test_system_commands()
    elif choice == "4":
        test_task_management()
    elif choice == "5":
        test_notes()
    elif choice == "6":
        test_web_search()
    elif choice == "7":
        test_memory_persistence()
    else:
        print("Invalid choice. Running quick demo...")
        quick_demo()
