"""
JARVIS AI OS - Main Entry Point

This is the startup file for the complete AI Operating System.

Usage:
    python main.py                    # Start interactive mode
    python main.py --autonomous       # Start autonomous mode
    python main.py --demo             # Run demo
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_os import (
    Orchestrator, SystemMode, InputType, Task, AgentType,
    create_research_workflow, create_coding_workflow
)


async def main_interactive():
    """Run JARVIS in interactive mode"""
    
    print("""
    ╔════════════════════════════════════════════╗
    ║  JARVIS AI OPERATING SYSTEM v5.0          ║
    ║  Full AI Intelligence Platform            ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Set interactive mode
    orchestrator.set_mode(SystemMode.INTERACTIVE)
    
    print("\n💬 Interactive Mode - Type commands (type 'help' for commands)")
    print("─" * 50)
    
    try:
        while True:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                break
            
            elif user_input.lower() == "help":
                print("""
Commands:
  help              - Show this help
  status            - Show system status
  autonomous        - Switch to autonomous mode
  task <task>       - Add a task
  workflow <type>   - Run a workflow (research, coding, communication)
  exit              - Exit JARVIS
                """)
            
            elif user_input.lower() == "status":
                status = orchestrator.get_status()
                print(f"\n🤖 JARVIS Status:")
                print(f"  Mode: {status['mode']}")
                print(f"  Running: {status['is_running']}")
                print(f"  Uptime: {status['uptime_seconds']:.1f}s")
                print(f"  Tasks processed: {status['tasks_processed']}")
                print(f"  Pending tasks: {status['pending_tasks']}")
                print(f"  CPU: {status['system']['cpu_usage']:.1f}%")
                print(f"  Memory: {status['system']['memory_usage']:.1f}%")
            
            elif user_input.lower() == "autonomous":
                orchestrator.set_mode(SystemMode.AUTONOMOUS)
                print("🤖 Switched to AUTONOMOUS mode")
                # Run for 30 seconds then return
                await orchestrator.run_autonomously(duration_seconds=30)
                print("Returned to INTERACTIVE mode")
            
            elif user_input.lower().startswith("task "):
                task_desc = user_input[5:]
                await orchestrator.process_input(InputType.TEXT, task_desc)
            
            elif user_input.lower().startswith("workflow "):
                workflow_type = user_input[9:].lower()
                
                if workflow_type == "research":
                    workflow = create_research_workflow()
                elif workflow_type == "coding":
                    workflow = create_coding_workflow()
                else:
                    print(f"Unknown workflow: {workflow_type}")
                    continue
                
                result = await orchestrator.execute_workflow(workflow)
                print(f"Workflow result: {result}")
            
            else:
                # Treat as general input
                await orchestrator.process_input(InputType.TEXT, user_input)
    
    finally:
        await orchestrator.shutdown()


async def main_autonomous(duration: int = 300):
    """Run JARVIS in autonomous mode"""
    
    print("""
    ╔════════════════════════════════════════════╗
    ║  JARVIS - AUTONOMOUS MODE                 ║
    ║  AI Acts Without User Interaction         ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Initialize
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Set callbacks to show what JARVIS is doing
    orchestrator.register_callback("task_started", lambda data: print(
        f"🚀 Task started: {data.get('title', 'Unknown')}"
    ))
    
    orchestrator.register_callback("task_completed", lambda data: print(
        f"✅ Task completed: {data.get('task_id', 'Unknown')[:8]}"
    ))
    
    orchestrator.register_callback("decision_made", lambda data: print(
        f"🤔 Decision: {data['action']} (Confidence: {data['confidence']:.0%})"
    ))
    
    # Run autonomously
    await orchestrator.run_autonomously(duration_seconds=duration)
    
    # Show final status
    status = orchestrator.get_status()
    print("\n" + "="*50)
    print("Autonomous Session Complete")
    print(f"  Tasks processed: {status['tasks_processed']}")
    print(f"  Decisions made: {status['tasks_processed']}")  # Approx
    print("="*50)
    
    await orchestrator.shutdown()


async def run_demo():
    """Run demonstration of JARVIS capabilities"""
    
    print("""
    ╔════════════════════════════════════════════╗
    ║  JARVIS - DEMONSTRATION                   ║
    ║  Showcasing AI OS Capabilities            ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Initialize
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    print("\n📊 System Status:")
    status = orchestrator.get_status()
    print(f"  Agents registered: {status['agents']['total_agents']}")
    print(f"  Avg agent success rate: {status['agents']['average_success_rate']:.1%}")
    
    print("\n🔄 Running Demo Workflow: Research Project")
    print("  Step 1: Research quantum computing")
    await orchestrator.process_input(
        InputType.TEXT,
        "Research quantum computing and provide insights"
    )
    
    print("\n  Step 2: Run full research workflow")
    workflow = create_research_workflow()
    result = await orchestrator.execute_workflow(workflow)
    
    print("\n📈 Completed Tasks:")
    for task in orchestrator.completed_tasks:
        print(f"  ✓ {task.title}")
    
    print("\n🤖 Agent Performance:")
    agent_status = orchestrator.agent_manager.get_all_agent_status()
    for agent in agent_status:
        print(f"  {agent['name']}: {agent['success_rate']:.1%} success rate")
    
    await orchestrator.shutdown()
    
    print("\n✅ Demo complete!")


def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--autonomous":
            # Run for specified seconds or 300
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            asyncio.run(main_autonomous(duration=duration))
        
        elif sys.argv[1] == "--demo":
            asyncio.run(run_demo())
        
        elif sys.argv[1] == "--help":
            print("""
JARVIS AI Operating System

Usage:
  python main.py              Start interactive mode
  python main.py --autonomous Start autonomous mode (300 seconds)
  python main.py --autonomous <seconds>  Autonomous mode for N seconds
  python main.py --demo       Run demonstration
  python main.py --help       Show this help
            """)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    
    else:
        # Default: interactive mode
        asyncio.run(main_interactive())


if __name__ == "__main__":
    main()
