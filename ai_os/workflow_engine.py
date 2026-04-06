"""
Workflow Engine - Execute multi-step task pipelines

Enables complex workflows like:
"Research topic" → "Synthesize findings" → "Create summary" → "Send report"

Each step handled by potentially different agents
"""

from typing import List, Dict, Any, Callable, Optional, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from .core_types import Task, TaskStatus, WorkflowState, WorkflowContext, AgentType


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    id: str
    name: str
    description: str
    agent_type: AgentType
    
    # Execution
    handler: Optional[Callable] = None
    timeout: int = 300  # seconds
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Configuration
    retry_count: int = 3
    skip_on_error: bool = False
    
    # Input/output
    required_inputs: List[str] = field(default_factory=list)
    output_keys: List[str] = field(default_factory=list)


class Workflow:
    """
    Multi-step workflow definition
    
    Example:
        workflow = Workflow("Research & Report")
        workflow.add_step("research", AgentType.RESEARCH, ...)
        workflow.add_step("synthesize", AgentType.RESEARCH, ...)
        workflow.add_step("write", AgentType.CODING, ...)
        workflow.add_step("send", AgentType.COMMUNICATION, ...)
    """
    
    def __init__(self, name: str, description: str = ""):
        self.id = f"workflow_{datetime.now().timestamp()}"
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.step_order: List[str] = []
        self.created_at = datetime.now()
    
    def add_step(self,
                 step_id: str,
                 name: str,
                 agent_type: AgentType,
                 handler: Optional[Callable] = None,
                 description: str = "",
                 depends_on: Optional[List[str]] = None,
                 **kwargs) -> WorkflowStep:
        """Add a step to the workflow"""
        
        step = WorkflowStep(
            id=step_id,
            name=name,
            description=description,
            agent_type=agent_type,
            handler=handler,
            depends_on=depends_on or [],
            **kwargs
        )
        
        self.steps[step_id] = step
        self.step_order.append(step_id)
        
        return step
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a workflow step"""
        return self.steps.get(step_id)
    
    def validate(self) -> bool:
        """Validate workflow structure"""
        
        # Check for cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id):
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = self.steps.get(step_id)
            if not step:
                return False
            
            for dep in step.depends_on:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        for step_id in self.steps:
            if step_id not in visited:
                if has_cycle(step_id):
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "agent_type": step.agent_type.value,
                    "depends_on": step.depends_on,
                }
                for step in self.steps.values()
            ],
            "created_at": self.created_at.isoformat()
        }


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    status: TaskStatus
    
    # Results per step
    step_results: Dict[str, Any] = field(default_factory=dict)
    
    # Errors
    errors: Dict[str, str] = field(default_factory=dict)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution metadata
    total_steps: int = 0
    completed_steps: int = 0
    
    def duration(self) -> Optional[float]:
        """Get total execution time in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def success_rate(self) -> float:
        """Get percentage of successful steps"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps / self.total_steps) * 100


class WorkflowEngine:
    """
    Execute multi-step workflows with intelligent routing
    """
    
    def __init__(self, agent_manager=None):
        self.agent_manager = agent_manager
        self.workflows: Dict[str, Workflow] = {}
        self.execution_states: Dict[str, WorkflowState] = {}
        self.results_history: List[WorkflowResult] = []
    
    def register_workflow(self, workflow: Workflow) -> bool:
        """Register a workflow"""
        if not workflow.validate():
            return False
        
        self.workflows[workflow.id] = workflow
        return True
    
    async def execute(self, workflow: Workflow, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        Execute a workflow
        
        Args:
            workflow: Workflow to execute
            context: Initial context/parameters
            
        Returns:
            WorkflowResult with execution status and results
        """
        
        if not workflow.validate():
            return WorkflowResult(
                workflow_id=workflow.id,
                status=TaskStatus.FAILED,
                errors={"validation": "Workflow validation failed"}
            )
        
        # Initialize result
        result = WorkflowResult(
            workflow_id=workflow.id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now(),
            total_steps=len(workflow.steps)
        )
        
        # Initialize context
        workflow_context = WorkflowContext(
            workflow_id=workflow.id,
            step_index=0,
            task=Task(
                title=workflow.name,
                description=workflow.description
            ),
            shared_state=context or {}
        )
        
        # Track execution state
        state = WorkflowState(
            workflow_id=workflow.id,
            total_steps=len(workflow.steps),
            context=context or {}
        )
        self.execution_states[workflow.id] = state
        
        # Execute steps
        executed_steps = set()
        
        try:
            while True:
                # Find next executable step
                next_step_id = self._find_next_executable_step(
                    workflow,
                    executed_steps,
                    workflow_context
                )
                
                if not next_step_id:
                    break  # All steps done
                
                step = workflow.get_step(next_step_id)
                if not step:
                    continue
                
                # Execute step
                try:
                    step_result = await self._execute_step(
                        step,
                        workflow_context,
                        result
                    )
                    
                    result.step_results[step_id] = step_result
                    workflow_context.set_result(step.id, step_result)
                    
                    result.completed_steps += 1
                    state.completed_steps.append(step.id)
                    executed_steps.add(next_step_id)
                    
                except Exception as e:
                    error_msg = f"Step failed: {str(e)}"
                    result.errors[step.id] = error_msg
                    state.failed_steps.append(step.id)
                    
                    if not step.skip_on_error:
                        result.status = TaskStatus.FAILED
                        break
                    else:
                        executed_steps.add(next_step_id)
        
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.errors["workflow"] = str(e)
        
        # Finalize result
        result.completed_at = datetime.now()
        result.status = TaskStatus.COMPLETED if not result.errors else TaskStatus.FAILED
        
        # Store result
        self.results_history.append(result)
        
        return result
    
    def _find_next_executable_step(self,
                                   workflow: Workflow,
                                   executed: set,
                                   context: WorkflowContext) -> Optional[str]:
        """Find the next step that's ready to execute"""
        
        for step_id in workflow.step_order:
            if step_id in executed:
                continue
            
            step = workflow.get_step(step_id)
            if not step:
                continue
            
            # Check dependencies
            deps_satisfied = all(dep in executed for dep in step.depends_on)
            
            if deps_satisfied:
                # Check required inputs
                inputs_available = all(
                    context.get_result(input_key) is not None
                    for input_key in step.required_inputs
                )
                
                if inputs_available:
                    return step_id
        
        return None
    
    async def _execute_step(self,
                            step: WorkflowStep,
                            context: WorkflowContext,
                            result: WorkflowResult) -> Any:
        """Execute a single step"""
        
        try:
            # Get agent for this step
            if self.agent_manager:
                agent = self.agent_manager.get_agent(step.agent_type)
                if agent:
                    # Execute via agent
                    task = Task(
                        title=step.name,
                        description=step.description,
                        agent_type=step.agent_type,
                        context=context.shared_state
                    )
                    
                    # Execute with timeout
                    try:
                        step_result = await asyncio.wait_for(
                            agent.execute(task),
                            timeout=step.timeout
                        )
                        return step_result
                    except asyncio.TimeoutError:
                        raise Exception(f"Step timeout after {step.timeout}s")
            
            # Fallback to direct handler
            if step.handler:
                if hasattr(step.handler, "__await__"):
                    return await step.handler(context)
                else:
                    return step.handler(context)
            
            raise Exception(f"No handler for step {step.id}")
        
        except Exception as e:
            raise Exception(f"Step '{step.name}' failed: {str(e)}")
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a registered workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all registered workflows"""
        return list(self.workflows.values())
    
    def get_execution_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get current execution state of a workflow"""
        return self.execution_states.get(workflow_id)
    
    def cancel_workflow(self, workflow_id: str):
        """Cancel a running workflow"""
        state = self.execution_states.get(workflow_id)
        if state:
            state.status = TaskStatus.CANCELLED
    
    def get_results_history(self, limit: int = 10) -> List[WorkflowResult]:
        """Get recent workflow results"""
        return self.results_history[-limit:]


