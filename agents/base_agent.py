"""
Base Agent Class for JARVIS Multi-Agent System

All specialized agents inherit from this base class.
Provides common interface and communication patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time
import json


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender_id: str
    recipient_id: str
    message_type: str  # "query", "command", "result", "broadcast"
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    priority: int = 5  # 1-10, higher = more important


@dataclass
class AgentState:
    """State of an agent."""
    agent_id: str
    status: str  # "idle", "busy", "error", "learning"
    last_activity: float
    tasks_completed: int = 0
    tasks_failed: int = 0
    performance_score: float = 1.0  # 0-1.0


class SharedMemory:
    """
    Shared memory for agent communication.
    Thread-safe key-value store for inter-agent data.
    """
    
    def __init__(self):
        """Initialize shared memory."""
        self.data = {}
        self.message_queue = []
        self.access_log = []
        self.update_callbacks = {}
    
    def set(self, key: str, value: Any, agent_id: str = "system"):
        """Set value in shared memory."""
        self.data[key] = {
            'value': value,
            'timestamp': time.time(),
            'updated_by': agent_id
        }
        self._log_access("WRITE", key, agent_id)
        self._trigger_callbacks(key, value)
    
    def get(self, key: str, agent_id: str = "system") -> Optional[Any]:
        """Get value from shared memory."""
        self._log_access("READ", key, agent_id)
        if key in self.data:
            return self.data[key]['value']
        return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self.data
    
    def delete(self, key: str, agent_id: str = "system"):
        """Delete from shared memory."""
        if key in self.data:
            del self.data[key]
            self._log_access("DELETE", key, agent_id)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all data."""
        return {k: v['value'] for k, v in self.data.items()}
    
    def broadcast_message(self, message: AgentMessage):
        """Broadcast message to agents."""
        self.message_queue.append(message)
    
    def get_messages(self, recipient_id: str) -> List[AgentMessage]:
        """Get messages for specific recipient."""
        messages = [m for m in self.message_queue if m.recipient_id == recipient_id]
        # Remove retrieved messages
        for m in messages:
            self.message_queue.remove(m)
        return messages
    
    def on_update(self, key: str, callback: Callable):
        """Register callback for key updates."""
        if key not in self.update_callbacks:
            self.update_callbacks[key] = []
        self.update_callbacks[key].append(callback)
    
    def _trigger_callbacks(self, key: str, value: Any):
        """Trigger registered callbacks."""
        if key in self.update_callbacks:
            for callback in self.update_callbacks[key]:
                try:
                    callback(value)
                except Exception as e:
                    print(f"⚠️  Callback error: {e}")
    
    def _log_access(self, operation: str, key: str, agent_id: str):
        """Log memory access."""
        self.access_log.append({
            'operation': operation,
            'key': key,
            'agent_id': agent_id,
            'timestamp': time.time()
        })
        
        # Keep log size manageable
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-500:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            'total_keys': len(self.data),
            'queue_size': len(self.message_queue),
            'log_size': len(self.access_log),
            'data_size_bytes': len(json.dumps(self.data))
        }


# Global shared memory instance
_shared_memory = SharedMemory()


def get_shared_memory() -> SharedMemory:
    """Get global shared memory instance."""
    return _shared_memory


