"""
JARVIS Autonomous Agent Examples
Demonstrates the agent system in action
"""

from agent_main import JARVISAgent
from agent_loop import AgentLoop
from tool_registry import ToolRegistry
import time


def example_1_simple_goal():
    """Example 1: Simple goal execution"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Goal Execution")
    print("="*60)
    
    agent = JARVISAgent()
    
    goal = "Get current system information"
    print(f"\n🎯 Goal: {goal}")
    
    success, result = agent.agent.execute_goal(goal)
    print(f"\n✅ Result: {result}")


def example_2_multi_step_task():
    """Example 2: Multi-step task with planning"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multi-Step Task Planning")
    print("="*60)
    
    agent = JARVISAgent()
    
    goal = "Search for artificial intelligence news and summarize the findings"
    print(f"\n🎯 Goal: {goal}")
    print("\nAgent will break this into steps: search → extract → summarize\n")
    
    success, result = agent.agent.execute_goal(goal)
    print(f"\n✅ Result: {result}")


def example_3_context_aware_execution():
    """Example 3: Context-aware task execution"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Context-Aware Task Execution")
    print("="*60)
    
    agent = JARVISAgent()
    
    goals = [
        "Search web for Python programming best practices",
        "Summarize the key points",
        "Save summary to a file"
    ]
    
    for i, goal in enumerate(goals, 1):
        print(f"\n{'─'*60}")
        print(f"Step {i}: {goal}")
        print(f"{'─'*60}")
        
        success, result = agent.agent.execute_goal(goal)
        print(f"Result: {result}")
        
        time.sleep(1)


def example_4_goal_with_fallback():
    """Example 4: Goal execution with automatic replanning on failure"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Intelligent Replanning on Failure")
    print("="*60)
    
    agent = JARVISAgent()
    
    goal = "Create a technical document about quantum computing and save it"
    print(f"\n🎯 Goal: {goal}")
    print("🔄 If any step fails, agent will automatically replan...\n")
    
    success, result = agent.agent.execute_goal(goal, context="Focus on beginner-friendly explanation")
    print(f"\n✅ Final Result: {result}")


def example_5_autonomous_mode():
    """Example 5: Autonomous operation mode"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Autonomous Mode (5 minutes)")
    print("="*60)
    
    agent = JARVISAgent()
    
    print("\n🤖 Agent will run autonomously for 5 minutes")
    print("It will suggest and execute tasks based on system state\n")
    
    agent.agent.run_autonomous_mode(duration_minutes=5)


def example_6_tool_discovery():
    """Example 6: Agent discovering and using tools"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Tool Discovery and Usage")
    print("="*60)
    
    agent = JARVISAgent()
    
    tasks = [
        "Find information about machine learning",
        "Save the information",
        "Create a summary note"
    ]
    
    print("\n🔧 Agent has access to these tools:")
    print(agent.agent.tool_registry.list_tools())
    
    for task in tasks:
        print(f"\n📋 Task: {task}")
        
        # Get tool recommendation
        recommendations = agent.agent.get_tool_recommendations(task)
        print(f"🔧 Recommended tools: {recommendations}")


def example_7_agent_memory_learning():
    """Example 7: Agent learning from experience"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Agent Memory and Learning")
    print("="*60)
    
    agent = JARVISAgent()
    
    # Execute some tasks
    tasks = [
        "Get weather information",
        "List available files",
        "Search for Python tips"
    ]
    
    for task in tasks:
        print(f"\n📋 Executing: {task}")
        agent.agent.execute_goal(task)
    
    # Show what agent learned
    print("\n🧠 Agent Memory Insights:")
    print(agent.agent.memory.get_memory_insights())
    
    print("\n📊 Execution Stats:")
    stats = agent.agent.memory.get_execution_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_8_complex_workflow():
    """Example 8: Complex multi-goal workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Complex Workflow Execution")
    print("="*60)
    
    agent = JARVISAgent()
    
    workflow = [
        ("Research Phase", "Search web for latest developments in generative AI"),
        ("Analysis Phase", "Summarize the key developments and trends"),
        ("Storage Phase", "Create a comprehensive note with findings"),
        ("Verification Phase", "List all created notes to verify completion")
    ]
    
    for phase, task in workflow:
        print(f"\n{'─'*60}")
        print(f"🔄 {phase}: {task}")
        print(f"{'─'*60}")
        
        success, result = agent.agent.execute_goal(task)
        print(f"Status: {'✅ Success' if success else '❌ Failed'}")
        print(f"Result: {result[:100]}...")
        
        time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Workflow Completed")
    agent.agent.print_agent_summary()


