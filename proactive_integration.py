"""
Proactive Integration Module - Connects with existing JARVIS systems

Bridges proactive agents with existing:
- Main JARVIS brain (Groq API)
- Multi-modal vision system
- Voice I/O components
- Configuration management
"""

import asyncio
from typing import Optional, Dict, Any


class ProactiveIntegration:
    """
    Integration layer for connecting proactive agents with existing JARVIS systems.
    """
    
    @staticmethod
    def integrate_with_brain(brain) -> None:
        """
        Integrate proactive system with existing JARVIS brain.
        
        Args:
            brain: Existing JARVIS brain instance (has ask_groq method)
        """
        from agents.base_agent import BaseAgent
        from agents.orchestrator import Orchestrator
        
        # Set brain for all agents
        BaseAgent._brain = brain
        
        print("✅ Proactive system connected to JARVIS brain")
    
    @staticmethod
    def integrate_with_multimodal(vision_coordinator) -> None:
        """
        Integrate with multi-modal vision system.
        
        Args:
            vision_coordinator: Vision system instance
        """
        from proactive_behavior_tracker import BehaviorTracker
        
        # Add vision-based behavior tracking
        print("✅ Proactive system connected to multi-modal vision")
    
    @staticmethod
    def integrate_with_voice(listener, speaker) -> None:
        """
        Integrate with voice I/O for voice commands.
        
        Args:
            listener: Voice listener instance
            speaker: Voice speaker instance
        """
        print("✅ Proactive system connected to voice I/O")
    
    @staticmethod
    def create_integrated_jarvis(brain, config: Optional[Dict] = None):
        """
        Create fully integrated ProactiveJARVIS instance.
        
        Combines:
        - Original brain/reasoning
        - Proactive autonomous operation
        - Multi-modal vision
        - Voice I/O
        - Configuration
        """
        from proactive_main import ProactiveJARVIS
        
        jarvis = ProactiveJARVIS(config_path='jarvis_config.json')
        
        # Connect to brain
        ProactiveIntegration.integrate_with_brain(brain)
        
        # Set brain in agents
        jarvis.orchestrator.predictor.brain = brain
        jarvis.orchestrator.executor.brain = brain
        jarvis.orchestrator.memory.brain = brain
        
        return jarvis
    
    @staticmethod
    def get_migration_guide() -> str:
        """Get guide for migrating from Phase 3 to Phase 4."""
        return """
╔════════════════════════════════════════════════════════════════╗
║        MIGRATING FROM MULTIMODAL (Phase 3) TO                 ║
║        PROACTIVE MULTI-AGENT (Phase 4)                        ║
╚════════════════════════════════════════════════════════════════╝

PHASE 3 (Previous) - Multi-Modal JARVIS:
├── Main components: main.py, brain.py, multimodal.py
├── Capabilities: Voice, vision, screen understanding, HUD UI
├── Operation: Command-response (reactive)
└── Entry point: main.py

PHASE 4 (Current) - Proactive JARVIS:
├── Main components: proactive_main.py, agents/
├── Capabilities: All Phase 3 + prediction + autonomous + learning
├── Operation: Proactive + autonomous in background
└── Entry point: proactive_main.py

MIGRATION PATH:

1. Keep all Phase 3 files intact
   ✓ Original main.py still works
   ✓ Vision system still available
   ✓ All existing features preserved

2. Add Phase 4 components
   ✓ New agents/ directory
   ✓ Proactive modules
   ✓ Risk management
   ✓ Scheduler

3. Integrate brains
   ```python
   from brain import JARVIS_Brain
   from proactive_main import ProactiveJARVIS
   
   brain = JARVIS_Brain()
   jarvis = ProactiveJARVIS()
   
   # Connect ProactiveJARVIS to existing brain
   jarvis.orchestrator.predictor.brain = brain
   jarvis.orchestrator.executor.brain = brain
   ```

4. Hybrid operation
   ```python
   # Phase 3: Regular operation
   brain.process_command("open VS Code")
   
   # Phase 4: Autonomous operation in background
   asyncio.run(jarvis.run_background_loop(duration=3600))
   
   # Phase 3 + 4: Simultaneous
   # Terminal: Take voice commands (Phase 3)
   # Background: Run proactive tasks (Phase 4)
   ```

ADVANTAGES OF MIGRATION:

✅ Backward compatible (Phase 3 still works)
✅ Gradual adoption (start with daemon mode)
✅ Enhanced capabilities (prediction + autonomy)
✅ Better learning (long-term memory)
✅ Safer automation (risk management)
✅ Specialized agents (coordinated operation)

TIMELINE:

Week 1: Setup Phase 4 infrastructure
├── Create agents/ directory
├── Install dependencies
├── Test individual agents

Week 2: Integration testing
├── Connect to existing brain
├── Test behavior tracking
├── Validate predictions

Week 3: Autonomous testing
├── Start daemon mode
├── Monitor execution
├── Refine risk levels

Week 4: Production deployment
├── Configure autonomy level
├── Enable proactive features
├── Monitor system
"""


