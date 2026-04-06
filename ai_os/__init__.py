"""
JARVIS AI Operating System (JAIOS)

Transform JARVIS into a full AI Operating System where:
- AI agents manage most workflows autonomously
- Traditional apps become secondary
- Unified context from all phases (1-7)
- Intelligent decision-making with Groq
- Natural human-AI partnership

Core components:
- Orchestrator: Central brain & decision maker
- AgentManager: Multi-agent control system
- WorkflowEngine: Task pipeline execution
- ContextEngine: Unified context aggregation
- DecisionEngine: Priority & reasoning logic
- PluginSystem: Extensibility framework

Architecture:
    Voice/Text/Vision Input
           ↓
    [Orchestrator Brain]
           ↓
    [Decision Engine] ← [Context Engine] ← All phases (1-7)
           ↓
    [Agent Manager] → Deploy agents
           ↓
    [Workflow Engine] → Execute pipelines
           ↓
    Output (Speak/Act/Control)
"""

# Core types
from .core_types import (
    Priority, AgentType, TaskStatus, SystemMode, InputType,
    Task, Decision, WorkflowState, SystemState, AgentCapability,
    WorkflowContext
)

# Context
from .context_engine import ContextEngine, UnifiedContext

# Decision
from .decision_engine import DecisionEngine

# Agents
from .agent_manager import (
    AgentManager, BaseAgent, AgentRegistry,
    ResearchAgent, CodingAgent, CommunicationAgent,
    AutomationAgent, PersonalAssistantAgent
)

# Workflows
from .workflow_engine import (
    WorkflowEngine, Workflow, WorkflowStep, WorkflowResult,
    create_research_workflow, create_coding_workflow, create_communication_workflow
)

# Plugins
from .plugin_system import PluginSystem, Plugin, PluginRegistry

# Orchestrator
from .orchestrator import Orchestrator

__version__ = "5.0.0"
__all__ = [
    # Types
    "Priority", "AgentType", "TaskStatus", "SystemMode", "InputType",
    "Task", "Decision", "WorkflowState", "SystemState", "AgentCapability",
    "WorkflowContext",
    
    # Context
    "ContextEngine", "UnifiedContext",
    
    # Decision
    "DecisionEngine",
    
    # Agents
    "AgentManager", "BaseAgent", "AgentRegistry",
    "ResearchAgent", "CodingAgent", "CommunicationAgent",
    "AutomationAgent", "PersonalAssistantAgent",
    
    # Workflows
    "WorkflowEngine", "Workflow", "WorkflowStep", "WorkflowResult",
    "create_research_workflow", "create_coding_workflow", "create_communication_workflow",
    
    # Plugins
    "PluginSystem", "Plugin", "PluginRegistry",
    
    # Orchestrator
    "Orchestrator",
]
