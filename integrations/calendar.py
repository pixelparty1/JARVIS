"""
Calendar Integration - Google Calendar / Outlook

Features:
- View events
- Create events
- Smart scheduling
- Find free slots
- Auto-schedule meetings
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .base import Integration, ToolDefinition, IntegrationError


@dataclass
class CalendarEvent:
    """Calendar event."""
    id: str
    title: str
    start_time: str  # ISO format
    end_time: str
    description: str = ""
    location: str = ""
    attendees: List[str] = None
    calendar: str = "primary"
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
    
    def duration_minutes(self) -> int:
        """Get event duration in minutes."""
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return int((end - start).total_seconds() / 60)
    
    def is_busy(self) -> bool:
        """Check if event is a busy time."""
        return self.title.lower() not in ["free", "available", "focus time"]


class CalendarIntegration(Integration):
    """
    Calendar service integration.
    
    Supports: Google Calendar, Outlook Calendar (via mock API)
    """
    
    def __init__(self, auth_manager=None, provider: str = "google"):
        """
        Initialize calendar integration.
        
        Args:
            auth_manager: AuthManager instance
            provider: "google" or "outlook"
        """
        super().__init__(f"calendar_{provider}", auth_manager=auth_manager)
        self.provider = provider
        self.mock_events = []
        self.timezone = "UTC"
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="get_events",
            description="Get calendar events in date range",
            parameters={"start_date": str, "end_date": str, "limit": int},
            returns="List[CalendarEvent]",
            category="calendar"
        ))
        
        self.register_tool(ToolDefinition(
            name="find_free_slot",
            description="Find free time slot for a meeting",
            parameters={"duration_minutes": int, "date": str, "start_hour": int, "end_hour": int},
            returns="Tuple[str, str]",  # (start_time, end_time)
            category="calendar"
        ))
        
        self.register_tool(ToolDefinition(
            name="create_event",
            description="Create a new calendar event",
            parameters={"title": str, "start_time": str, "end_time": str, "description": str, "location": str, "attendees": list},
            returns="str",  # event_id
            category="calendar"
        ))
        
        self.register_tool(ToolDefinition(
            name="modify_event",
            description="Modify existing event",
            parameters={"event_id": str, "title": str, "start_time": str, "end_time": str},
            returns="bool",
            category="calendar"
        ))
        
        self.register_tool(ToolDefinition(
            name="delete_event",
            description="Delete an event",
            parameters={"event_id": str},
            returns="bool",
            category="calendar"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate with calendar service."""
        if not self.auth_manager:
            self.is_authenticated = True
            return True
        
        cred = self.auth_manager.get_credentials(self.provider)
        if cred:
            self.is_authenticated = True
            return True
        
        return False
    
    async def health_check(self) -> bool:
        """Check calendar service health."""
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "get_events":
            return await self.get_events(
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                limit=kwargs.get("limit", 50)
            )
        elif tool_name == "find_free_slot":
            return await self.find_free_slot(
                duration_minutes=kwargs.get("duration_minutes", 30),
                date=kwargs.get("date"),
                start_hour=kwargs.get("start_hour", 9),
                end_hour=kwargs.get("end_hour", 17)
            )
        elif tool_name == "create_event":
            return await self.create_event(
                title=kwargs.get("title"),
                start_time=kwargs.get("start_time"),
                end_time=kwargs.get("end_time"),
                description=kwargs.get("description", ""),
                location=kwargs.get("location", ""),
                attendees=kwargs.get("attendees", [])
            )
        elif tool_name == "modify_event":
            return await self.modify_event(
                event_id=kwargs.get("event_id"),
                title=kwargs.get("title"),
                start_time=kwargs.get("start_time"),
                end_time=kwargs.get("end_time")
            )
        elif tool_name == "delete_event":
            return await self.delete_event(event_id=kwargs.get("event_id"))
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    async def get_events(self, start_date: str, end_date: str,
                        limit: int = 50) -> List[CalendarEvent]:
        """
        Get calendar events in date range.
        
        Args:
            start_date: ISO format start date
            end_date: ISO format end date
            limit: Max events to return
            
        Returns:
            List of events
        """
        events = self._get_mock_events()
        
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        filtered = []
        for event in events:
            event_start = datetime.fromisoformat(event.start_time)
            if start <= event_start < end:
                filtered.append(event)
        
        return filtered[:limit]
    
    async def find_free_slot(self, duration_minutes: int = 30,
                            date: str = None,
                            start_hour: int = 9,
                            end_hour: int = 17) -> Optional[Tuple[str, str]]:
        """
        Find a free time slot.
        
        Args:
            duration_minutes: Meeting length
            date: Date to search (YYYY-MM-DD)
            start_hour: Work day start
            end_hour: Work day end
            
        Returns:
            (start_time, end_time) tuple or None
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get events for the day
        start_date = f"{date}T00:00:00"
        end_date = f"{date}T23:59:59"
        
        events = await self.get_events(start_date, end_date)
        
        # Sort events by start time
        events.sort(key=lambda e: e.start_time)
        
        # Find first free slot
        current_time = datetime.fromisoformat(f"{date}T{start_hour:02d}:00:00")
        end_time_limit = datetime.fromisoformat(f"{date}T{end_hour:02d}:00:00")
        
        for event in events:
            event_start = datetime.fromisoformat(event.start_time)
            
            # Check if slot before event is free
            if event_start - current_time >= timedelta(minutes=duration_minutes):
                slot_end = current_time + timedelta(minutes=duration_minutes)
                return (current_time.isoformat(), slot_end.isoformat())
            
            # Move past this event
            event_end = datetime.fromisoformat(event.end_time)
            current_time = max(current_time, event_end)
        
        # Check if time after last event is available
        if end_time_limit - current_time >= timedelta(minutes=duration_minutes):
            slot_end = current_time + timedelta(minutes=duration_minutes)
            return (current_time.isoformat(), slot_end.isoformat())
        
        return None
    
    async def create_event(self, title: str, start_time: str,
                          end_time: str, description: str = "",
                          location: str = "",
                          attendees: List[str] = None) -> str:
        """
        Create a calendar event.
        
        Args:
            title: Event title
            start_time: ISO format start
            end_time: ISO format end
            description: Event description
            location: Event location
            attendees: List of attendee emails
            
        Returns:
            Event ID
        """
        if attendees is None:
            attendees = []
        
        event_id = f"evt_{len(self._get_mock_events())}"
        
        event = CalendarEvent(
            id=event_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees
        )
        
        self.mock_events.append(event)
        
        print(f"✅ Event created: {title}")
        return event_id
    
    async def modify_event(self, event_id: str,
                          title: str = None,
                          start_time: str = None,
                          end_time: str = None) -> bool:
        """Modify an existing event."""
        event = next((e for e in self.mock_events if e.id == event_id), None)
        if not event:
            return False
        
        if title:
            event.title = title
        if start_time:
            event.start_time = start_time
        if end_time:
            event.end_time = end_time
        
        return True
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event."""
        self.mock_events = [e for e in self.mock_events if e.id != event_id]
        return True
    
    def _get_mock_events(self) -> List[CalendarEvent]:
        """Get mock events for testing."""
        if self.mock_events:
            return self.mock_events
        
        now = datetime.now()
        
        self.mock_events = [
            CalendarEvent(
                id="1",
                title="Team Standup",
                start_time=(now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).isoformat(),
                end_time=(now + timedelta(hours=1, minutes=30)).replace(minute=0, second=0, microsecond=0).isoformat(),
                description="Daily standup",
                location="Zoom"
            ),
            CalendarEvent(
                id="2",
                title="Project Meeting",
                start_time=(now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0).isoformat(),
                end_time=(now + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0).isoformat(),
                description="Discuss Q2 roadmap",
                location="Conference Room A",
                attendees=["manager@company.com", "team@company.com"]
            ),
            CalendarEvent(
                id="3",
                title="Focus Time",
                start_time=(now + timedelta(hours=4)).replace(minute=0, second=0, microsecond=0).isoformat(),
                end_time=(now + timedelta(hours=6)).replace(minute=0, second=0, microsecond=0).isoformat(),
                description="Deep work session"
            ),
        ]
        
        return self.mock_events


