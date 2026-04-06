"""
JARVIS Agent Memory Module
Stores and retrieves long-term context for the autonomous agent
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os

class AgentMemory:
    """Long-term memory for autonomous agent"""
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return self._create_default_memory()
        return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict:
        """Create default memory structure"""
        return {
            "agent_profile": {
                "name": "JARVIS",
                "mode": "autonomous",
                "created_at": datetime.now().isoformat()
            },
            "goals_completed": [],
            "goals_failed": [],
            "goals_in_progress": [],
            "user_preferences": {},
            "learned_patterns": {},  # Patterns learned from execution
            "tool_preferences": {},  # Which tools work best
            "common_failures": {},
            "execution_stats": {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0
            }
        }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            self.memory["agent_profile"]["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving memory: {e}")
    
    def record_goal_completed(self, goal: str, steps_executed: int, duration: float):
        """Record a successfully completed goal"""
        entry = {
            "goal": goal,
            "status": "completed",
            "steps": steps_executed,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory["goals_completed"].append(entry)
        self.memory["execution_stats"]["successful_tasks"] += 1
        self.memory["execution_stats"]["total_tasks"] += 1
        
        # Learn from success
        self._learn_from_execution(goal, True)
        
        self._save_memory()
    
    def record_goal_failed(self, goal: str, reason: str, steps_attempted: int):
        """Record a failed goal attempt"""
        entry = {
            "goal": goal,
            "status": "failed",
            "reason": reason,
            "steps": steps_attempted,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory["goals_failed"].append(entry)
        self.memory["execution_stats"]["failed_tasks"] += 1
        self.memory["execution_stats"]["total_tasks"] += 1
        
        # Learn from failure
        self._learn_from_execution(goal, False)
        
        self._save_memory()
    
    def add_goal_in_progress(self, goal: str, plan: Dict):
        """Track goal being worked on"""
        entry = {
            "goal": goal,
            "plan": plan,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        self.memory["goals_in_progress"].append(entry)
        self._save_memory()
    
    def remove_goal_in_progress(self, goal: str):
        """Remove from in-progress when done"""
        self.memory["goals_in_progress"] = [
            g for g in self.memory["goals_in_progress"]
            if g["goal"] != goal
        ]
        self._save_memory()
    
    def _learn_from_execution(self, goal: str, success: bool):
        """Learn patterns from execution"""
        # Simple learning: track success/failure patterns
        goal_type = goal.split()[0].lower()  # Simple: use first word as type
        
        if goal_type not in self.memory["learned_patterns"]:
            self.memory["learned_patterns"][goal_type] = {
                "successes": 0,
                "failures": 0,
                "examples": []
            }
        
        pattern = self.memory["learned_patterns"][goal_type]
        
        if success:
            pattern["successes"] += 1
        else:
            pattern["failures"] += 1
        
        pattern["examples"].append({
            "goal": goal,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent examples
        pattern["examples"] = pattern["examples"][-10:]
    
    def get_similar_goals(self, goal: str, limit: int = 5) -> List[Dict]:
        """Get similar goals from history"""
        all_goals = self.memory["goals_completed"] + self.memory["goals_failed"]
        
        # Simple similarity: check if key words match
        goal_words = set(goal.lower().split())
        
        similar = []
        for past_goal in all_goals:
            past_words = set(past_goal["goal"].lower().split())
            overlap = len(goal_words & past_words)
            
            if overlap >= 2:  # At least 2 words in common
                similar.append({
                    "goal": past_goal["goal"],
                    "status": past_goal["status"],
                    "similarity": overlap / max(len(goal_words), len(past_words))
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar[:limit]
    
    def get_best_tool_for_task(self, task_type: str) -> Optional[str]:
        """Get tool that worked best for similar tasks"""
        patterns = self.memory["learned_patterns"].get(task_type, {})
        
        if patterns.get("successes", 0) > 0:
            return patterns.get("preferred_tool")
        
        return None
    
    def record_tool_success(self, tool_name: str):
        """Record successful tool usage"""
        if "tool_success_count" not in self.memory["tool_preferences"]:
            self.memory["tool_preferences"]["tool_success_count"] = {}
        
        count = self.memory["tool_preferences"]["tool_success_count"]
        count[tool_name] = count.get(tool_name, 0) + 1
        
        self._save_memory()
    
    def record_tool_failure(self, tool_name: str, error: str):
        """Record tool failure"""
        if "tool_failure_count" not in self.memory["tool_preferences"]:
            self.memory["tool_preferences"]["tool_failure_count"] = {}
        
        if tool_name not in self.memory["common_failures"]:
            self.memory["common_failures"][tool_name] = []
        
        count = self.memory["tool_preferences"]["tool_failure_count"]
        count[tool_name] = count.get(tool_name, 0) + 1
        
        self.memory["common_failures"][tool_name].append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent failures
        self.memory["common_failures"][tool_name] = \
            self.memory["common_failures"][tool_name][-10:]
        
        self._save_memory()
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        stats = self.memory["execution_stats"]
        success_rate = 0
        
        if stats["total_tasks"] > 0:
            success_rate = stats["successful_tasks"] / stats["total_tasks"]
        
        return {
            "total_tasks": stats["total_tasks"],
            "successful": stats["successful_tasks"],
            "failed": stats["failed_tasks"],
            "success_rate": success_rate,
            "goals_in_progress": len(self.memory["goals_in_progress"])
        }
    
    def get_memory_insights(self) -> str:
        """Get insights from memory"""
        insights = "🧠 Agent Memory Insights:\n\n"
        
        # Stats
        stats = self.memory["execution_stats"]
        if stats["total_tasks"] > 0:
            rate = 100 * stats["successful_tasks"] / stats["total_tasks"]
            insights += f"Success Rate: {rate:.1f}%\n"
        
        # Most successful patterns
        if self.memory["learned_patterns"]:
            insights += "\nSuccessful Patterns:\n"
            patterns = sorted(
                self.memory["learned_patterns"].items(),
                key=lambda x: x[1]["successes"],
                reverse=True
            )
            for pattern_type, data in patterns[:3]:
                if data["successes"] > 0:
                    insights += f"  • {pattern_type}: {data['successes']} successes\n"
        
        # Common failures
        if self.memory["common_failures"]:
            insights += "\nCommon Failures:\n"
            failures = sorted(
                self.memory["common_failures"].items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
            for tool, errors in failures[:3]:
                insights += f"  • {tool}: {len(errors)} errors\n"
        
        return insights
    
    def set_user_preference(self, key: str, value: Any):
        """Set learned user preference"""
        self.memory["user_preferences"][key] = value
        self._save_memory()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.memory["user_preferences"].get(key, default)
    
    def get_memory_summary(self) -> Dict:
        """Get comprehensive memory summary"""
        return {
            "profile": self.memory["agent_profile"],
            "stats": self.memory["execution_stats"],
            "goals_completed": len(self.memory["goals_completed"]),
            "goals_failed": len(self.memory["goals_failed"]),
            "goals_in_progress": len(self.memory["goals_in_progress"]),
            "learned_patterns": len(self.memory["learned_patterns"]),
            "common_failures": len(self.memory["common_failures"])
        }
