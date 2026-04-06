"""
Core types and enums for JARVIS AI OS
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 1      # Immediate action required
    HIGH = 2          # Important, do soon
    NORMAL = 3        # Regular priority
    LOW = 4           # Can wait
    BACKGROUND = 5    # Run when free


class AgentType(Enum):
    """Types of agents in the system"""
    RESEARCH = "research"
    CODING = "coding"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"
    ASSISTANT = "assistant"
    CUSTOM = "custom"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SystemMode(Enum):
    """System operation mode"""
    INTERACTIVE = "interactive"      # Ask before acting
    AUTONOMOUS = "autonomous"        # Act without asking
    SUPERVISED = "supervised"        # Ask for critical actions
    LEARNING = "learning"            # Learn from user behavior


class InputType(Enum):
    """Types of user input"""
    VOICE = "voice"
    TEXT = "text"
    GESTURE = "gesture"
    NONE = "none"


@dataclass
class Task:
    """Represents a task to be executed"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: Priority = Priority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    agent_type: Optional[AgentType] = None
    workflow_id: Optional[str] = None
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    requires_user_input: bool = False
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Results
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Scheduling
    should_repeat: bool = False
    repeat_interval: Optional[int] = None  # seconds
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def duration(self) -> Optional[float]:
        """Returns execution duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def is_overdue(self) -> bool:
        """Check if task is past deadline"""
        if self.deadline:
            return self.status != TaskStatus.COMPLETED and datetime.now() > self.deadline
        return False


@dataclass
class Decision:
    """Represents a decision made by the system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: str = ""
    priority: Priority = Priority.NORMAL
    confidence: float = 0.0  # 0-1
    reasoning: str = ""
    
    # Required context
    requires_context: List[str] = field(default_factory=list)
    
    # Execution details
    task: Optional[Task] = None
    agent_type: Optional[AgentType] = None
    
    # User interaction
    requires_approval: bool = False
    can_defer: bool = True
    
    # Scheduling
    execute_at: Optional[datetime] = None
    urgency: int = 0  # 0-10 scale
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        """Compare decisions by priority and confidence"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.confidence < other.confidence


@dataclass
class WorkflowState:
    """State of a workflow execution"""
    workflow_id: str
    current_step: int = 0
    total_steps: int = 0
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Progress
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    
    # Results
    results: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def progress(self) -> float:
        """Return progress 0-1"""
        if self.total_steps == 0:
            return 0.0
        return self.current_step / self.total_steps


@dataclass
class SystemState:
    """Overall state of the JARVIS system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Mode
    mode: SystemMode = SystemMode.INTERACTIVE
    
    # Resources
    cpu_usage: float = 0.0      # 0-100
    memory_usage: float = 0.0   # 0-100
    running_tasks: int = 0
    
    # Active workflows
    active_workflows: List[str] = field(default_factory=list)
    
    # Queued decisions
    pending_decisions: List[Decision] = field(default_factory=list)
    
    # Context
    current_context: Optional[Dict[str, Any]] = None
    
    # Logging
    last_action: Optional[str] = None
    last_error: Optional[str] = None
    
    # Timestamps
    initialized_at: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    
    def is_busy(self) -> bool:
        """Check if system is at capacity"""
        return self.running_tasks > 5 or self.cpu_usage > 80
    
    def can_accept_task(self) -> bool:
        """Check if system can accept a new task"""
        return not self.is_busy() and self.cpu_usage < 70


@dataclass
class AgentCapability:
    """Represents what an agent can do"""
    name: str
    description: str
    tools: List[str] = field(default_factory=list)
    required_context: List[str] = field(default_factory=list)
    success_rate: float = 0.0  # Historical success rate


@dataclass
class WorkflowContext:
    """Context passed through a workflow"""
    workflow_id: str
    step_index: int
    task: Task
    
    # Data from previous steps
    results: Dict[str, Any] = field(default_factory=dict)
    
    # Shared context
    shared_state: Dict[str, Any] = field(default_factory=dict)
    
    # System state
    system_state: Optional[SystemState] = None
    
    def get_result(self, key: str, default: Any = None) -> Any:
        """Get result from previous workflow step"""
        return self.results.get(key, default)
    
    def set_result(self, key: str, value: Any):
        """Set result for next workflow step"""
        self.results[key] = value


# Callback types
TaskCallback = Callable[[Task], Awaitable[None]]
DecisionCallback = Callable[[Decision], Awaitable[None]]
ContextUpdateCallback = Callable[[Dict[str, Any]], Awaitable[None]]
AgentStatusCallback = Callable[[str, str], Awaitable[None]]