class CalendarAssistant:
    """High-level calendar assistant."""
    
    def __init__(self, calendar_integration: CalendarIntegration):
        """
        Initialize calendar assistant.
        
        Args:
            calendar_integration: CalendarIntegration instance
        """
        self.calendar = calendar_integration
    
    async def today_schedule(self) -> str:
        """Get today's schedule."""
        now = datetime.now()
        start_date = now.replace(hour=0, minute=0, second=0).isoformat()
        end_date = now.replace(hour=23, minute=59, second=59).isoformat()
        
        events = await self.calendar.get_events(start_date, end_date)
        
        schedule = "📅 Today's Schedule:\n\n"
        
        if not events:
            return schedule + "No events scheduled."
        
        for event in events:
            start = datetime.fromisoformat(event.start_time)
            end = datetime.fromisoformat(event.end_time)
            
            schedule += f"• {start.strftime('%H:%M')} - {end.strftime('%H:%M')}: {event.title}\n"
            if event.location:
                schedule += f"  📍 {event.location}\n"
        
        return schedule
    
    async def schedule_meeting(self, title: str, duration_minutes: int = 30,
                              date: str = None) -> str:
        """
        Find free time and schedule meeting.
        
        Args:
            title: Meeting title
            duration_minutes: Meeting duration
            date: Target date
            
        Returns:
            Confirmation or error message
        """
        slot = await self.calendar.find_free_slot(
            duration_minutes=duration_minutes,
            date=date
        )
        
        if not slot:
            return "❌ No free time slots available."
        
        start_time, end_time = slot
        event_id = await self.calendar.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time
        )
        
        start = datetime.fromisoformat(start_time)
        return f"✅ Meeting scheduled: {title}\n   Time: {start.strftime('%Y-%m-%d %H:%M')}"


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_calendar():
        print("🧪 Calendar Integration Test\n")
        
        calendar = CalendarIntegration(provider="google")
        await calendar.authenticate()
        
        # Get today's events
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0).isoformat()
        end = now.replace(hour=23, minute=59, second=59).isoformat()
        
        events = await calendar.get_events(start, end)
        print(f"✅ Found {len(events)} events today\n")
        
        # Find free slot
        slot = await calendar.find_free_slot(duration_minutes=30)
        if slot:
            start_time, end_time = slot
            start_dt = datetime.fromisoformat(start_time)
            print(f"✅ Free slot found: {start_dt.strftime('%H:%M')} - {datetime.fromisoformat(end_time).strftime('%H:%M')}")
    
    asyncio.run(test_calendar())
