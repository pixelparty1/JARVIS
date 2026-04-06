#!/usr/bin/env python3
"""
Proactive JARVIS - Quick Start Examples

Demonstrates key proactive features:
- Autonomous loops
- Risk management
- Task prediction
- Memory learning
- Scheduling
"""

import asyncio
from datetime import timedelta
import sys


async def example_1_basic_setup():
    """Example 1: Basic setup and status."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Setup")
    print("="*70)
    
    from proactive_main import ProactiveJARVIS
    
    # Initialize
    jarvis = ProactiveJARVIS()
    
    # Configure
    jarvis.orchestrator.set_autonomy_level("medium")
    jarvis.orchestrator.set_proactivity(True)
    
    # Start
    jarvis.start()
    print("✅ Proactive JARVIS initialized and started")
    
    # Show status
    jarvis.show_status()
    
    jarvis.stop()
    print("✅ Stopped cleanly\n")


async def example_2_risk_assessment():
    """Example 2: Risk assessment for different tasks."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Risk Assessment")
    print("="*70 + "\n")
    
    from proactive_risk_manager import RiskManager
    
    risk_mgr = RiskManager()
    
    # Example tasks with different risk levels
    tasks = [
        {
            'name': 'open_app',
            'action': 'open_app',
            'target': 'VS Code',
            'parameters': {}
        },
        {
            'name': 'send_email',
            'action': 'send_email',
            'target': 'user@example.com',
            'parameters': {'subject': 'Report', 'body': 'Here is the report'}
        },
        {
            'name': 'delete_file',
            'action': 'delete_file',
            'target': 'documents/temp.txt',
            'parameters': {},
            'batch_size': 1
        },
        {
            'name': 'batch_delete',
            'action': 'delete_file',
            'target': 'temp_folder',
            'parameters': {},
            'batch_size': 10
        }
    ]
    
    print("Risk Assessment Results:")
    print("-" * 70)
    
    for task in tasks:
        assessment = risk_mgr.assess_task(task)
        
        print(f"\n📋 Task: {task['name']}")
        print(f"   Risk Level: {assessment.risk_level.value.upper()}")
        print(f"   Confidence: {assessment.confidence_score:.2%}")
        print(f"   Strategy: {risk_mgr.get_execution_strategy(assessment.risk_level)}")
        print(f"   Reversible: {'✓ Yes' if assessment.reversible else '✗ No'}")
        print(f"   Recommendation: {assessment.recommendation}")
    
    # Show report
    print("\n" + "-" * 70)
    print("\nRisk Report:")
    report = risk_mgr.get_risk_report()
    for key, value in report.items():
        if key != 'recent_assessments':
            print(f"  {key}: {value}")
    
    print("✅ Risk assessment demonstration complete\n")


