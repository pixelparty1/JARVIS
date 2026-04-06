"""
Workflow Automation - Multi-platform Workflows

Enables chaining operations across integrations.

Examples:
- "Summarize emails and save to Notion"
- "Check calendar and send Slack reminder"
- "Create GitHub issue from email"
"""

import asyncio
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Single workflow step."""
    id: str = None
    name: str = ""
    action: str = ""  # integration.tool format
    parameters: Dict[str, Any] = field(default_factory=dict)
    next_step: Optional[str] = None
    on_error: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"step_{uuid.uuid4().hex[:8]}"


@dataclass
class WorkflowExecution:
    """Workflow execution record."""
    id: str
    workflow_name: str
    status: WorkflowStatus
    started_at: str
    ended_at: Optional[str] = None
    steps_executed: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class Workflow:
    """
    Workflow definition and execution.
    
    Features:
    - Multi-step workflows
    - Error handling
    - Conditional execution
    - Result chaining
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
        """
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.start_step: Optional[str] = None
        self.triggers: List[str] = []  # Trigger conditions
        self.created_at = datetime.now().isoformat()
    
    def add_step(self, step: WorkflowStep, as_start: bool = False) -> None:
        """
        Add a step to the workflow.
        
        Args:
            step: WorkflowStep instance
            as_start: Make this the starting step
        """
        self.steps[step.id] = step
        
        if as_start or self.start_step is None:
            self.start_step = step.id
    
    def connect_steps(self, from_step: str, to_step: str) -> None:
        """Connect two steps."""
        if from_step in self.steps:
            self.steps[from_step].next_step = to_step
    
    def set_error_handler(self, from_step: str, error_handler: str) -> None:
        """Set error handling step."""
        if from_step in self.steps:
            self.steps[from_step].on_error = error_handler
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize workflow."""
        return {
            'name': self.name,
            'description': self.description,
            'steps': {
                step_id: {
                    'name': step.name,
                    'action': step.action,
                    'parameters': step.parameters,
                    'next_step': step.next_step,
                    'on_error': step.on_error
                }
                for step_id, step in self.steps.items()
            },
            'start_step': self.start_step,
            'created_at': self.created_at
        }


class WorkflowEngine:
    """
    Workflow execution engine.
    
    Handles running workflows across integrations.
    """
    
    def __init__(self):
        """Initialize workflow engine."""
        self.workflows: Dict[str, Workflow] = {}
        self.executions: List[WorkflowExecution] = []
        self.integrations: Dict[str, Any] = {}
    
    def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow."""
        self.workflows[workflow.name] = workflow
        print(f"✅ Workflow registered: {workflow.name}")
    
    def register_integration(self, name: str, integration: Any) -> None:
        """
        Register an integration.
        
        Args:
            name: Integration name
            integration: Integration instance
        """
        self.integrations[name] = integration
        print(f"✅ Integration registered: {name}")
    
    async def execute(self, workflow_name: str,
                     context: Dict[str, Any] = None) -> WorkflowExecution:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of workflow to execute
            context: Initial context
            
        Returns:
            WorkflowExecution record
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        execution = WorkflowExecution(
            id=execution_id,
            workflow_name=workflow_name,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now().isoformat()
        )
        
        if context is None:
            context = {}
        
        print(f"\n🚀 Executing workflow: {workflow_name}")
        
        try:
            # Execute steps
            current_step = workflow.start_step
            
            while current_step:
                step = workflow.steps.get(current_step)
                if not step:
                    break
                
                print(f"  📍 Step: {step.name}")
                
                try:
                    result = await self._execute_step(step, context)
                    
                    # Store result
                    execution.results[step.id] = result
                    execution.steps_executed.append(step.id)
                    
                    # Move to next step
                    current_step = step.next_step
                    
                except Exception as e:
                    print(f"     ❌ Error: {e}")
                    
                    if step.on_error:
                        current_step = step.on_error
                    else:
                        raise
            
            execution.status = WorkflowStatus.SUCCESS
            print(f"✅ Workflow completed successfully\n")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            print(f"❌ Workflow failed: {e}\n")
        
        finally:
            execution.ended_at = datetime.now().isoformat()
            execution.duration_seconds = (
                (datetime.fromisoformat(execution.ended_at) -
                 datetime.fromisoformat(execution.started_at)).total_seconds()
            )
            
            self.executions.append(execution)
        
        return execution
    
    async def _execute_step(self, step: WorkflowStep,
                           context: Dict[str, Any]) -> Any:
        """
        Execute a single step.
        
        Args:
            step: WorkflowStep to execute
            context: Workflow context
            
        Returns:
            Step result
        """
        # Parse action: integration.tool_name
        parts = step.action.split(".")
        if len(parts) != 2:
            raise ValueError(f"Invalid action format: {step.action}")
        
        integration_name, tool_name = parts
        
        if integration_name not in self.integrations:
            raise ValueError(f"Integration not found: {integration_name}")
        
        integration = self.integrations[integration_name]
        
        # Prepare parameters (substitute context variables)
        params = {}
        for key, value in step.parameters.items():
            if isinstance(value, str) and value.startswith("$."):
                # Context reference
                context_key = value[2:]
                params[key] = context.get(context_key, value)
            else:
                params[key] = value
        
        # Execute tool
        result = await integration._execute_tool(tool_name, **params)
        
        # Store result in context for next steps
        context[step.id] = result
        
        print(f"     ✓ {tool_name} executed")
        
        return result
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history."""
        return [
            {
                'id': exec.id,
                'workflow': exec.workflow_name,
                'status': exec.status.value,
                'started_at': exec.started_at,
                'duration': exec.duration_seconds,
                'steps': len(exec.steps_executed)
            }
            for exec in self.executions[-limit:]
        ]
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        total_execs = len(self.executions)
        successful = sum(1 for e in self.executions if e.status == WorkflowStatus.SUCCESS)
        failed = sum(1 for e in self.executions if e.status == WorkflowStatus.FAILED)
        
        avg_duration = 0
        if self.executions:
            durations = [e.duration_seconds for e in self.executions if e.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_executions': total_execs,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_execs * 100) if total_execs > 0 else 0,
            'average_duration': avg_duration,
            'registered_workflows': len(self.workflows)
        }


