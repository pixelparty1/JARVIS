"""
Base Integration Classes

Provides infrastructure for all third-party integrations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import asyncio


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


class AuthError(IntegrationError):
    """Authentication error."""
    pass


class ServiceError(IntegrationError):
    """Service connection error."""
    pass


@dataclass
class ToolDefinition:
    """Definition of a tool provided by an integration."""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: str
    category: str = "general"


class BaseIntegration(ABC):
    """
    Base class for all integrations.
    
    Provides:
    - Authentication management
    - Tool registry
    - Error handling
    - Health checking
    """
    
    def __init__(self, name: str, auth_manager=None):
        """
        Initialize integration.
        
        Args:
            name: Integration name
            auth_manager: AuthManager instance
        """
        self.name = name
        self.auth_manager = auth_manager
        self.is_authenticated = False
        self.tools: Dict[str, ToolDefinition] = {}
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'last_error': None
        }
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if service is accessible."""
        pass
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool provided by this integration."""
        self.tools[tool.name] = tool
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get all tools provided by this integration."""
        return list(self.tools.values())
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a specific tool definition."""
        return self.tools.get(name)
    
    async def _execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of the tool
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        self.stats['total_calls'] += 1
        
        try:
            if not self.is_authenticated:
                raise AuthError(f"{self.name} not authenticated")
            
            result = await self._call_tool(tool_name, **kwargs)
            self.stats['successful_calls'] += 1
            return result
            
        except Exception as e:
            self.stats['failed_calls'] += 1
            self.stats['last_error'] = str(e)
            raise
    
    @abstractmethod
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Implementation of tool execution."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        return {
            **self.stats,
            'authenticated': self.is_authenticated,
            'tools_available': len(self.tools)
        }


class Integration(BaseIntegration):
    """Base integration for simple services."""
    
    def __init__(self, name: str, base_url: str = None, auth_manager=None):
        """
        Initialize simple integration.
        
        Args:
            name: Service name
            base_url: API base URL
            auth_manager: AuthManager instance
        """
        super().__init__(name, auth_manager)
        self.base_url = base_url
        self.session = None
    
    async def authenticate(self) -> bool:
        """Default authentication (override in subclasses)."""
        self.is_authenticated = True
        return True
    
    async def health_check(self) -> bool:
        """Check service health."""
        try:
            if self.base_url:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.base_url, timeout=5) as resp:
                        return resp.status < 500
            return self.is_authenticated
        except:
            return False
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Default implementation."""
        raise NotImplementedError(f"Tool {tool_name} not implemented")


class EventBus:
    """Central event dispatcher for integrations."""
    
    def __init__(self):
        self.listeners: Dict[str, List[callable]] = {}
        self.history: List[Dict[str, Any]] = []
    
    def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to an event."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(handler)
    
    async def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event."""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.history.append(event)
        
        if event_type in self.listeners:
            tasks = []
            for handler in self.listeners[event_type]:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get event history."""
        if event_type:
            return [e for e in self.history if e['type'] == event_type][-limit:]
        return self.history[-limit:]


# Global event bus
event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus."""
    return event_bus
