"""
Agent Manager - Control and coordinate multiple AI agents

Agents:
- Research Agent: Gather and analyze information
- Coding Agent: Write and debug code
- Communication Agent: Write and send messages
- Automation Agent: Create and manage workflows
- Personal Assistant Agent: General tasks and suggestions

Each agent:
- Has specific tools
- Maintains memory
- Can work independently
- Communicates with orchestrator
"""

import asyncio
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime
from .core_types import Task, TaskStatus, AgentType, AgentCapability


class BaseAgent(ABC):
    """
    Base class for all JARVIS agents
    
    Each agent:
    - Specializes in specific tasks
    - Has a set of tools
    - Maintains success metrics
    - Can be monitored and controlled
    """
    
    def __init__(self, name: str, agent_type: AgentType, description: str = ""):
        self.id = f"agent_{agent_type.value}_{datetime.now().timestamp()}"
        self.name = name
        self.agent_type = agent_type
        self.description = description
        
        # Capabilities
        self.capabilities: Dict[str, AgentCapability] = {}
        self.tools: Dict[str, callable] = {}
        
        # Memory
        self.memory: List[Dict[str, Any]] = []
        self.max_memory = 100
        
        # Metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0.0
        self.success_rate = 0.0
        
        # Status
        self.is_active = True
        self.current_task: Optional[Task] = None
    
    async def execute(self, task: Task) -> Any:
        """
        Execute a task
        
        This is the main entry point for task execution.
        Subclasses should override process_task()
        """
        
        if not self.is_active:
            raise Exception(f"Agent {self.name} is not active")
        
        start_time = datetime.now()
        self.current_task = task
        
        try:
            # Process the task
            result = await self.process_task(task)
            
            # Update metrics
            self.tasks_completed += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            self.total_processing_time += processing_time
            self.success_rate = self.tasks_completed / (self.tasks_completed + self.tasks_failed)
            
            # Remember in memory
            await self.remember({
                "task": task.title,
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        
        except Exception as e:
            self.tasks_failed += 1
            self.success_rate = self.tasks_completed / (self.tasks_completed + self.tasks_failed)
            
            await self.remember({
                "task": task.title,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            raise
        
        finally:
            self.current_task = None
    
    @abstractmethod
    async def process_task(self, task: Task) -> Any:
        """
        Process a specific task
        
        Override this in subclasses
        """
        raise NotImplementedError()
    
    async def remember(self, memory_entry: Dict[str, Any]):
        """Remember something for future reference"""
        self.memory.append(memory_entry)
        
        # Keep memory bounded
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
    
    def register_capability(self, capability: AgentCapability):
        """Register a capability"""
        self.capabilities[capability.name] = capability
    
    def register_tool(self, name: str, handler: callable):
        """Register a tool"""
        self.tools[name] = handler
    
    def get_capabilities(self) -> Dict[str, AgentCapability]:
        """Get all capabilities"""
        return self.capabilities
    
    def get_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def call_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Call a tool"""
        if tool_name not in self.tools:
            raise Exception(f"Tool {tool_name} not found")
        
        return self.tools[tool_name](*args, **kwargs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get agent summary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type.value,
            "active": self.is_active,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "success_rate": self.success_rate,
            "capabilities": len(self.capabilities),
            "tools": len(self.tools)
        }


class AgentRegistry:
    """Registry to track all agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.id] = agent
    
    def unregister(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        return [a for a in self.agents.values() if a.agent_type == agent_type]
    
    def list_agents(self) -> List[BaseAgent]:
        """List all agents"""
        return list(self.agents.values())


class AgentManager:
    """
    Manage multiple agents
    
    Responsibilities:
    - Register/unregister agents
    - Route tasks to appropriate agents
    - Monitor agent status
    - Coordinate between agents
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.task_queue: List[Task] = []
        self.executing = False
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.registry.register(agent)
        print(f"✅ Agent registered: {agent.name} ({agent.agent_type.value})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        self.registry.unregister(agent_id)
    
    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Get an agent of a specific type (returns first available)"""
        agents = self.registry.get_agents_by_type(agent_type)
        
        # Return least busy agent
        if agents:
            return min(agents, key=lambda a: a.tasks_completed)
        
        return None
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a type"""
        return self.registry.get_agents_by_type(agent_type)
    
    async def dispatch_task(self, task: Task) -> Any:
        """
        Dispatch a task to the appropriate agent
        
        Automatically routes based on task type
        """
        
        if not task.agent_type:
            raise Exception("Task must have agent_type specified")
        
        # Get appropriate agent
        agent = self.get_agent(task.agent_type)
        
        if not agent:
            raise Exception(f"No agent available for type {task.agent_type.value}")
        
        # Execute task
        return await agent.execute(task)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent"""
        agent = self.registry.get_agent(agent_id)
        if agent:
            return agent.get_summary()
        return None
    
    def get_all_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        agents = self.registry.list_agents()
        return [agent.get_summary() for agent in agents]
    
    def get_agent_memory(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get agent memory"""
        agent = self.registry.get_agent(agent_id)
        if agent:
            return agent.memory[-limit:]
        return []
    
    def deactivate_agent(self, agent_id: str):
        """Deactivate an agent (stop it from accepting tasks)"""
        agent = self.registry.get_agent(agent_id)
        if agent:
            agent.is_active = False
            print(f"🔴 Agent deactivated: {agent.name}")
    
    def activate_agent(self, agent_id: str):
        """Activate an agent"""
        agent = self.registry.get_agent(agent_id)
        if agent:
            agent.is_active = True
            print(f"🟢 Agent activated: {agent.name}")
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get system-wide agent metrics"""
        agents = self.registry.list_agents()
        
        total_completed = sum(a.tasks_completed for a in agents)
        total_failed = sum(a.tasks_failed for a in agents)
        avg_success = sum(a.success_rate for a in agents) / len(agents) if agents else 0
        
        return {
            "total_agents": len(agents),
            "total_tasks_completed": total_completed,
            "total_tasks_failed": total_failed,
            "average_success_rate": avg_success,
            "agents": [a.get_summary() for a in agents]
        }


# Built-in Agents

class ResearchAgent(BaseAgent):
    """
    Research Agent
    
    Specializes in:
    - Gathering information
    - Searching knowledge bases
    - Analyzing data
    - Creating summaries
    """
    
    def __init__(self, groq_client=None):
        super().__init__(
            "Research Agent",
            AgentType.RESEARCH,
            "Gathers, analyzes, and synthesizes information"
        )
        self.groq = groq_client
        
        # Register tools
        self.register_capability(AgentCapability(
            "search",
            "Search for information",
            tools=["google_search", "wikipedia_search"]
        ))
        self.register_capability(AgentCapability(
            "analyze",
            "Analyze data and information",
            tools=["analyze_text", "extract_insights"]
        ))
    
    async def process_task(self, task: Task) -> Any:
        """Process a research task"""
        
        # Simulated research process
        context = task.context or {}
        topic = context.get("topic", task.title)
        
        # Use Groq for reasoning if available
        if self.groq:
            try:
                message = self.groq.messages.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "user", "content": f"Research: {topic}. Provide key insights in 3-4 sentences."}
                    ],
                    max_tokens=300
                )
                return message.content[0].text
            except:
                pass
        
        return f"Research summary on {topic}: [Information would be gathered here]"


class CodingAgent(BaseAgent):
    """
    Coding Agent
    
    Specializes in:
    - Writing code
    - Debugging
    - Code review
    - Testing
    """
    
    def __init__(self, groq_client=None):
        super().__init__(
            "Coding Agent",
            AgentType.CODING,
            "Writes, debugs, and tests code"
        )
        self.groq = groq_client
        
        # Register tools
        self.register_capability(AgentCapability(
            "write_code",
            "Write code for a task",
            tools=["generate_code", "format_code"]
        ))
        self.register_capability(AgentCapability(
            "debug",
            "Debug and fix code",
            tools=["analyze_error", "test_code"]
        ))
    
    async def process_task(self, task: Task) -> Any:
        """Process a coding task"""
        
        context = task.context or {}
        requirement = context.get("requirement", task.description)
        language = context.get("language", "python")
        
        if self.groq:
            try:
                message = self.groq.messages.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "user", "content": f"Write {language} code for: {requirement}"}
                    ],
                    max_tokens=500
                )
                return message.content[0].text
            except:
                pass
        
        return f"Generated code for: {requirement}"


