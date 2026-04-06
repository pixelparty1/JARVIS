"""
Events Integration - Event-Driven Triggers

Features:
- Real-time event monitoring
- Trigger-action patterns
- Auto-workflows on events
- Event filtering and routing
- Event history
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from .base import Integration, ToolDefinition, IntegrationError, EventBus


class EventType(Enum):
    """Event types."""
    EMAIL_RECEIVED = "email.received"
    EMAIL_READ = "email.read"
    CALENDAR_EVENT = "calendar.event_created"
    CALENDAR_REMINDER = "calendar.reminder"
    GITHUB_PR_CREATED = "github.pr_created"
    GITHUB_ISSUE_CREATED = "github.issue_created"
    SLACK_MESSAGE = "slack.message"
    DEVICE_STATE_CHANGE = "device.state_changed"
    DEVICE_OFFLINE = "device.offline"


class TriggerCondition(Enum):
    """Trigger condition types."""
    EQUALS = "equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    ANY = "any"


@dataclass
class Event:
    """System event."""
    id: str
    type: EventType
    source: str  # email, calendar, github, etc.
    timestamp: str = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Condition:
    """Event condition."""
    field: str  # Path to field in event data (e.g., "data.sender")
    operator: TriggerCondition
    value: Any
    
    def matches(self, event: Event) -> bool:
        """Check if condition matches event."""
        # Get field value from event
        try:
            parts = self.field.split(".")
            obj = event
            for part in parts:
                obj = getattr(obj, part)
            event_value = obj
        except (AttributeError, KeyError):
            return False
        
        if self.operator == TriggerCondition.EQUALS:
            return event_value == self.value
        elif self.operator == TriggerCondition.CONTAINS:
            return str(self.value).lower() in str(event_value).lower()
        elif self.operator == TriggerCondition.GREATER_THAN:
            try:
                return float(event_value) > float(self.value)
            except:
                return False
        elif self.operator == TriggerCondition.LESS_THAN:
            try:
                return float(event_value) < float(self.value)
            except:
                return False
        elif self.operator == TriggerCondition.IN:
            return event_value in self.value
        elif self.operator == TriggerCondition.NOT_IN:
            return event_value not in self.value
        elif self.operator == TriggerCondition.ANY:
            return True
        
        return False


@dataclass
class Trigger:
    """Event trigger."""
    id: str
    name: str
    event_type: EventType
    conditions: List[Condition]
    action: str  # Workflow name or action
    active: bool = True
    runs: int = 0
    last_triggered: str = None
    
    def matches(self, event: Event) -> bool:
        """Check if trigger should fire."""
        if not self.active or event.type != self.event_type:
            return False
        
        # All conditions must match
        for condition in self.conditions:
            if not condition.matches(event):
                return False
        
        return True
    
    def fire(self) -> None:
        """Record trigger fire."""
        self.runs += 1
        self.last_triggered = datetime.now().isoformat()


@dataclass
class Automation:
    """Full automation rule."""
    id: str
    name: str
    trigger: Trigger
    actions: List[str]  # List of actions/tools to execute
    enabled: bool = True
    executions: int = 0
    last_execution: str = None
    
    async def execute(self) -> bool:
        """Execute automation."""
        self.executions += 1
        self.last_execution = datetime.now().isoformat()
        print(f"⚡ Automation executed: {self.name}")
        return True


class EventsIntegration(Integration):
    """
    Events integration for trigger-based automation.
    
    Monitors events across integrations and executes automated workflows.
    """
    
    def __init__(self, auth_manager=None, event_bus: EventBus = None):
        """
        Initialize events integration.
        
        Args:
            auth_manager: AuthManager instance
            event_bus: EventBus instance
        """
        super().__init__("events", auth_manager=auth_manager)
        self.event_bus = event_bus or EventBus()
        self.triggers = {}
        self.automations = {}
        self.event_history = []
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="create_trigger",
            description="Create an event trigger",
            parameters={"trigger_name": str, "event_type": str, "conditions": list},
            returns="Trigger",
            category="events"
        ))
        
        self.register_tool(ToolDefinition(
            name="create_automation",
            description="Create an automation rule",
            parameters={"automation_name": str, "trigger_id": str, "actions": list},
            returns="Automation",
            category="events"
        ))
        
        self.register_tool(ToolDefinition(
            name="list_triggers",
            description="List all triggers",
            parameters={},
            returns="List[Trigger]",
            category="events"
        ))
        
        self.register_tool(ToolDefinition(
            name="get_automation",
            description="Get automation details",
            parameters={"automation_id": str},
            returns="Automation",
            category="events"
        ))
        
        self.register_tool(ToolDefinition(
            name="emit_event",
            description="Emit an event",
            parameters={"event_type": str, "source": str, "data": dict},
            returns="Event",
            category="events"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate events integration."""
        self.is_authenticated = True
        return True
    
    async def health_check(self) -> bool:
        """Health check."""
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "create_trigger":
            return await self.create_trigger(
                trigger_name=kwargs.get("trigger_name"),
                event_type=kwargs.get("event_type"),
                conditions=kwargs.get("conditions", [])
            )
        elif tool_name == "create_automation":
            return await self.create_automation(
                automation_name=kwargs.get("automation_name"),
                trigger_id=kwargs.get("trigger_id"),
                actions=kwargs.get("actions", [])
            )
        elif tool_name == "list_triggers":
            return await self.list_triggers()
        elif tool_name == "get_automation":
            return await self.get_automation(automation_id=kwargs.get("automation_id"))
        elif tool_name == "emit_event":
            return await self.emit_event(
                event_type=kwargs.get("event_type"),
                source=kwargs.get("source"),
                data=kwargs.get("data", {})
            )
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    async def create_trigger(self, trigger_name: str, event_type: str,
                            conditions: List[Dict[str, Any]] = None) -> Trigger:
        """
        Create an event trigger.
        
        Args:
            trigger_name: Trigger name
            event_type: Event type to monitor
            conditions: List of conditions
            
        Returns:
            Trigger instance
        """
        trigger_id = f"trigger_{len(self.triggers) + 1}"
        
        cond_objs = []
        if conditions:
            for cond in conditions:
                cond_objs.append(Condition(
                    field=cond.get("field"),
                    operator=TriggerCondition[cond.get("operator", "ANY")],
                    value=cond.get("value")
                ))
        
        trigger = Trigger(
            id=trigger_id,
            name=trigger_name,
            event_type=EventType[event_type],
            conditions=cond_objs,
            action=trigger_name
        )
        
        self.triggers[trigger_id] = trigger
        print(f"✅ Trigger created: {trigger_name}")
        
        return trigger
    
    async def create_automation(self, automation_name: str, trigger_id: str,
                               actions: List[str] = None) -> Automation:
        """
        Create an automation rule.
        
        Args:
            automation_name: Automation name
            trigger_id: Associated trigger ID
            actions: List of actions to execute
            
        Returns:
            Automation instance
        """
        if trigger_id not in self.triggers:
            raise IntegrationError(f"Trigger not found: {trigger_id}")
        
        automation_id = f"auto_{len(self.automations) + 1}"
        trigger = self.triggers[trigger_id]
        
        automation = Automation(
            id=automation_id,
            name=automation_name,
            trigger=trigger,
            actions=actions or []
        )
        
        self.automations[automation_id] = automation
        print(f"✅ Automation created: {automation_name}")
        
        return automation
    
    async def list_triggers(self) -> List[Trigger]:
        """List all triggers."""
        return list(self.triggers.values())
    
    async def get_automation(self, automation_id: str) -> Optional[Automation]:
        """Get automation details."""
        return self.automations.get(automation_id)
    
    async def emit_event(self, event_type: str, source: str,
                        data: Dict[str, Any] = None) -> Event:
        """
        Emit an event.
        
        Args:
            event_type: Event type
            source: Event source
            data: Event data
            
        Returns:
            Event instance
        """
        event_id = f"event_{len(self.event_history) + 1}"
        
        event = Event(
            id=event_id,
            type=EventType[event_type],
            source=source,
            data=data or {}
        )
        
        self.event_history.append(event)
        
        # Broadcast via event bus
        self.event_bus.emit(event_type, event)
        
        # Check triggers
        await self._check_triggers(event)
        
        print(f"📤 Event emitted: {event_type} from {source}")
        
        return event
    
    async def _check_triggers(self, event: Event) -> None:
        """
        Check if event triggers any automations.
        
        Args:
            event: Event to check
        """
        for automation in self.automations.values():
            if not automation.enabled:
                continue
            
            if automation.trigger.matches(event):
                automation.trigger.fire()
                await automation.execute()
                
                # Execute actions
                for action in automation.actions:
                    print(f"  → Executing action: {action}")
    
    def get_event_history(self, limit: int = 50) -> List[Event]:
        """Get event history."""
        return self.event_history[-limit:]
    
    def get_trigger_stats(self) -> Dict[str, Any]:
        """Get trigger statistics."""
        return {
            "total_triggers": len(self.triggers),
            "active_triggers": sum(1 for t in self.triggers.values() if t.active),
            "total_automations": len(self.automations),
            "enabled_automations": sum(1 for a in self.automations.values() if a.enabled),
            "total_events": len(self.event_history),
        }