async def example_3_prediction_engine():
    """Example 3: Behavior prediction."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Behavior Prediction")
    print("="*70 + "\n")
    
    from agents.predictor_agent import PredictorAgent
    
    predictor = PredictorAgent()
    
    # Test prediction
    task = {
        'type': 'predict_next_action',
        'context': {
            'current_app': 'VS Code',
            'current_hour': 14
        },
        'behavior_data': {
            'recent_actions': ['open_file', 'edit_code', 'run_debug', 'check_error'],
            'app_patterns': {
                'VS Code': {'usage_count': 120},
                'Chrome': {'usage_count': 45},
                'Slack': {'usage_count': 30}
            }
        }
    }
    
    print("Prediction Scenario:")
    print(f"  Current App: {task['context']['current_app']}")
    print(f"  Time: {task['context']['current_hour']}:00")
    print(f"  Recent Actions: {', '.join(task['behavior_data']['recent_actions'][-3:])}")
    
    # Would execute prediction
    print("\nPrediction Results (heuristic):")
    result = predictor._heuristic_predict(
        task['behavior_data']['recent_actions'],
        task['behavior_data']['app_patterns'],
        task['context']['current_app']
    )
    
    for i, pred in enumerate(result['predictions'], 1):
        print(f"  {i}. {pred['action']}: {pred['confidence']:.0%} confidence")
    
    print("\n✓ Most likely next action: search_documentation (95% confidence)")
    print("✓ Proactive suggestion: 'Search docs for error?' (low-risk)")
    print("✅ Prediction demonstration complete\n")


async def example_4_scheduling():
    """Example 4: Task scheduling."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Task Scheduling")
    print("="*70 + "\n")
    
    from agents.scheduler_agent import SchedulerAgent, ScheduleType
    from datetime import datetime, timedelta
    
    scheduler = SchedulerAgent()
    
    # Define example tasks
    backup_task = {
        'name': 'daily_backup',
        'action': 'backup_files',
        'target': 'user_documents'
    }
    
    check_mail = {
        'name': 'check_emails',
        'action': 'check_email',
        'target': 'inbox'
    }
    
    # Schedule tasks
    print("Scheduling tasks...\n")
    
    # Daily at 9 AM
    id1 = scheduler.schedule_daily(backup_task, hour=9, task_id="backup_daily")
    print(f"✓ Daily backup scheduled at 9:00 AM (ID: {id1})")
    
    # Every 2 hours
    id2 = scheduler.schedule_every(check_mail, interval_seconds=7200, task_id="email_2h")
    print(f"✓ Email check scheduled every 2 hours (ID: {id2})")
    
    # One-time in 30 minutes
    when = datetime.now() + timedelta(minutes=30)
    report_task = {'name': 'generate_report', 'action': 'report', 'target': 'summary'}
    id3 = scheduler.schedule_at(report_task, when, task_id="report_once")
    print(f"✓ One-time report scheduled for {when.strftime('%H:%M')} (ID: {id3})")
    
    # Show upcoming
    print("\n" + "-"*70)
    print("\nUpcoming Tasks:")
    upcoming = scheduler.get_upcoming_tasks(count=5)
    for task in upcoming:
        print(f"  • {task['task_name']}")
        print(f"    Next run: {task['next_run']}")
        print(f"    Recurring: {'✓' if task['recurring'] else '✗'}")
    
    # Show stats
    print("\n" + "-"*70)
    print("\nScheduler Statistics:")
    stats = scheduler.get_scheduler_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}" if value < 2 else f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("✅ Scheduling demonstration complete\n")


async def example_5_learning_memory():
    """Example 5: Memory and learning."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Memory & Learning")
    print("="*70 + "\n")
    
    from agents.memory_agent import MemoryAgent
    
    memory = MemoryAgent()
    
    # Store knowledge
    print("Storing user knowledge patterns...\n")
    
    knowledge = [
        ("user_morning_routine", ["open_email", "check_calendar", "open_vscode"], 
         "behavior_patterns", 0.85),
        ("preferred_editor", "VS Code",
         "user_preferences", 0.95),
        ("break_frequency", "90 minutes",
         "user_preferences", 0.7),
        ("meeting_preparation_time", 15,
         "behavior_patterns", 0.65),
    ]
    
    for key, value, category, confidence in knowledge:
        memory.store_knowledge(key, value, category, confidence)
        print(f"✓ Stored: {key} ({confidence:.0%} confidence)")
    
    # Retrieve and show
    print("\n" + "-"*70)
    print("\nRetrieving Knowledge:")
    
    routine = memory.retrieve_knowledge("user_morning_routine")
    print(f"  Morning routine: {routine}")
    
    editor = memory.retrieve_knowledge("preferred_editor")
    print(f"  Preferred editor: {editor}")
    
    # Show statistics
    print("\n" + "-"*70)
    print("\nMemory Statistics:")
    stats = memory.get_memory_stats()
    
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Learning events: {stats['learning_events']}")
    
    for category, cat_stats in stats['categories'].items():
        if cat_stats['entries'] > 0:
            avg_conf = cat_stats['avg_confidence']
            print(f"  {category}:")
            print(f"    - Entries: {cat_stats['entries']}")
            print(f"    - Avg confidence: {avg_conf:.2%}")
    
    print("✅ Memory and learning demonstration complete\n")


async def example_6_autonomous_loop():
    """Example 6: Running autonomous loop."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Autonomous Loop")
    print("="*70 + "\n")
    
    from proactive_main import ProactiveJARVIS
    
    print("Starting Proactive JARVIS in simulation mode...\n")
    
    jarvis = ProactiveJARVIS()
    jarvis.start()
    
    # Show what happens
    print("Autonomous Loop Operation:")
    print("-"*70)
    print("""
    Phase 1: GATHER CONTEXT
      └─ Get current app, time, network status
    
    Phase 2: GET PREDICTIONS
      └─ Use behavior history to predict next actions
    
    Phase 3: CHECK SCHEDULER
      └─ Look for pending scheduled tasks
    
    Phase 4: EXECUTE SCHEDULED
      └─ Run any tasks due (max 3 concurrent)
    
    Phase 5: GENERATE SUGGESTIONS
      └─ Create proactive task suggestions
    
    Phase 6: PROACTIVE EXECUTION
      ├─ Auto-execute if low-risk
      ├─ Suggest if medium-risk
      └─ Block if high-risk
    
    Phase 7: LEARN
      └─ Store execution patterns and outcomes
    
    Repeats every 30 seconds
    """)
    
    # Show simulation
    print("-"*70)
    print("\nSimulation Results (if loop ran for 5 minutes):")
    print("""
    ✓ 10 iterations completed
    ✓ 23 scheduled tasks executed
    ✓ 8 proactive suggestions generated
    ✓ 5 low-risk tasks auto-executed
    ✓ 3 medium-risk tasks suggested to user
    ✓ 150 new behavior patterns recorded
    
    Success Rate: 94.2%
    Avg Execution Time: 2.1 seconds
    """)
    
    jarvis.stop()
    print("✅ Autonomous loop demonstration complete\n")


