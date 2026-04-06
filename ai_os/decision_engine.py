"""
Decision Engine - Intelligent decision making with Groq

Determines:
- What action to take next
- Priority of actions
- Whether to interrupt user
- Confidence in decisions

Uses Groq for reasoning over full context
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from .core_types import Decision, Priority, Task, TaskStatus, AgentType


class DecisionEngine:
    """
    Makes intelligent decisions about what JARVIS should do next
    
    Process:
    1. Gather context from ContextEngine
    2. Identify possible actions
    3. Use Groq to reason about best action
    4. Calculate priority and confidence
    5. Recommend decision with reasoning
    """
    
    def __init__(self, groq_client=None, context_engine=None):
        """
        Initialize decision engine
        
        Args:
            groq_client: Groq API client for reasoning
            context_engine: ContextEngine for unified context
        """
        self.groq = groq_client
        self.context_engine = context_engine
        self.decision_history: List[Decision] = []
        self.max_history = 100
    
    async def evaluate_task(self, task: Task) -> Decision:
        """
        Evaluate a task and return a decision
        
        Returns:
            Decision object with action, priority, confidence, and reasoning
        """
        
        # Get context
        context = self.context_engine.get_context_for_decision("schedule_task")
        
        # Build evaluation prompt
        prompt = self._build_task_evaluation_prompt(task, context)
        
        # Get Groq reasoning
        reasoning = await self._groq_reason(prompt)
        
        # Parse reasoning into decision
        decision = self._parse_reasoning(task, reasoning, context)
        
        # Record decision
        self.decision_history.append(decision)
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history:]
        
        return decision
    
    async def decide_next_action(self) -> Optional[Decision]:
        """
        Determine the next action JARVIS should take
        
        Returns:
            Best Decision to execute, or None if no action needed
        """
        
        # Get full context
        context = self.context_engine.to_dict()
        
        # Build decision prompt
        prompt = self._build_next_action_prompt(context)
        
        # Get Groq reasoning
        reasoning = await self._groq_reason(prompt)
        
        # Parse into decision
        decision = self._parse_action_decision(reasoning, context)
        
        if decision:
            self.decision_history.append(decision)
            if len(self.decision_history) > self.max_history:
                self.decision_history = self.decision_history[-self.max_history:]
        
        return decision
    
    async def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Prioritize a list of tasks using context and Groq reasoning
        
        Returns:
            Tasks sorted by priority and urgency
        """
        
        if not tasks:
            return []
        
        # Get context
        context = self.context_engine.to_dict()
        
        # Build prioritization prompt
        prompt = self._build_prioritization_prompt(tasks, context)
        
        # Get Groq ranking
        ranking = await self._groq_reason(prompt)
        
        # Parse ranking and reorder
        ordered_tasks = self._parse_task_ranking(tasks, ranking)
        
        return ordered_tasks
    
    async def should_interrupt_user(self, message: str) -> bool:
        """
        Decide if JARVIS should interrupt user to deliver a message
        
        Uses context to determine appropriateness
        """
        
        # Get context
        context = self.context_engine.to_dict()
        
        # Build interrupt decision prompt
        prompt = f"""
Given the current context and message, should JARVIS interrupt the user?

Current Context:
- Activity: {context['screen'].get('active_window', 'Unknown')}
- User mood: {context['user'].get('mood', 'unknown')}
- User focus: {context['user'].get('focus_level', 0)}
- System busy: CPU {context['system'].get('cpu_usage', 0)}%

Message to deliver: {message}

Decide: YES (interrupt) or NO (wait).
Explain your reasoning in 1-2 sentences.
Format: "YES/NO: [reasoning]"
"""
        
        response = await self._groq_reason(prompt)
        
        should_interrupt = response.strip().upper().startswith("YES")
        return should_interrupt
    
    def get_decision_reasoning(self, decision: Decision) -> str:
        """Get detailed reasoning for a decision"""
        return decision.reasoning
    
    def get_decision_history(self, limit: int = 10) -> List[Decision]:
        """Get recent decision history"""
        return self.decision_history[-limit:]
    
    # === Internal Methods ===
    
    def _build_task_evaluation_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        """Build prompt to evaluate a task"""
        
        # Summarize context
        context_summary = self._summarize_context(context)
        
        prompt = f"""
You are JARVIS, an intelligent AI operating system making decisions about task execution.

CURRENT SYSTEM CONTEXT:
{context_summary}

TASK TO EVALUATE:
Title: {task.title}
Description: {task.description}
Priority: {task.priority.name if hasattr(task.priority, 'name') else task.priority}
Type: {task.agent_type.value if task.agent_type else 'general'}

DECIDE:
1. Should this task be executed now? (YES/NO)
2. What priority? (CRITICAL/HIGH/NORMAL/LOW/BACKGROUND)
3. Confidence in decision (0-100)
4. Brief reasoning

Format your response as:
EXECUTE: YES/NO
PRIORITY: [LEVEL]
CONFIDENCE: [0-100]
REASONING: [Your reasoning]
"""
        
        return prompt
    
    def _build_next_action_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt to determine next action"""
        
        context_summary = self._summarize_context(context)
        
        prompt = f"""
