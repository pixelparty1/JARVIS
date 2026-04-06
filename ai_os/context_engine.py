"""
Context Engine - Unified context aggregation from all JARVIS phases

Combines:
- Voice/speech context (Phase 1)
- Agent orchestration state (Phase 4)
- Memory and knowledge (Phase 5)
- Screen/activity context (Phase 3)
- Integrations state (Phase 6)
- Vision/real-world data (Phase 7)
- User behavior patterns
"""

from typing import Any, Dict, Optional, List, Set
from datetime import datetime
import json


class UnifiedContext:
    """Represents the complete system state and context"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        
        # Phase 1: Voice/Speech context
        self.voice = {
            "last_input": None,
            "language": "en",
            "volume": 0.0,
            "sentiment": "neutral"
        }
        
        # Phase 3: Screen/Activity context
        self.screen = {
            "active_window": None,
            "active_application": None,
            "screen_text": [],
            "clipboard": None,
            "screen_changes": []
        }
        
        # Phase 4: Orchestrator state
        self.orchestration = {
            "planner_state": None,
            "executor_state": None,
            "monitor_state": None,
            "current_plan": None
        }
        
        # Phase 5: Memory & Knowledge
        self.memory = {
            "recent_memories": [],
            "relevant_knowledge": [],
            "learned_patterns": [],
            "user_preferences": {},
            "historical_context": {}
        }
        
        # Phase 6: Integrations
        self.integrations = {
            "email_status": None,
            "calendar_events": [],
            "slack_messages": [],
            "github_notifications": [],
            "notion_tasks": [],
            "iot_status": {},
            "external_workflows": []
        }
        
        # Phase 7: Vision/Real-world
        self.vision = {
            "detected_people": [],
            "emotions": [],
            "gestures": [],
            "scene_analysis": None,
            "activity_inference": None
        }
        
        # User context
        self.user = {
            "current_goal": None,
            "mood": "neutral",
            "energy_level": "normal",
            "focus_level": 0.0,
            "stress_level": 0.0
        }
        
        # System context
        self.system = {
            "time_of_day": None,
            "day_of_week": None,
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "network_status": "online",
            "running_processes": []
        }
        
        # Behavioral patterns
        self.patterns = {
            "common_tasks": [],
            "peak_hours": [],
            "preferences": {},
            "learned_workflows": []
        }
        
        # Raw context for debugging
        self._raw_updates: List[Dict[str, Any]] = []
    
    def update_voice_context(self, **kwargs):
        """Update voice/speech context"""
        self.voice.update(kwargs)
        self._log_update("voice", kwargs)
    
    def update_screen_context(self, **kwargs):
        """Update screen/activity context"""
        self.screen.update(kwargs)
        self._log_update("screen", kwargs)
    
    def update_vision_context(self, **kwargs):
        """Update vision/real-world context"""
        self.vision.update(kwargs)
        self._log_update("vision", kwargs)
    
    def update_memory_context(self, memories: List[Dict], knowledge: List[Dict]):
        """Update memory and knowledge context"""
        self.memory["recent_memories"] = memories
        self.memory["relevant_knowledge"] = knowledge
        self._log_update("memory", {"memories": len(memories), "knowledge": len(knowledge)})
    
    def update_integrations_context(self, **kwargs):
        """Update integrations context"""
        self.integrations.update(kwargs)
        self._log_update("integrations", kwargs)
    
    def update_orchestration_context(self, **kwargs):
        """Update orchestrator state"""
        self.orchestration.update(kwargs)
        self._log_update("orchestration", kwargs)
    
    def update_user_context(self, **kwargs):
        """Update user state"""
        self.user.update(kwargs)
        self._log_update("user", kwargs)
    
    def update_system_context(self, **kwargs):
        """Update system state"""
        self.system.update(kwargs)
        self._log_update("system", kwargs)
    
    def update_patterns(self, **kwargs):
        """Update behavioral patterns"""
        self.patterns.update(kwargs)
        self._log_update("patterns", kwargs)
    
    def _log_update(self, category: str, data: Dict[str, Any]):
        """Log context update for debugging"""
        self._raw_updates.append({
            "timestamp": datetime.now(),
            "category": category,
            "data": data
        })
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get value from context using dot notation
        Example: get("voice.sentiment") → returns sentiment value
        """
        parts = path.split(".")
        value = self.__dict__.get(parts[0])
        
        for part in parts[1:]:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default
        
        return value if value is not None else default
    
    def to_dict(self) -> Dict[str, Any]:
        """Return context as dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "voice": self.voice,
            "screen": self.screen,
            "orchestration": self.orchestration,
            "memory": self.memory,
            "integrations": self.integrations,
            "vision": self.vision,
            "user": self.user,
            "system": self.system,
            "patterns": self.patterns
        }
    
    def to_json(self) -> str:
        """Return context as JSON string"""
        return json.dumps(self.to_dict(), default=str, indent=2)
    
    def get_relevant_context(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get filtered context focused on specific areas
        Useful for passing to decision engine without bloat
        """
        if not focus_areas:
            return self.to_dict()
        
        result = {"timestamp": self.timestamp.isoformat()}
        
        area_map = {
            "voice": self.voice,
            "screen": self.screen,
            "orchestration": self.orchestration,
            "memory": self.memory,
            "integrations": self.integrations,
            "vision": self.vision,
            "user": self.user,
            "system": self.system,
            "patterns": self.patterns
        }
        
        for area in focus_areas:
            if area in area_map:
                result[area] = area_map[area]
        
        return result
    
    def summarize(self) -> str:
        """Create human-readable summary of context"""
        summary = []
        
        # User state
        summary.append(f"👤 User: {self.user['mood']} ({self.user['energy_level']} energy)")
        
        # Current activity
        if self.screen['active_window']:
            summary.append(f"💻 Active: {self.screen['active_window']}")
        
        # Current people
        if self.vision['detected_people']:
            people = ", ".join(self.vision['detected_people'])
            summary.append(f"👥 People: {people}")
        
        # Current emotion
        if self.vision['emotions']:
            emotions = ", ".join([str(e) for e in self.vision['emotions'][:2]])
            summary.append(f"🎭 Emotions: {emotions}")
        
        # Upcoming calendar
        if self.integrations['calendar_events']:
            next_event = self.integrations['calendar_events'][0]
            summary.append(f"📅 Next: {next_event}")
        
        # System status
        summary.append(f"⚙️ System: CPU {self.system['cpu_usage']:.1f}%, Memory {self.system['memory_usage']:.1f}%")
        
        # Time
        summary.append(f"🕐 Time: {self.system['time_of_day']}")
        
        return "\n".join(summary)