class BaseAgent(ABC):
    """
    Base class for all agents in JARVIS systems.
    
    Properties:
    - Clear responsibilities
    - Shared memory communication
    - Performance tracking
    - Error handling
    """
    
    def __init__(self, agent_id: str, agent_type: str, brain=None):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier
            agent_type: Type of agent (planner, executor, etc.)
            brain: Optional Brain instance for Groq API
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.brain = brain
        self.shared_memory = get_shared_memory()
        
        # State tracking
        self.state = AgentState(
            agent_id=agent_id,
            status="idle",
            last_activity=time.time()
        )
        
        # Performance metrics
        self.metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'avg_execution_time': 0,
            'success_rate': 1.0,
            'last_error': None
        }
        
        # Configuration
        self.config = {
            'timeout': 30.0,
            'retry_count': 2,
            'debug': False
        }
        
        print(f"✅ Agent {agent_id} ({agent_type}) initialized")
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's primary task.
        Must be implemented by subclass.
        
        Args:
            task: Task specification
            
        Returns:
            Task result
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        pass
    
    def send_message(self, recipient_id: str, message_type: str, 
                    content: Dict[str, Any], priority: int = 5):
        """
        Send message to another agent.
        
        Args:
            recipient_id: Target agent ID
            message_type: Type of message
            content: Message content
            priority: Priority level (1-10)
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            priority=priority
        )
        self.shared_memory.broadcast_message(message)
        
        if self.config['debug']:
            print(f"📤 {self.agent_id} → {recipient_id}: {message_type}")
    
    def receive_messages(self) -> List[AgentMessage]:
        """Receive messages for this agent."""
        return self.shared_memory.get_messages(self.agent_id)
    
    def update_state(self, status: str):
        """Update agent state."""
        self.state.status = status
        self.state.last_activity = time.time()
    
    def record_success(self, execution_time: float):
        """Record successful task execution."""
        self.metrics['tasks_completed'] += 1
        
        # Update average execution time
        total = self.metrics['tasks_completed']
        old_avg = self.metrics['avg_execution_time']
        self.metrics['avg_execution_time'] = (
            (old_avg * (total - 1) + execution_time) / total
        )
        
        # Update success rate
        total_tasks = (self.metrics['tasks_completed'] + 
                      self.metrics['tasks_failed'])
        if total_tasks > 0:
            self.metrics['success_rate'] = (
                self.metrics['tasks_completed'] / total_tasks
            )
    
    def record_failure(self, error: str):
        """Record failed task execution."""
        self.metrics['tasks_failed'] += 1
        self.metrics['last_error'] = error
        
        # Update success rate
        total_tasks = (self.metrics['tasks_completed'] + 
                      self.metrics['tasks_failed'])
        if total_tasks > 0:
            self.metrics['success_rate'] = (
                self.metrics['tasks_completed'] / total_tasks
            )
    
    def query_shared_memory(self, key: str) -> Optional[Any]:
        """Query shared memory."""
        return self.shared_memory.get(key, self.agent_id)
    
    def update_shared_memory(self, key: str, value: Any):
        """Update shared memory."""
        self.shared_memory.set(key, value, self.agent_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            'agent_id': self.agent_id,
            'type': self.agent_type,
            'status': self.state.status,
            'metrics': self.metrics,
            'last_activity': datetime.fromtimestamp(self.state.last_activity)
        }
    
    def config_set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
    
    def config_get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with agent context."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.agent_id}: {message}")
    
    def think(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Use Groq to think through problem.
        
        Args:
            prompt: Thinking prompt
            temperature: Creativity level
            
        Returns:
            AI reasoning
        """
        if not self.brain:
            return None
        
        try:
            response = self.brain.ask_groq(prompt, temperature=temperature)
            return response
        except Exception as e:
            self.log(f"❌ Thinking error: {e}")
            return None


# Example usage
if __name__ == "__main__":
    print("🤖 Base Agent Framework Test")
    
    # Test shared memory
    memory = get_shared_memory()
    
    print("\n💾 Shared Memory Test:")
    memory.set("user_context", {"action": "coding"}, "agent1")
    print(f"   Stored: {memory.get('user_context')}")
    
    message = AgentMessage(
        sender_id="agent1",
        recipient_id="agent2",
        message_type="query",
        content={"question": "What should I do?"}
    )
    memory.broadcast_message(message)
    
    messages = memory.get_messages("agent2")
    print(f"   Messages for agent2: {len(messages)}")
    
    print("\n📊 Memory Stats:")
    stats = memory.get_stats()
    for key, val in stats.items():
        print(f"   {key}: {val}")