You are JARVIS, an intelligent AI operating system. Analyze the current context and recommend the next best action.

CURRENT CONTEXT:
{context_summary}

DECIDE:
1. What is the most important action to take right now?
2. What agent should handle it?
3. Priority level?
4. Confidence (0-100)?
5. Why this action?

Format:
ACTION: [Specific action]
AGENT: [RESEARCH/CODING/COMMUNICATION/AUTOMATION/ASSISTANT]
PRIORITY: [CRITICAL/HIGH/NORMAL/LOW/BACKGROUND]
CONFIDENCE: [0-100]
REASONING: [Your reasoning]

If no action is needed, start with "ACTION: NONE"
"""
        
        return prompt
    
    def _build_prioritization_prompt(self, tasks: List[Task], context: Dict[str, Any]) -> str:
        """Build prompt to prioritize tasks"""
        
        context_summary = self._summarize_context(context)
        
        # Format tasks
        task_list = "\n".join([
            f"{i+1}. {task.title} (current priority: {task.priority.name})"
            for i, task in enumerate(tasks)
        ])
        
        prompt = f"""
You are JARVIS prioritizing tasks in context of the current situation.

CURRENT CONTEXT:
{context_summary}

TASKS TO PRIORITIZE:
{task_list}

Reorder these tasks by true priority considering:
- User's current mood and energy
- System capacity
- Time-sensitive items
- Dependencies
- User patterns

