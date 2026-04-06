"""
JARVIS Integrations - Ecosystem Controller (Phase 6)

Complete integration system connecting JARVIS to external services:
- Email (Gmail, Outlook)
- Calendar (Google Calendar, Outlook)
- GitHub (Repositories & Issues)
- Slack (Team Communication)
- Notion (Knowledge Base)
- IoT (Smart Home Devices)
- Events (Trigger-based Automation)
- Workflows (Multi-step Orchestration)
- Orchestrator Bridge (JARVIS Planner/Executor Integration)

Features:
- OAuth-based credential management
- Tool discovery and registration
- Async-first architecture
- Event-driven automation
- Workflow DAG execution
- Smart home scene management
- Cross-service data flow

Quick Start:
    from integrations import email, calendar, slack
    
    # Create integrations
    email_int = email.EmailIntegration()
    calendar_int = calendar.CalendarIntegration()
    
    # Authenticate
    await email_int.authenticate()
    
    # Use tools
    emails = await email_int.read_inbox(limit=5)
    
    # Build workflows
    from integrations.workflow import Workflow, WorkflowStep
    workflow = Workflow(name="my_workflow")
    # ... define steps ...
"""

__version__ = "1.0.0"
__author__ = "JARVIS Team"

from .base import (
    BaseIntegration,
    Integration,
    ToolDefinition,
    IntegrationError,
    EventBus
)

from .auth_manager import AuthManager, Credentials

from .workflow import (
    WorkflowEngine,
    WorkflowStep,
    Workflow,
    WorkflowExecution,
    WorkflowStatus
)

from .orchestrator_bridge import (
    OrchestratorBridge,
    IntegrationRegistry,
    PlannerToolInterface,
    ExecutorExecutionInterface,
    ToolExecution
)

# Make submodules easily importable
from . import email
from . import calendar
from . import github
from . import slack
from . import notion
from . import iot
from . import events
from . import workflow

__all__ = [
    # Core infrastructure
    "BaseIntegration",
    "Integration",
    "ToolDefinition",
    "IntegrationError",
    "EventBus",
    
    # Authentication
    "AuthManager",
    "Credentials",
    
    # Workflow
    "WorkflowEngine",
    "WorkflowStep",
    "Workflow",
    "WorkflowExecution",
    "WorkflowStatus",
    
    # Orchestrator bridge
    "OrchestratorBridge",
    "IntegrationRegistry",
    "PlannerToolInterface",
    "ExecutorExecutionInterface",
    "ToolExecution",
    
    # Integration modules
    "email",
    "calendar",
    "github",
    "slack",
    "notion",
    "iot",
    "events",
    "workflow"
]