class ContextEngine:
    """
    Main context aggregation engine
    
    Pulls data from all JARVIS phases and creates unified context
    """
    
    def __init__(self):
        self.context = UnifiedContext()
        self.listeners: List[callable] = []
    
    async def update_from_phase_1(self, voice_data: Dict[str, Any]):
        """Update context from Phase 1 (Voice System)"""
        self.context.update_voice_context(**voice_data)
        await self._notify_listeners()
    
    async def update_from_phase_3(self, screen_data: Dict[str, Any]):
        """Update context from Phase 3 (Screen Vision)"""
        self.context.update_screen_context(**screen_data)
        await self._notify_listeners()
    
    async def update_from_phase_4(self, orchestrator_data: Dict[str, Any]):
        """Update context from Phase 4 (Orchestrator)"""
        self.context.update_orchestration_context(**orchestrator_data)
        await self._notify_listeners()
    
    async def update_from_phase_5(self, memory_data: Dict[str, Any]):
        """Update context from Phase 5 (Memory)"""
        memories = memory_data.get("recent_memories", [])
        knowledge = memory_data.get("knowledge", [])
        self.context.update_memory_context(memories, knowledge)
        await self._notify_listeners()
    
    async def update_from_phase_6(self, integrations_data: Dict[str, Any]):
        """Update context from Phase 6 (Integrations)"""
        self.context.update_integrations_context(**integrations_data)
        await self._notify_listeners()
    
    async def update_from_phase_7(self, vision_data: Dict[str, Any]):
        """Update context from Phase 7 (Vision)"""
        self.context.update_vision_context(**vision_data)
        await self._notify_listeners()
    
    async def update_user_state(self, mood: str, energy: str, focus: float, stress: float):
        """Update user state"""
        self.context.update_user_context(
            mood=mood,
            energy_level=energy,
            focus_level=focus,
            stress_level=stress
        )
        await self._notify_listeners()
    
    async def update_system_state(self, cpu: float, memory: float, processes: List[str]):
        """Update system state"""
        self.context.update_system_context(
            cpu_usage=cpu,
            memory_usage=memory,
            running_processes=processes,
            time_of_day=datetime.now().strftime("%H:%M")
        )
        await self._notify_listeners()
    
    def register_listener(self, callback: callable):
        """Register listener to be notified of context changes"""
        self.listeners.append(callback)
    
    async def _notify_listeners(self):
        """Notify all listeners of context update"""
        for listener in self.listeners:
            try:
                if hasattr(listener, "__await__"):
                    await listener()
                else:
                    listener()
            except Exception as e:
                print(f"Error notifying listener: {e}")
    
    def get_context_for_decision(self, decision_type: str) -> Dict[str, Any]:
        """Get filtered context relevant for a specific decision type"""
        
        decision_focus = {
            "schedule_task": ["user", "system", "integrations", "patterns"],
            "respond_to_user": ["user", "voice", "screen", "vision"],
            "automate_workflow": ["orchestration", "integrations", "memory", "patterns"],
            "monitor_system": ["system", "screen", "vision"],
            "learn_pattern": ["user", "patterns", "orchestration", "integrations"]
        }
        
        focus = decision_focus.get(decision_type)
        return self.context.get_relevant_context(focus)
    
    def get_summary(self) -> str:
        """Get human-readable context summary"""
        return self.context.summarize()