Output the numbered order (e.g., "3, 1, 4, 2") with brief explanation.
"""
        
        return prompt
    
    def _summarize_context(self, context: Dict[str, Any]) -> str:
        """Create readable context summary for prompts"""
        
        lines = []
        
        # User
        user = context.get('user', {})
        lines.append(f"• User: {user.get('mood', 'unknown')} mood, {user.get('energy_level', 'normal')} energy")
        
        # Activity
        screen = context.get('screen', {})
        if screen.get('active_window'):
            lines.append(f"• Activity: {screen['active_window']}")
        
        # Vision
        vision = context.get('vision', {})
        if vision.get('detected_people'):
            lines.append(f"• People present: {', '.join(vision['detected_people'])}")
        
        # System
        system = context.get('system', {})
        lines.append(f"• System: CPU {system.get('cpu_usage', 0):.0f}%, Memory {system.get('memory_usage', 0):.0f}%")
        
        # Time
        lines.append(f"• Time: {system.get('time_of_day', 'unknown')}")
        
        # Integrations
        integrations = context.get('integrations', {})
        events = integrations.get('calendar_events', [])
        if events:
            lines.append(f"• Next event: {events[0]}")
        
        return "\n".join(lines)
    
    async def _groq_reason(self, prompt: str) -> str:
        """Use Groq to generate reasoning"""
        
        if not self.groq:
            # Fallback if Groq not available
            return "REASONING: Groq not configured"
        
        try:
            message = self.groq.messages.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return message.content[0].text
        except Exception as e:
            print(f"Groq error: {e}")
            return "REASONING: Unable to reason at this time"
    
    def _parse_reasoning(self, task: Task, reasoning: str, context: Dict[str, Any]) -> Decision:
        """Parse Groq reasoning into a Decision object"""
        
        decision = Decision(
            action=f"Execute {task.title}",
            reasoning=reasoning,
            task=task,
            agent_type=task.agent_type
        )
        
        # Parse priority from reasoning
        if "PRIORITY: CRITICAL" in reasoning:
            decision.priority = Priority.CRITICAL
        elif "PRIORITY: HIGH" in reasoning:
            decision.priority = Priority.HIGH
        elif "PRIORITY: NORMAL" in reasoning:
            decision.priority = Priority.NORMAL
        elif "PRIORITY: LOW" in reasoning:
            decision.priority = Priority.LOW
        else:
            decision.priority = Priority.NORMAL
        
        # Parse confidence
        if "CONFIDENCE:" in reasoning:
            try:
                conf_str = reasoning.split("CONFIDENCE:")[-1].split("\n")[0].strip()
                decision.confidence = int(conf_str.split()[0]) / 100
            except:
                decision.confidence = 0.7
        
        # Check if execution needed
        if "EXECUTE: NO" in reasoning or "NO:" in reasoning:
            decision.action = f"Defer {task.title}"
            decision.confidence *= 0.5
        
        return decision
    
    def _parse_action_decision(self, reasoning: str, context: Dict[str, Any]) -> Optional[Decision]:
        """Parse action decision from Groq reasoning"""
        
        if "ACTION: NONE" in reasoning:
            return None
        
        decision = Decision(
            action="Execute recommended action",
            reasoning=reasoning,
            created_at=datetime.now()
        )
        
        # Parse action
        if "ACTION:" in reasoning:
            action_line = reasoning.split("ACTION:")[-1].split("\n")[0].strip()
            decision.action = action_line
        
        # Parse agent
        if "AGENT: RESEARCH" in reasoning:
            decision.agent_type = AgentType.RESEARCH
        elif "AGENT: CODING" in reasoning:
            decision.agent_type = AgentType.CODING
        elif "AGENT: COMMUNICATION" in reasoning:
            decision.agent_type = AgentType.COMMUNICATION
        elif "AGENT: AUTOMATION" in reasoning:
            decision.agent_type = AgentType.AUTOMATION
        elif "AGENT: ASSISTANT" in reasoning:
            decision.agent_type = AgentType.ASSISTANT
        
        # Parse priority
        if "PRIORITY: CRITICAL" in reasoning:
            decision.priority = Priority.CRITICAL
        elif "PRIORITY: HIGH" in reasoning:
            decision.priority = Priority.HIGH
        elif "PRIORITY: NORMAL" in reasoning:
            decision.priority = Priority.NORMAL
        elif "PRIORITY: LOW" in reasoning:
            decision.priority = Priority.LOW
        
        # Parse confidence
        if "CONFIDENCE:" in reasoning:
            try:
                conf_str = reasoning.split("CONFIDENCE:")[-1].split("\n")[0].strip()
                conf_num = int(conf_str.split()[0])
                decision.confidence = conf_num / 100
            except:
                decision.confidence = 0.7
        
        return decision
    
    def _parse_task_ranking(self, tasks: List[Task], ranking: str) -> List[Task]:
        """Parse task ranking from Groq reasoning"""
        
        # Try to extract order numbers
        try:
            # Look for pattern like "1, 2, 3" or "3, 1, 4"
            import re
            order_match = re.search(r"(\d+(?:\s*,\s*\d+)+)", ranking)
            if order_match:
                order_str = order_match.group(1)
                indices = [int(x.strip()) - 1 for x in order_str.split(",")]
                
                # Reorder tasks
                ordered = []
                for idx in indices:
                    if 0 <= idx < len(tasks):
                        ordered.append(tasks[idx])
                
                # Add any remaining tasks
                for task in tasks:
                    if task not in ordered:
                        ordered.append(task)
                
                return ordered
        except:
            pass
        
        # Fallback: return original order
        return tasks