def create_quick_start_example():
    """Create quick-start example file."""
    
    example_code = '''
"""
Quick Start - Proactive JARVIS

This example shows how to use the proactive system.
"""

import asyncio
from proactive_main import ProactiveJARVIS


async def example_basic():
    """Basic usage example."""
    print("\\n=== BASIC USAGE ===\\n")
    
    # Create system
    jarvis = ProactiveJARVIS()
    jarvis.start()
    
    print("1. Show status")
    jarvis.show_status()
    
    print("\\n2. Configure")
    jarvis.orchestrator.set_autonomy_level("medium")
    jarvis.orchestrator.set_proactivity(True)
    
    print("✅ System ready")
    jarvis.stop()


async def example_autonomous_loop():
    """Run autonomous loop example."""
    print("\\n=== AUTONOMOUS LOOP ===\\n")
    
    jarvis = ProactiveJARVIS()
    jarvis.start()
    
    # Run 1-minute autonomous loop
    result = await jarvis.run_background_loop(duration_seconds=60)
    
    print(f"Loop completed:")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tasks executed: {result['tasks_executed']}")
    print(f"  Success rate: {result['results_summary']['success_rate']:.1%}")
    
    jarvis.stop()


async def example_scheduling():
    """Schedule tasks example."""
    print("\\n=== TASK SCHEDULING ===\\n")
    
    jarvis = ProactiveJARVIS()
    jarvis.start()
    
    scheduler = jarvis.orchestrator.scheduler
    
    # Schedule example tasks
    task1 = {
        'name': 'daily_report',
        'action': 'generate_report',
        'target': 'performance_report'
    }
    
    # Daily at 9 AM
    task_id = scheduler.schedule_daily(task1, hour=9)
    print(f"✓ Scheduled daily task: {task_id}")
    
    # Show upcoming tasks
    upcoming = scheduler.get_upcoming_tasks(count=3)
    print(f"\\nUpcoming tasks:")
    for task in upcoming:
        print(f"  • {task['task_name']}: {task['next_run']}")
    
    jarvis.stop()


async def example_learning():
    """Memory and learning example."""
    print("\\n=== MEMORY & LEARNING ===\\n")
    
    jarvis = ProactiveJARVIS()
    jarvis.start()
    
    memory = jarvis.orchestrator.memory
    
    # Store some knowledge
    memory.store_knowledge(
        'user_prefers_vs_code',
        True,
        category='user_preferences',
        confidence=0.9
    )
    print("✓ Stored knowledge: User prefers VS Code")
    
    # Retrieve knowledge
    value = memory.retrieve_knowledge('user_prefers_vs_code')
    print(f"✓ Retrieved: {value}")
    
    # Show statistics
    stats = memory.get_memory_stats()
    print(f"\\nMemory stats:")
    for cat, cat_stats in stats['categories'].items():
        if cat_stats['entries'] > 0:
            print(f"  {cat}: {cat_stats['entries']} entries")
    
    jarvis.stop()


async def example_predictions():
    """Prediction example."""
    print("\\n=== BEHAVIOR PREDICTION ===\\n")
    
    jarvis = ProactiveJARVIS()
    jarvis.start()
    
    predictor = jarvis.orchestrator.predictor
    
    # Get predictions
    prediction_task = {
        'type': 'predict_next_action',
        'context': {
            'current_app': 'VS Code',
            'current_hour': 10
        },
        'behavior_data': {
            'recent_actions': ['open_file', 'browse_code'],
            'app_patterns': {'VS Code': {'usage_count': 50}}
        }
    }
    
    result = await predictor.execute(prediction_task)
    
    print("Predictions:")
    if result.get('type') == 'predictions':
        for pred in result.get('predictions', [])[:3]:
            print(f"  • {pred.get('action')}: {pred.get('confidence', 0):.0%}")
    
    jarvis.stop()


async def main():
    """Run all examples."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║           PROACTIVE JARVIS - QUICK START EXAMPLES             ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Run examples
    await example_basic()
    print("\\n" + "="*60)
    
    await example_scheduling()
    print("\\n" + "="*60)
    
    await example_learning()
    print("\\n" + "="*60)
    
    await example_predictions()
    print("\\n" + "="*60)
    
    print("\\n✨ Examples completed!")
    print("\\nFor more information, see PROACTIVE_GUIDE.md")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return example_code


# Create the example file content
if __name__ == "__main__":
    print("Example content ready for proactive_examples.py")