class EventSystemBuilder:
    """Helper to build event automation systems."""
    
    def __init__(self, events_integration: EventsIntegration):
        """
        Initialize builder.
        
        Args:
            events_integration: EventsIntegration instance
        """
        self.events = events_integration
    
    async def setup_email_automation(self) -> None:
        """Setup email event automation."""
        # Trigger: Email from important contacts
        trigger = await self.events.create_trigger(
            trigger_name="important_email",
            event_type="EMAIL_RECEIVED",
            conditions=[
                {"field": "data.priority", "operator": "equals", "value": "high"}
            ]
        )
        
        # Automation: Send Slack notification
        auto = await self.events.create_automation(
            automation_name="notify_important_email",
            trigger_id=trigger.id,
            actions=["slack.notify", "calendar.reminder"]
        )
        
        print("✅ Email automation configured")
    
    async def setup_github_automation(self) -> None:
        """Setup GitHub event automation."""
        # Trigger: PR created
        trigger = await self.events.create_trigger(
            trigger_name="pr_created",
            event_type="GITHUB_PR_CREATED",
            conditions=[{"field": "data.draft", "operator": "equals", "value": False}]
        )
        
        # Automation: Create Notion task
        auto = await self.events.create_automation(
            automation_name="track_pr_in_notion",
            trigger_id=trigger.id,
            actions=["notion.create_page", "slack.notify"]
        )
        
        print("✅ GitHub automation configured")
    
    async def setup_device_automation(self) -> None:
        """Setup device event automation."""
        # Trigger: Device offline
        trigger = await self.events.create_trigger(
            trigger_name="device_offline",
            event_type="DEVICE_OFFLINE",
            conditions=[]
        )
        
        # Automation: Alert
        auto = await self.events.create_automation(
            automation_name="alert_device_offline",
            trigger_id=trigger.id,
            actions=["slack.notify", "email.send"]
        )
        
        print("✅ Device automation configured")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_events():
        print("🧪 Events Integration Test\n")
        
        events = EventsIntegration()
        await events.authenticate()
        
        # Create trigger
        trigger = await events.create_trigger(
            trigger_name="high_priority_email",
            event_type="EMAIL_RECEIVED",
            conditions=[
                {"field": "data.priority", "operator": "equals", "value": "high"}
            ]
        )
        
        # Create automation
        automation = await events.create_automation(
            automation_name="notify_important",
            trigger_id=trigger.id,
            actions=["slack.notify"]
        )
        
        print(f"\n✅ Created automation: {automation.name}")
        print(f"   Trigger: {automation.trigger.name}")
        print(f"   Actions: {', '.join(automation.actions)}")
        
        # Emit event
        print(f"\nEmitting test event...")
        event = await events.emit_event(
            event_type="EMAIL_RECEIVED",
            source="gmail",
            data={"priority": "high", "sender": "boss@company.com"}
        )
        
        print(f"\n📊 Event System Stats:")
        stats = events.get_trigger_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    asyncio.run(test_events())
