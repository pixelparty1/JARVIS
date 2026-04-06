"""
JARVIS Agent Planner Module
Breaks complex goals into executable steps using AI reasoning
"""

from brain import JarvisBrain
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class TaskPlan:
    """Represents a plan to achieve a goal"""
    
    def __init__(self, goal: str, steps: List[Dict[str, Any]], reasoning: str):
        self.goal = goal
        self.steps = steps
        self.reasoning = reasoning
        self.created_at = datetime.now().isoformat()
        self.status = "pending"
        self.completed_steps = []
        self.failed_steps = []
    
    def to_dict(self) -> Dict:
        """Convert plan to dictionary"""
        return {
            "goal": self.goal,
            "steps": self.steps,
            "reasoning": self.reasoning,
            "created_at": self.created_at,
            "status": self.status,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps
        }


class Planner:
    """Plans complex tasks by breaking them into steps"""
    
    def __init__(self):
        self.brain = JarvisBrain()
        self.plans = []
    
    def plan(self, goal: str, context: str = "") -> TaskPlan:
        """
        Create a plan to achieve a goal
        
        Args:
            goal: High-level goal to achieve
            context: Additional context about the task
            
        Returns:
            TaskPlan object with steps
        """
        print(f"\n🤔 Planning task: {goal}")
        
        # Build planning prompt
        planning_prompt = f"""You are an expert task planner. Break down this goal into clear, executable steps.

GOAL: {goal}
{f"CONTEXT: {context}" if context else ""}

For each step, provide:
1. action: What to do (noun phrase)
2. tool: Primary tool needed (open_app, search_web, write_file, etc.)
3. parameters: Input parameters needed
4. expected_output: What success looks like

Respond with ONLY a valid JSON array. Example format:
[
  {{"action": "Search for latest AI news", "tool": "search_web", "parameters": {{"query": "AI news today"}}, "expected_output": "List of recent AI articles"}},
  {{"action": "Read first article", "tool": "read_url", "parameters": {{"url": ""}}, "expected_output": "Article content"}},
  {{"action": "Summarize content", "tool": "summarize", "parameters": {{"text": "article content"}}, "expected_output": "2-3 sentence summary"}}
]

Return ONLY the JSON array, no other text."""
        
        # Get plan from AI
        messages = [
            {"role": "system", "content": "You are a task planning AI. Return ONLY valid JSON, nothing else."},
            {"role": "user", "content": planning_prompt}
        ]
        
        try:
            completion = self.brain.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.5,  # Lower for more structured output
                max_completion_tokens=1000,
                top_p=1.0,
                stream=False
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # Extract JSON
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                steps = json.loads(json_str)
            else:
                steps = self._create_fallback_plan(goal)
            
            # Get reasoning
            reasoning = self._get_reasoning(goal, steps)
            
            plan = TaskPlan(goal, steps, reasoning)
            self.plans.append(plan)
            
            print(f"✅ Plan created with {len(steps)} steps")
            self._print_plan(plan)
            
            return plan
        
        except Exception as e:
            print(f"❌ Planning error: {e}")
            # Fallback plan
            steps = self._create_fallback_plan(goal)
            plan = TaskPlan(goal, steps, f"Fallback plan for: {goal}")
            self.plans.append(plan)
            return plan
    
    def _get_reasoning(self, goal: str, steps: List[Dict]) -> str:
        """Get reasoning behind the plan"""
        reasoning_prompt = f"""Explain briefly why this is the right approach for: {goal}

Steps: {len(steps)}
{chr(10).join([f"- {s.get('action', 'Unknown')}" for s in steps])}

Keep reasoning to 2-3 sentences."""
        
        try:
            response = self.brain.query(reasoning_prompt)
            return response
        except:
            return "Plan created based on task analysis"
    
    def _create_fallback_plan(self, goal: str) -> List[Dict]:
        """Create a fallback plan if AI planning fails"""
        # Simple heuristic-based fallback
        if "search" in goal.lower():
            return [
                {"action": "Search for information", "tool": "search_web", "parameters": {"query": goal}, "expected_output": "Search results"},
                {"action": "Summarize results", "tool": "summarize", "parameters": {}, "expected_output": "Summary of findings"}
            ]
        elif "write" in goal.lower() or "save" in goal.lower():
            return [
                {"action": "Prepare content", "tool": "prepare_content", "parameters": {}, "expected_output": "Content ready"},
                {"action": "Write to file", "tool": "write_file", "parameters": {}, "expected_output": "File saved"}
            ]
        elif "open" in goal.lower():
            return [
                {"action": "Open application", "tool": "open_app", "parameters": {}, "expected_output": "App opened"}
            ]
        else:
            return [
                {"action": "Execute primary task", "tool": "execute_task", "parameters": {}, "expected_output": "Task completed"}
            ]
    
    def _print_plan(self, plan: TaskPlan):
        """Print plan details"""
        print(f"\n📋 Plan for: {plan.goal}")
        print(f"Reasoning: {plan.reasoning}\n")
        for i, step in enumerate(plan.steps, 1):
            print(f"  Step {i}: {step.get('action', 'Unknown')}")
            print(f"    Tool: {step.get('tool', 'N/A')}")
            print(f"    Expected: {step.get('expected_output', 'N/A')}")
    
    def refine_plan(self, plan: TaskPlan, failure_info: str) -> TaskPlan:
        """Refine plan based on execution failures"""
        print(f"\n🔄 Refining plan due to: {failure_info}")
        
        refinement_prompt = f"""The following steps failed: {failure_info}

Original goal: {plan.goal}
Original steps: {len(plan.steps)}

Propose an alternative approach. Return ONLY JSON array of new steps."""
        
        try:
            # Get refined steps
            response = self.brain.query(refinement_prompt)
            
            # Parse response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1:
                refined_steps = json.loads(response[start_idx:end_idx])
                refined_plan = TaskPlan(plan.goal, refined_steps, f"Refined plan: {plan.reasoning}")
                self.plans.append(refined_plan)
                return refined_plan
        except:
            pass
        
        return plan
    
    def get_plan_history(self) -> List[Dict]:
        """Get history of all plans"""
        return [p.to_dict() for p in self.plans]
    
    def estimate_complexity(self, goal: str) -> int:
        """Estimate task complexity (1-10)"""
        # Simple heuristic
        factors = 0
        if len(goal.split()) > 20:
            factors += 2
        if any(x in goal.lower() for x in ["and", "then", "after", "multiple"]):
            factors += 3
        if any(x in goal.lower() for x in ["search", "research", "analyze"]):
            factors += 2
        
        return min(10, max(1, factors))