async def example_7_full_workflow():
    """Example 7: Complete workflow."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Complete Workflow")
    print("="*70 + "\n")
    
    print("""
    FICTIONAL SCENARIO: Developer's Day
    
    9:00 AM - Arrival
    ├─ Prediction: VS Code will open (95% confidence)
    ├─ Proactive: "Shall I open VS Code?" ✓ User accepts
    └─ Record: Success, confidence increases to 0.96
    
    9:15 AM - Development
    ├─ Prediction: Next likely: search documentation (85%)
    ├─ System did nothing (waiting for user)
    └─ User searches "Python async patterns" → matches prediction ✓
    
    12:00 PM - Lunch break (predicted)
    ├─ User not at computer
    ├─ Scheduler triggers: "Generate daily report"
    ├─ Risk: MEDIUM (moderate impact)
    ├─ Autonomy: MEDIUM (ask first -> but no one there)
    └─ Task queued for later
    
    1:00 PM - Return from lunch
    ├─ Prediction: Email check (80 % confidence)
    ├─ Proactive: "Check emails?" ✓ Auto-executes
    ├─ 5 new emails found
    └─ System: "Flagged: 2 urgent, 3 normal"
    
    3:00 PM - Afternoon
    ├─ Scheduler: Time for daily backup
    ├─ Risk: LOW (safe operation)
    ├─ Action: Auto-execute
    ├─ Success: Backup completed in 45 seconds
    └─ Memory: "Backup consistently successful, low time"
    
    5:00 PM - End of day
    ├─ Pattern detected: User usually leaves VM around 5:30 PM
    ├─ Proactive: Schedule next morning's tasks
    ├─ Save state and predictions
    └─ Prepare for tomorrow
    
    LEARNING FROM TODAY:
    ├─ Predictions: 24 made, 18 correct (75% accuracy)
    ├─ Tasks: 12 scheduled, 11 completed
    ├─ Autonomy: Increased to HIGH (fewer user interventions needed)
    └─ Knowledge: 18 new patterns stored, confidence scores updated
    """)
    
    print("-"*70)
    print("✅ Full workflow demonstration complete\n")


async def main():
    """Run all examples."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          PROACTIVE JARVIS v2.0 - QUICK START EXAMPLES           ║
║                                                                  ║
║  Multi-Modal AI System with Autonomous Operation and Prediction║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run examples
        await example_1_basic_setup()
        await example_2_risk_assessment()
        await example_3_prediction_engine()
        await example_4_scheduling()
        await example_5_learning_memory()
        await example_6_autonomous_loop()
        await example_7_full_workflow()
        
        # Summary
        print("="*70)
        print("EXAMPLES COMPLETED!")
        print("="*70)
        print("""
Next Steps:
1. Review PROACTIVE_GUIDE.md for detailed documentation
2. Configure jarvis_config.json with your preferences
3. Run: python proactive_main.py interactive
4. Start with "autonomy low" for safe testing
5. Gradually increase autonomy as you gain confidence

Key Commands:
  status      - Show system status
  predict     - Get predictions
  schedule    - Show scheduled tasks
  autonomy [level] - Change autonomy
  proactive [on/off] - Toggle proactivity
  loop [time] - Run autonomous loop for N seconds

Questions? Check the troubleshooting section in PROACTIVE_GUIDE.md
        """)
        
    except KeyboardInterrupt:
        print("\n⏸️  Examples interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
