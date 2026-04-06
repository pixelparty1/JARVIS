"""
JARVIS Autonomous Agent Loop
Main orchestration of the autonomous agent system
"""

from typing import Dict, List, Any, Optional, Tuple
from agent_planner import Planner, TaskPlan
from agent_executor import Executor, ExecutionContext
from agent_observer import Observer, ObserverResult
from agent_memory import AgentMemory
from tool_registry import ToolRegistry
from brain import JarvisBrain
import time
from datetime import datetime

class AgentLoop:
    """Main autonomous agent loop"""
    
    def __init__(self):
        print("\n🤖 Initializing Autonomous Agent Loop...")
        
        self.planner = Planner()
        self.tool_registry = ToolRegistry()
        self.executor = Executor(self.tool_registry)
        self.observer = Observer()
        self.memory = AgentMemory()
        self.brain = JarvisBrain()
        
        self.active_goals = []
        self.completed_goals = []
        self.failed_goals = []
        
        # Agent state
        self.is_running = False
        self.current_goal = None
        self.replan_count = 0
        self.max_replans = 2
        
        print("✅ Agent loop initialized successfully")
    
    def register_tool(self, name: str, func, description: str, 
                     parameters: Dict, required: List[str], returns: str, category: str = "general"):
        """Register a tool with the agent"""
        self.tool_registry.register_tool(name, func, description, parameters, required, returns, category)
    
    def execute_goal(self, goal: str, context: str = "") -> Tuple[bool, str]:
        """
        Execute a goal through the full agent loop
        
        Args:
            goal: The goal to achieve
            context: Additional context
            
        Returns:
            (success, summary) tuple
        """
        print(f"\n{'='*60}")
        print(f"🎯 AGENT EXECUTING GOAL")
        print(f"{'='*60}")
        print(f"Goal: {goal}")
        
        self.current_goal = goal
        self.replan_count = 0
        
        # Step 1: PLAN
        plan = self.planner.plan(goal, context)
        self.memory.add_goal_in_progress(goal, plan.to_dict())
        
        # Step 2-4: EXECUTE-OBSERVE-REPLAN LOOP
        while self.replan_count <= self.max_replans:
            print(f"\n🔄 Execution attempt {self.replan_count + 1}")
            
            # Execute
            execution_context = self.executor.execute_plan(
                goal,
                plan.steps
            )
            
            # Observe
            observations = self.observer.observe(execution_context)
            
            # Check if successful
            achieved, explanation = self.observer.verify_goal_achievement(goal, execution_context)
            
            print(f"\n✓ Goal achievement: {explanation}")
            
            if achieved:
                # SUCCESS
                print(f"\n✅ GOAL ACHIEVED!")
                self.memory.record_goal_completed(
                    goal,
                    len(plan.steps),
                    (execution_context.end_time - execution_context.start_time).total_seconds()
                )
                self.memory.remove_goal_in_progress(goal)
                self.completed_goals.append(goal)
                
                return True, f"Goal completed: {goal}"
            
            # Check if should replan
            if self.observer.should_replan(observations) and self.replan_count < self.max_replans:
                # REPLAN
                print(f"\n🔄 REPLANNING...")
                failure_info = self.observer.get_failure_info(observations)
                plan = self.planner.refine_plan(plan, failure_info)
                self.replan_count += 1
            else:
                # FAILED
                print(f"\n❌ GOAL FAILED - Max replans reached")
                reason = self.observer.get_failure_info(observations)
                self.memory.record_goal_failed(goal, reason, len(plan.steps))
                self.memory.remove_goal_in_progress(goal)
                self.failed_goals.append(goal)
                
                return False, f"Goal failed: {reason}"
        
        return False, "Execution incomplete"
    
    def suggest_next_actions(self) -> List[str]:
        """Suggest what JARVIS should do next based on context"""
        suggestions = []
        
        # Check if long break needed
        stats = self.memory.get_execution_stats()
        if stats["total_tasks"] > 5:
            working_time = (datetime.now() - datetime.fromisoformat(
                self.memory.memory["agent_profile"]["created_at"]
            )).total_seconds() / 3600
            
            if working_time > 2:
                suggestions.append("💤 You've been working a while. Consider taking a break.")
        
        # Check failed patterns
        if self.failed_goals:
            suggestions.append(f"⚠️ {len(self.failed_goals)} goals failed. Would you like to review them?")
        
        # Check in-progress goals
        if self.memory.memory["goals_in_progress"]:
            suggestions.append("📋 You have incomplete goals. Want to continue?")
        
        return suggestions
    
    def get_system_status(self) -> str:
        """Get current agent system status"""
        status = "🤖 Agent Status Report:\n"
        status += f"{'='*50}\n"
        
        stats = self.memory.get_execution_stats()
        status += f"Total Tasks: {stats['total_tasks']}\n"
        status += f"Successful: {stats['successful']}\n"
        status += f"Failed: {stats['failed']}\n"
        status += f"Success Rate: {stats['success_rate']*100:.1f}%\n"
        status += f"In Progress: {stats['goals_in_progress']}\n\n"
        
        # Tool stats
        tool_stats = self.tool_registry.get_tool_stats()
        status += f"Tools Available: {tool_stats['total_tools']}\n"
        status += f"Total Tool Calls: {tool_stats['total_calls']}\n"
        status += f"Total Tool Errors: {tool_stats['total_errors']}\n\n"
        
        # Observer recommendations
        observer_recommendations = self.observer.get_recommendations()
        status += "Observations:\n"
        for rec in observer_recommendations:
            status += f"  • {rec}\n"
        
        return status
    
    def run_autonomous_mode(self, duration_minutes: int = 10):
        """
        Run agent in autonomous mode for specified duration
        Agent will suggest and execute tasks automatically
        """
        print(f"\n🤖 AUTONOMOUS MODE - Running for {duration_minutes} minutes")
        print(f"{'='*60}")
        
        self.is_running = True
        start_time = datetime.now()
        task_count = 0
        
        try:
            while self.is_running:
                # Check time limit
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                if elapsed > duration_minutes:
                    print(f"\n⏳ Time limit reached ({duration_minutes} minutes)")
                    break
                
                # Suggest action
                suggestions = self.suggest_next_actions()
                
                if suggestions:
                    print(f"\n💡 Suggestion: {suggestions[0]}")
                else:
                    print("\n🤔 No immediate actions. Monitoring system...")
                
                # Check for system alerts (would be implemented in full system)
                
                time.sleep(30)  # Check every 30 seconds
        
        except KeyboardInterrupt:
            print("\n⏹️ Autonomous mode stopped by user")
        
        self.is_running = False
        
        # Print summary
        print(f"\n📊 Autonomous Session Summary:")
        print(f"Duration: {(datetime.now() - start_time).total_seconds():.0f}s")
        print(f"Tasks completed: {len(self.completed_goals)}")
        print(f"Tasks failed: {len(self.failed_goals)}")
    
    def interactive_planning_mode(self):
        """Interactive mode where user confirms each step"""
        print("\n🤖 INTERACTIVE PLANNING MODE")
        print(f"{'='*60}")
        
        while True:
            goal = input("\n📝 Enter goal (or 'quit' to exit): ").strip()
            
            if goal.lower() == "quit":
                break
            
            # Plan
            plan = self.planner.plan(goal)
            
            # Ask user to refine
            refine = input("\nRefine plan? (y/n): ").lower()
            if refine == "y":
                print("\nHow would you like to modify it?")
                modifications = input("> ").strip()
                # In a full system, would refine based on user input
            
            # Execute with confirmation
            success, output = self.executor.execute_step_by_step(goal, plan.steps)
            
            if success:
                print(f"\n✅ Goal achieved!")
                self.memory.record_goal_completed(goal, len(plan.steps), 0)
            else:
                print(f"\n❌ Goal incomplete")
                self.memory.record_goal_failed(goal, "User cancelled", len(plan.steps))
    
    def export_agent_state(self, filename: str = "agent_state.json"):
        """Export full agent state to file"""
        import json
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "memory": self.memory.memory,
            "stats": self.memory.get_execution_stats(),
            "completed_goals": self.completed_goals,
            "failed_goals": self.failed_goals,
            "tool_stats": self.tool_registry.get_tool_stats(),
            "observer_summary": self.observer.summarize_observations()
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✅ Agent state exported to {filename}")
    
    def import_tool_set(self, tools: Dict[str, tuple]):
        """
        Register a set of tools
        
        tools format: {
            "tool_name": (function, description, parameters, required, returns, category)
        }
        """
        for tool_name, (func, desc, params, required, returns, cat) in tools.items():
            self.register_tool(tool_name, func, desc, params, required, returns, cat)
    
    def get_tool_recommendations(self, task: str) -> List[str]:
        """Get recommended tools for a task"""
        suggested = self.tool_registry.suggest_tool(task)
        
        if suggested:
            return [suggested]
        
        # Fallback: return tools that might help
        category_map = {
            "search": "web",
            "write": "file",
            "open": "app",
            "calculate": "task"
        }
        
        for keyword, cat in category_map.items():
            if keyword in task.lower():
                return self.tool_registry.get_tools_by_category(cat)
        
        return []
    
    def print_agent_summary(self):
        """Print comprehensive agent summary"""
        print(f"\n{'='*60}")
        print(f"🤖 JARVIS AUTONOMOUS AGENT SUMMARY")
        print(f"{'='*60}\n")
        
        print(self.memory.get_memory_insights())
        print(self.get_system_status())
        
        print(f"\n📋 Recent Completed Goals:")
        for goal in self.completed_goals[-5:]:
            print(f"  ✅ {goal}")
        
        if self.failed_goals:
            print(f"\n❌ Recent Failed Goals:")
            for goal in self.failed_goals[-3:]:
                print(f"  ❌ {goal}")