def example_9_adaptive_planning():
    """Example 9: Adaptive planning based on complexity"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Adaptive Task Planning")
    print("="*60)
    
    agent = JARVISAgent()
    
    # Simple task
    simple_goal = "Get current time"
    complexity_simple = agent.agent.planner.estimate_complexity(simple_goal)
    
    # Complex task
    complex_goal = "Research machine learning, summarize findings, and save to multiple formats"
    complexity_complex = agent.agent.planner.estimate_complexity(complex_goal)
    
    print(f"\nSimple Goal: '{simple_goal}'")
    print(f"Complexity: {complexity_simple}/10")
    print(f"✓ Will use minimal steps\n")
    
    print(f"Complex Goal: '{complex_goal}'")
    print(f"Complexity: {complexity_complex}/10")
    print(f"✓ Agent will create detailed plan with multiple steps\n")


def example_10_failure_recovery():
    """Example 10: Intelligent failure recovery"""
    print("\n" + "="*60)
    print("EXAMPLE 10: Failure Detection and Recovery")
    print("="*60)
    
    agent = JARVISAgent()
    
    # This goal might have challenges
    challenging_goal = "Access and summarize a file, then create multiple copies"
    
    print(f"\n🎯 Challenging Goal: {challenging_goal}")
    print("\nAgent will:")
    print("  1. Plan the steps")
    print("  2. Execute each step")
    print("  3. Observe results")
    print("  4. Detect failures")
    print("  5. Replan automatically\n")
    
    success, result = agent.agent.execute_goal(challenging_goal)
    
    # Show failures analysis
    print("\n📊 Failure Analysis:")
    failures = agent.agent.executor.analyze_failures()
    print(f"  Total failures: {failures['total_failures']}")
    print(f"  Failure rate: {failures['failure_rate']*100:.1f}%")
    
    if failures['recent_failures']:
        print("  Recent failures:")
        for failure in failures['recent_failures'][-3:]:
            print(f"    • {failure['tool']}: {failure['error'][:50]}")


def example_11_tool_statistics():
    """Example 11: Tool usage statistics and optimization"""
    print("\n" + "="*60)
    print("EXAMPLE 11: Tool Usage Statistics")
    print("="*60)
    
    agent = JARVISAgent()
    
    # Use various tools
    goals = [
        "Search web for information",
        "Get system information",
        "Search web again for different info"
    ]
    
    for goal in goals:
        agent.agent.execute_goal(goal)
    
    # Show stats
    print("\n📊 Tool Statistics:")
    stats = agent.agent.tool_registry.get_tool_stats()
    
    print(f"\nTotal Tools: {stats['total_tools']}")
    print(f"Total Calls: {stats['total_calls']}")
    print(f"Total Errors: {stats['total_errors']}")
    
    print("\n🔧 Most Used Tools:")
    for tool in stats['most_used'][:5]:
        print(f"  • {tool['name']}: {tool['calls']} calls")
    
    if stats['most_errors']:
        print("\n⚠️ Tools with Most Errors:")
        for tool in stats['most_errors'][:3]:
            print(f"  • {tool['name']}: {tool['errors']} errors")


def example_12_agent_export_and_analysis():
    """Example 12: Export agent state for analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 12: Agent State Export and Analysis")
    print("="*60)
    
    agent = JARVISAgent()
    
    # Execute some tasks
    print("\nExecuting sample tasks...")
    for goal in ["Get system info", "Search web for information"]:
        agent.agent.execute_goal(goal)
    
    # Export state
    print("\n💾 Exporting agent state...")
    agent.agent.export_agent_state("agent_demo_state.json")
    
    # Show summary
    print("\n📊 Agent State Summary:")
    agent.agent.print_agent_summary()


def run_demo_interactive():
    """Run interactive demo menu"""
    examples = [
        ("Simple Goal Execution", example_1_simple_goal),
        ("Multi-Step Task Planning", example_2_multi_step_task),
        ("Context-Aware Execution", example_3_context_aware_execution),
        ("Intelligent Replanning", example_4_goal_with_fallback),
        ("Autonomous Mode (5 min)", example_5_autonomous_mode),
        ("Tool Discovery", example_6_tool_discovery),
        ("Agent Memory & Learning", example_7_agent_memory_learning),
        ("Complex Workflow", example_8_complex_workflow),
        ("Adaptive Planning", example_9_adaptive_planning),
        ("Failure Recovery", example_10_failure_recovery),
        ("Tool Statistics", example_11_tool_statistics),
        ("Export & Analysis", example_12_agent_export_and_analysis),
    ]
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🎬 JARVIS AGENT EXAMPLES MENU                          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("\n🎯 Available Examples:\n")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i:2}. {name}")
    print("0. Run All Examples")
    print("Q. Quit\n")
    
    while True:
        choice = input("Select example (0-12, Q): ").strip()
        
        if choice.upper() == "Q":
            print("Goodbye!")
            break
        
        elif choice == "0":
            print("\n▶️ Running all examples...\n")
            for name, func in examples:
                try:
                    func()
                    time.sleep(2)
                except KeyboardInterrupt:
                    print("\n⏹️ Stopped")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            try:
                examples[int(choice)-1][1]()
            except KeyboardInterrupt:
                print("\n⏹️ Interrupted")
            except Exception as e:
                print(f"❌ Error running example: {e}")
        
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    run_demo_interactive()