# Common Workflow Builders

def create_research_workflow() -> Workflow:
    """Create a research workflow"""
    wf = Workflow("Research & Analysis", "Research a topic and create summary")
    
    wf.add_step(
        "research",
        "Gather Information",
        AgentType.RESEARCH,
        description="Search and gather relevant information"
    )
    
    wf.add_step(
        "analyze",
        "Analyze Findings",
        AgentType.RESEARCH,
        depends_on=["research"],
        description="Synthesize and analyze the gathered information"
    )
    
    wf.add_step(
        "summarize",
        "Create Summary",
        AgentType.ASSISTANT,
        depends_on=["analyze"],
        description="Create a concise summary"
    )
    
    return wf


def create_coding_workflow() -> Workflow:
    """Create a coding project workflow"""
    wf = Workflow("Code Project", "Plan, code, test, document")
    
    wf.add_step(
        "plan",
        "Design & Plan",
        AgentType.ASSISTANT,
        description="Design the solution"
    )
    
    wf.add_step(
        "code",
        "Write Code",
        AgentType.CODING,
        depends_on=["plan"],
        description="Implement the solution"
    )
    
    wf.add_step(
        "test",
        "Test & Debug",
        AgentType.CODING,
        depends_on=["code"],
        description="Test the code"
    )
    
    wf.add_step(
        "document",
        "Document",
        AgentType.ASSISTANT,
        depends_on=["code"],
        description="Create documentation"
    )
    
    return wf


def create_communication_workflow() -> Workflow:
    """Create a communication workflow"""
    wf = Workflow("Send Report", "Prepare, review, send")
    
    wf.add_step(
        "prepare",
        "Prepare Content",
        AgentType.ASSISTANT,
        description="Prepare the report content"
    )
    
    wf.add_step(
        "review",
        "Review",
        AgentType.ASSISTANT,
        depends_on=["prepare"],
        description="Review for quality"
    )
    
    wf.add_step(
        "send",
        "Send",
        AgentType.COMMUNICATION,
        depends_on=["review"],
        description="Send to recipients"
    )
    
    return wf