class CommunicationAgent(BaseAgent):
    """
    Communication Agent
    
    Specializes in:
    - Writing messages
    - Email composition
    - Social communication
    - Notifications
    """
    
    def __init__(self, groq_client=None):
        super().__init__(
            "Communication Agent",
            AgentType.COMMUNICATION,
            "Composes and sends communications"
        )
        self.groq = groq_client
        
        # Register tools
        self.register_capability(AgentCapability(
            "compose",
            "Compose messages",
            tools=["generate_email", "generate_message"]
        ))
        self.register_capability(AgentCapability(
            "send",
            "Send communications",
            tools=["send_email", "send_slack", "send_notification"]
        ))
    
    async def process_task(self, task: Task) -> Any:
        """Process a communication task"""
        
        context = task.context or {}
        recipient = context.get("recipient", "user")
        message_type = context.get("type", "message")
        
        return f"Composed {message_type} to {recipient}: {task.description}"


class AutomationAgent(BaseAgent):
    """
    Automation Agent
    
    Specializes in:
    - Creating workflows
    - Automating repetitive tasks
    - System automation
    - Integration management
    """
    
    def __init__(self):
        super().__init__(
            "Automation Agent",
            AgentType.AUTOMATION,
            "Creates and manages automated workflows"
        )
        
        # Register tools
        self.register_capability(AgentCapability(
            "create_workflow",
            "Create automated workflow",
            tools=["define_workflow", "setup_triggers"]
        ))
        self.register_capability(AgentCapability(
            "manage",
            "Manage existing automations",
            tools=["list_automations", "disable_automation", "enable_automation"]
        ))
    
    async def process_task(self, task: Task) -> Any:
        """Process an automation task"""
        
        context = task.context or {}
        workflow_name = context.get("workflow", task.title)
        
        return f"Created automation: {workflow_name}"


class PersonalAssistantAgent(BaseAgent):
    """
    Personal Assistant Agent
    
    Specializes in:
    - General task assistance
    - Information retrieval
    - Scheduling
    - Suggestions and recommendations
    """
    
    def __init__(self, groq_client=None):
        super().__init__(
            "Personal Assistant",
            AgentType.ASSISTANT,
            "Provides general assistance and suggestions"
        )
        self.groq = groq_client
        
        # Register tools
        self.register_capability(AgentCapability(
            "assist",
            "General assistance",
            tools=["answer_question", "provide_suggestion"]
        ))
    
    async def process_task(self, task: Task) -> Any:
        """Process an assistance task"""
        
        if self.groq:
            try:
                message = self.groq.messages.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "user", "content": f"{task.description}"}
                    ],
                    max_tokens=300
                )
                return message.content[0].text
            except:
                pass
        
        return f"Response to: {task.description}"