# Predefined Workflows

def create_email_to_notion_workflow() -> Workflow:
    """Create workflow: Email → Notion."""
    workflow = Workflow(
        name="email_to_notion",
        description="Summarize emails and save to Notion"
    )
    
    # Step 1: Read emails
    step1 = WorkflowStep(
        name="Read unread emails",
        action="email.read_inbox",
        parameters={"unread_only": True, "limit": 5}
    )
    workflow.add_step(step1, as_start=True)
    
    # Step 2: Summarize
    step2 = WorkflowStep(
        name="Summarize for each email",
        action="email.summarize_email",
        parameters={"email_id": "$.email_id"}
    )
    workflow.add_step(step2)
    workflow.connect_steps(step1.id, step2.id)
    
    # Step 3: Save to Notion
    step3 = WorkflowStep(
        name="Save to Notion",
        action="notion.create_page",
        parameters={
            "title": "Email Summary",
            "content": "$.step2",
            "database": "email_archive",
            "tags": ["email"]
        }
    )
    workflow.add_step(step3)
    workflow.connect_steps(step2.id, step3.id)
    
    return workflow


def create_calendar_reminder_workflow() -> Workflow:
    """Create workflow: Check calendar & send Slack reminder."""
    workflow = Workflow(
        name="calendar_reminder",
        description="Check calendar and send Slack reminders"
    )
    
    # Step 1: Get today's events
    step1 = WorkflowStep(
        name="Get calendar events",
        action="calendar.get_events",
        parameters={
            "start_date": "$.today_start",
            "end_date": "$.today_end",
            "limit": 10
        }
    )
    workflow.add_step(step1, as_start=True)
    
    # Step 2: Send Slack notification
    step2 = WorkflowStep(
        name="Send reminder",
        action="slack.send_message",
        parameters={
            "channel": "general",
            "content": "Good morning! Here's your schedule for today."
        }
    )
    workflow.add_step(step2)
    workflow.connect_steps(step1.id, step2.id)
    
    return workflow


def create_github_digest_workflow() -> Workflow:
    """Create workflow: GitHub digest."""
    workflow = Workflow(
        name="github_digest",
        description="Generate GitHub status digest"
    )
    
    # Step 1: Get repositories
    step1 = WorkflowStep(
        name="List repos",
        action="github.list_repos",
        parameters={"limit": 5}
    )
    workflow.add_step(step1, as_start=True)
    
    # Step 2: Get open issues
    step2 = WorkflowStep(
        name="Get open issues",
        action="github.get_issues",
        parameters={"repo": "$.repo_name", "state": "open"}
    )
    workflow.add_step(step2)
    workflow.connect_steps(step1.id, step2.id)
    
    return workflow


# Example usage
if __name__ == "__main__":
    async def test_workflow():
        print("🧪 Workflow Engine Test\n")
        
        from . import email, calendar, notion, slack
        
        # Create engine
        engine = WorkflowEngine()
        
        # Register integrations
        email_int = email.EmailIntegration()
        calendar_int = calendar.CalendarIntegration()
        notion_int = notion.NotionIntegration()
        slack_int = slack.SlackIntegration()
        
        await email_int.authenticate()
        await calendar_int.authenticate()
        await notion_int.authenticate()
        await slack_int.authenticate()
        
        engine.register_integration("email", email_int)
        engine.register_integration("calendar", calendar_int)
        engine.register_integration("notion", notion_int)
        engine.register_integration("slack", slack_int)
        
        # Register workflows
        workflow = create_calendar_reminder_workflow()
        engine.register_workflow(workflow)
        
        # Execute workflow
        execution = await engine.execute("calendar_reminder")
        print(f"\nExecution status: {execution.status.value}")
    
    # asyncio.run(test_workflow())
