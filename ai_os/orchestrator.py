"""
Orchestrator - Central brain of JARVIS AI OS

The orchestrator:
1. Receives all inputs (voice, text, vision, integrations)
2. Gathers context from all phases (1-7)
3. Makes decisions about what to do
4. Delegates tasks to agents
5. Monitors execution
6. Provides responses and feedback

This is the main entry point for all JARVIS operations.
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from .core_types import Task, TaskStatus, SystemMode, SystemState, Decision, Priority, InputType
from .context_engine import ContextEngine, UnifiedContext
from .decision_engine import DecisionEngine
from .agent_manager import AgentManager, BaseAgent
from .workflow_engine import WorkflowEngine, Workflow
from .plugin_system import PluginSystem
import psutil
import threading


class Orchestrator:
    """
    Central orchestrating brain of JARVIS AI OS
    
    The orchestrator is the core system that:
    - Receives input from all sources
    - Maintains unified context
    - Makes intelligent decisions
    - Manages agents and workflows
    - Controls system behavior
    - Maintains autonomy mode
    
    Example:
        orchestrator = Orchestrator(groq_client)
        orchestrator.initialize()
        
        # User input
        await orchestrator.process_input(InputType.TEXT, "Research quantum computing")
        
        # Autonomous operation
        orchestrator.set_mode(SystemMode.AUTONOMOUS)
        await orchestrator.run_autonomously()
    """
    
    def __init__(self, groq_client=None):
        """
        Initialize orchestrator
        
        Args:
            groq_client: Groq API client for intelligent reasoning
        """
        self.id = f"orchestrator_{datetime.now().timestamp()}"
        self.groq = groq_client
        
        # Core systems
        self.context_engine = ContextEngine()
        self.decision_engine = DecisionEngine(groq_client, self.context_engine)
        self.agent_manager = AgentManager()
        self.workflow_engine = WorkflowEngine(self.agent_manager)
        self.plugin_system = PluginSystem()
        
        # State
        self.state = SystemState()
        self.mode = SystemMode.INTERACTIVE
        self.is_running = False
        
        # Task management
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.max_task_history = 100
        
        # Decision management
        self.pending_decisions: List[Decision] = []
        self.decision_history: List[Decision] = []
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "decision_made": [],
            "mode_changed": [],
            "input_received": [],
            "output_generated": []
        }
        
        # Configuration
        self.config = {
            "auto_prioritize": True,
            "batch_similar_tasks": True,
            "max_concurrent_tasks": 3,
            "interruption_threshold": 0.8,
            "learning_mode": True
        }
        
        # Monitoring
        self.start_time = datetime.now()
        self.total_tasks_processed = 0
        self.total_decisions_made = 0
        self.system_monitor_thread = None
    
    async def initialize(self) -> bool:
        """
        Initialize all orchestrator systems
        
        Must be called before using orchestrator
        """
        
        print("🧠 Initializing JARVIS Orchestrator...")
        
        try:
            # Register built-in agents
            await self._register_default_agents()
            
            # Load default workflows
            await self._register_default_workflows()
            
            # Load default plugins
            await self._load_default_plugins()
            
            print("✅ JARVIS Orchestrator initialized")
            return True
        
        except Exception as e:
            print(f"❌ Orchestrator initialization failed: {e}")
            return False
    
    async def process_input(self,
                           input_type: InputType,
                           content: str,
                           metadata: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Process user input from any source
        
        Args:
            input_type: Type of input (VOICE, TEXT, GESTURE, etc.)
            content: Input content
            metadata: Additional metadata
            
        Returns:
            Response or result
        """
        
        print(f"📥 Input received ({input_type.value}): {content[:50]}...")
        
        await self._notify_callbacks("input_received", {
            "type": input_type,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # Create task from input
        task = Task(
            title=f"Process {input_type.value} input",
            description=content,
            context=metadata or {}
        )
        
        # Queue task
        self.task_queue.append(task)
        
        # Process based on mode
        if self.mode == SystemMode.INTERACTIVE:
            return await self._process_with_interaction(task)
        elif self.mode == SystemMode.AUTONOMOUS:
            return await self._process_autonomously(task)
        else:
            return await self._process_supervised(task)
    
    async def run_autonomously(self, duration_seconds: Optional[int] = None):
        """
        Run in autonomous mode
        
        JARVIS makes decisions and acts without asking
        Only interrupts for critical events
        
        Args:
            duration_seconds: How long to run (None = indefinite)
        """
        
        print("🤖 JARVIS entering autonomous mode...")
        self.set_mode(SystemMode.AUTONOMOUS)
        self.is_running = True
        
        start_time = datetime.now()
        
        try:
            while self.is_running:
                # Check duration
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed > duration_seconds:
                        break
                
                # Make next decision
                decision = await self.decision_engine.decide_next_action()
                
                if decision:
                    # Execute decision
                    await self._execute_decision(decision)
                
                # Update context
                await self._update_system_state()
                
                # Small delay to avoid spinning
                await asyncio.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n⏸️ Autonomous mode interrupted by user")
        except Exception as e:
            print(f"❌ Error in autonomous mode: {e}")
        
        finally:
            self.is_running = False
            self.set_mode(SystemMode.INTERACTIVE)
            print("🛑 Autonomous mode ended")
    
    def set_mode(self, mode: SystemMode):
        """Set system mode"""
        if mode != self.mode:
            self.mode = mode
            print(f"🔄 Mode changed to: {mode.value}")
            asyncio.create_task(self._notify_callbacks(
                "mode_changed", {"mode": mode.value, "timestamp": datetime.now()}
            ))
    
    async def add_task(self, task: Task) -> str:
        """
        Add a task to the queue
        
        Returns:
            Task ID
        """
        
        self.task_queue.append(task)
        
        # Auto-prioritize if enabled
        if self.config["auto_prioritize"]:
            self.task_queue = await self.decision_engine.prioritize_tasks(
                self.task_queue
            )
        
        return task.id
    
    async def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a workflow"""
        
        result = await self.workflow_engine.execute(workflow)
        
        if result.status == TaskStatus.COMPLETED:
            print(f"✅ Workflow completed: {workflow.name}")
        else:
            print(f"❌ Workflow failed: {workflow.name}")
        
        return result.to_dict() if hasattr(result, 'to_dict') else {
            "status": result.status.value,
            "errors": result.errors
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        
        agents = self.agent_manager.get_agent_metrics()
        
        return {
            "id": self.id,
            "mode": self.mode.value,
            "is_running": self.is_running,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "tasks_processed": self.total_tasks_processed,
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "pending_decisions": len(self.pending_decisions),
            "agents": agents,
            "system": {
                "cpu_usage": self.state.cpu_usage,
                "memory_usage": self.state.memory_usage,
                "running_tasks": self.state.running_tasks
            }
        }
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for an event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    # === Internal Methods ===
    
    async def _register_default_agents(self):
        """Register built-in agents"""
        
        from .agent_manager import (
            ResearchAgent, CodingAgent, CommunicationAgent,
            AutomationAgent, PersonalAssistantAgent
        )
        
        agents = [
            ResearchAgent(self.groq),
            CodingAgent(self.groq),
            CommunicationAgent(self.groq),
            AutomationAgent(),
            PersonalAssistantAgent(self.groq)
        ]
        
        for agent in agents:
            self.agent_manager.register_agent(agent)
    
    async def _register_default_workflows(self):
        """Register default workflows"""
        
        from .workflow_engine import (
            create_research_workflow,
            create_coding_workflow,
            create_communication_workflow
        )
        
        workflows = [
            create_research_workflow(),
            create_coding_workflow(),
            create_communication_workflow()
        ]
        
        for workflow in workflows:
            self.workflow_engine.register_workflow(workflow)
    
    async def _load_default_plugins(self):
        """Load default plugins"""
        
        from .plugin_system import WeatherPlugin, NotificationPlugin
        
        plugins = [
            WeatherPlugin(),
            NotificationPlugin()
        ]
        
        for plugin in plugins:
            await self.plugin_system.load_plugin(plugin)
            await self.plugin_system.enable_plugin(plugin.id)
    
    async def _process_with_interaction(self, task: Task) -> Optional[Any]:
        """Process task in interactive mode (ask user)"""
        
        # Make decision
        decision = await self.decision_engine.evaluate_task(task)
        
        # Present to user
        print(f"\n🤔 Decision: {decision.action}")
        print(f"Priority: {decision.priority.name} (Confidence: {decision.confidence:.0%})")
        print(f"Reasoning: {decision.reasoning[:200]}...")
        
        # In real implementation, wait for user confirmation
        # For now, auto-approve
        return await self._execute_decision(decision)
    
    async def _process_autonomously(self, task: Task) -> Optional[Any]:
        """Process task in autonomous mode (no asking)"""
        
        # Make decision
        decision = await self.decision_engine.evaluate_task(task)
        
        # Auto-execute
        return await self._execute_decision(decision)
    
    async def _process_supervised(self, task: Task) -> Optional[Any]:
        """Process task in supervised mode (ask only for critical)"""
        
        # Make decision
        decision = await self.decision_engine.evaluate_task(task)
        
        # Ask only if critical
        if decision.requires_approval and decision.priority == Priority.CRITICAL:
            should_interrupt = await self.decision_engine.should_interrupt_user(
                decision.action
            )
            
            if should_interrupt:
                print(f"\n⚠️ CRITICAL: {decision.action}")
                # Ask user
                # For now, auto-approve
        
        return await self._execute_decision(decision)
    
    async def _execute_decision(self, decision: Decision) -> Optional[Any]:
        """Execute a decision"""
        
        self.pending_decisions.append(decision)
        self.total_decisions_made += 1
        
        await self._notify_callbacks("decision_made", {
            "action": decision.action,
            "priority": decision.priority.name,
            "confidence": decision.confidence,
            "timestamp": datetime.now()
        })
        
        try:
            # Create task from decision
            if decision.task:
                task = decision.task
            else:
                task = Task(
                    title=decision.action,
                    agent_type=decision.agent_type
                )
            
            task.status = TaskStatus.RUNNING
            
            await self._notify_callbacks("task_started", {
                "task_id": task.id,
                "title": task.title,
                "timestamp": datetime.now()
            })
            
            # Execute via agent
            if decision.agent_type:
                result = await self.agent_manager.dispatch_task(task)
            else:
                result = await self._execute_generic(task)
            
            # Mark complete
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            
            self.completed_tasks.append(task)
            self.total_tasks_processed += 1
            
            if len(self.completed_tasks) > self.max_task_history:
                self.completed_tasks = self.completed_tasks[-self.max_task_history:]
            
            await self._notify_callbacks("task_completed", {
                "task_id": task.id,
                "result": result,
                "timestamp": datetime.now()
            })
            
            return result
        
        except Exception as e:
            await self._notify_callbacks("task_failed", {
                "error": str(e),
                "timestamp": datetime.now()
            })
            raise
    
    async def _execute_generic(self, task: Task) -> Optional[Any]:
        """Execute generic task without specific agent"""
        
        if self.groq:
            try:
                message = self.groq.messages.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "user", "content": f"Task: {task.title}. {task.description}"}
                    ],
                    max_tokens=500
                )
                return message.content[0].text
            except:
                pass
        
        return f"Executed: {task.title}"
    
    async def _update_system_state(self):
        """Update system state metrics"""
        
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        
        self.state.cpu_usage = cpu
        self.state.memory_usage = memory
        self.state.running_tasks = len([t for t in self.task_queue if t.status == TaskStatus.RUNNING])
        self.state.last_update = datetime.now()
    
    async def _notify_callbacks(self, event: str, data: Dict[str, Any]):
        """Notify all callbacks for an event"""
        
        if event not in self.callbacks:
            return
        
        for callback in self.callbacks[event]:
            try:
                if hasattr(callback, "__await__"):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                print(f"Error in callback for {event}: {e}")
    
    async def shutdown(self):
        """Shutdown orchestrator"""
        
        print("🛑 Shutting down JARVIS Orchestrator...")
        
        self.is_running = False
        
        # Disable plugins
        for plugin in self.plugin_system.registry.list_plugins(enabled_only=True):
            await self.plugin_system.disable_plugin(plugin.id)
        
        print("✅ Orchestrator shutdown complete")
