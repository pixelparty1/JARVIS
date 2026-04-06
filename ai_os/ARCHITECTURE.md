"""
ARCHITECTURE.md - JARVIS AI Operating System Architecture

Complete technical documentation of the AI OS design and components
"""

# Architecture Overview

## Design Principles

1. **Modular**: Each component is independent and composable
2. **Intelligent**: Uses Groq for reasoning and decision-making
3. **Integrated**: Combines all JARVIS phases (1-7) into unified system
4. **Autonomous**: Can operate without user interaction
5. **Extensible**: Plugin system for adding capabilities

## Core Components

### 1. Orchestrator (Central Brain)

**Responsibility**: Main decision maker and coordinator

- Receives all inputs (voice, text, vision, integrations)
- Maintains system state
- Makes intelligent decisions
- Routes tasks to agents
- Manages workflows
- Provides responses

**Key Methods**:
- `process_input()` - Handle user input
- `run_autonomously()` - Autonomous operation
- `execute_workflow()` - Run multi-step workflows
- `get_status()` - System status

**Example**:
```python
orchestrator = Orchestrator(groq_client)
await orchestrator.initialize()
await orchestrator.process_input(InputType.TEXT, "Research quantum computing")
```

### 2. Context Engine (Unified Context)

**Responsibility**: Aggregate context from all systems

Combines data from:
- **Phase 1**: Voice/speech data
- **Phase 3**: Screen and activity
- **Phase 4**: Orchestrator state
- **Phase 5**: Memory and knowledge
- **Phase 6**: Integrations (email, calendar, etc.)
- **Phase 7**: Vision and real-world data
- Plus: User state, system metrics, behavioral patterns

**Key Methods**:
- `update_from_phase_X()` - Update context from each phase
- `get_relevant_context()` - Get filtered context
- `to_dict()` - Get full context snapshot

**Example**:
```python
context = context_engine.to_dict()
# Returns unified context dict with all phases
```

### 3. Decision Engine (Intelligent Reasoning)

**Responsibility**: Make intelligent decisions using Groq

Capabilities:
- Evaluate tasks (should execute? when? how?)
- Prioritize task queue
- Decide if should interrupt user
- Reason about complex situations
- Recommend next action

Uses Groq for:
- Natural language reasoning
- Context-aware analysis
- Confidence scoring
- Priority determination

**Key Methods**:
- `evaluate_task()` - Analyze a task
- `decide_next_action()` - Determine next step
- `prioritize_tasks()` - Sort task queue
- `should_interrupt_user()` - Interrupt decision

**Example**:
```python
decision = await decision_engine.evaluate_task(task)
# Returns Decision with action, priority, confidence, reasoning
```

### 4. Agent Manager (Multi-Agent Control)

**Responsibility**: Manage multiple specialized AI agents

Built-in Agents:
- **ResearchAgent**: Gather and analyze information
- **CodingAgent**: Write and debug code
- **CommunicationAgent**: Write and send messages
- **AutomationAgent**: Create workflows
- **PersonalAssistantAgent**: General assistance

Each agent:
- Specializes in specific task types
- Has dedicated tools
- Maintains memory of past work
- Tracks success metrics

**Key Methods**:
- `register_agent()` - Add an agent
- `dispatch_task()` - Route task to agent
- `get_agent()` - Get agent by type
- `get_agent_metrics()` - Performance data

**Example**:
```python
agent = agent_manager.get_agent(AgentType.RESEARCH)
result = await agent.execute(task)
```

### 5. Workflow Engine (Task Pipelines)

**Responsibility**: Execute multi-step workflows

Workflows enable:
- Complex multi-step tasks
- Different agents per step
- Dependencies between steps
- Parallel execution (when possible)
- Error handling and recovery

Built-in Workflows:
- Research & Analysis (3 steps)
- Code Project (4 steps)
- Send Report (3 steps)

**Key Methods**:
- `register_workflow()` - Register workflow
- `execute()` - Run workflow
- `get_execution_state()` - Check progress
- `cancel_workflow()` - Stop workflow

**Example**:
```python
workflow = create_research_workflow()
result = await workflow_engine.execute(workflow)
```

### 6. Plugin System (Extensibility)

**Responsibility**: Enable extending JARVIS with plugins

Plugin Types:
- Custom agents
- New tools
- Integrations
- Features

Plugin Lifecycle:
- Load → Enable → Run → Disable → Unload

Built-in Plugins:
- WeatherPlugin: Weather information
- NotificationPlugin: System notifications

**Key Methods**:
- `load_plugin()` - Load plugin
- `enable_plugin()` - Activate plugin
- `disable_plugin()` - Deactivate plugin
- `register_hook()` - Register hook callback

**Example**:
```python
plugin = MyCustomPlugin()
await plugin_system.load_plugin(plugin)
await plugin_system.enable_plugin(plugin.id)
```

## System Modes

### 1. INTERACTIVE Mode (Default)

JARVIS asks before taking action:
- Present decision to user
- Wait for confirmation
- Execute when approved
- Safe but slower

**Use cases**:
- General operation
- Learning new tasks
- Sensitive operations

### 2. AUTONOMOUS Mode

JARVIS acts without asking:
- Make decisions immediately
- Execute without confirmation
- Only interrupt for critical events
- Fast and efficient

**Use cases**:
- Background monitoring
- Scheduled tasks
- Trusted operations
- Demonstrations

### 3. SUPERVISED Mode

Hybrid approach:
- Ask only for critical decisions
- Auto-execute normal tasks
- Interrupt if needed
- Balance between safety and efficiency

**Use cases**:
- Mixed work scenarios
- Production environments
- Custom policies

## Data Flow

```
User Input (Voice/Text/Vision)
        ↓
   [Orchestrator] receives input
        ↓
[Context Engine] updates unified context with:
- User input
- Screen state
- Vision data
- Memory
- Integrations
        ↓
[Decision Engine] analyzes with Groq:
- What should happen?
- Priority?
- Confidence?
- Reasoning?
        ↓
  Decision: {action, priority, confidence}
        ↓
Check Mode (INTERACTIVE/AUTONOMOUS/SUPERVISED):
- INTERACTIVE: Ask user → Wait → Execute if approved
- AUTONOMOUS: Execute immediately
- SUPERVISED: Execute unless critical
        ↓
[Agent Manager] dispatch to appropriate agent
        ↓
Agent executes task using its tools:
- Research Agent: Search, analyze
- Coding Agent: Write, test code
- Communication: Compose, send messages
- Automation: Create workflows
- Assistant: General tasks
        ↓
Result returned to orchestrator
        ↓
Output (Speak/Write/Act/Control)
```

## Integration with Previous Phases

### Phase 1: Voice System
- Integration point: Voice input type
- Context: Last spoken input, sentiment
- Output: Speak responses

### Phase 3: Screen Vision
- Integration point: Screen context updates
- Context: Active window, OCR text, mouse position
- Output: Control mouse/keyboard

### Phase 4: Agent Orchestrator (Old)
- Integration point: Replaces Phase 4
- Context: Previous plans converted to context
- Output: Improved planning

### Phase 5: Memory System
- Integration point: Context updates
- Context: Relevant memories, learned patterns
- Output: Store decisions, learn from results

### Phase 6: Integrations
- Integration point: Integration status updates
- Context: Email, calendar, Slack, GitHub, etc.
- Output: Trigger integration actions

### Phase 7: Vision System
- Integration point: Real-world vision updates
- Context: Detected people, emotions, gestures, analysis
- Output: Vision-triggered responses

## Task Execution Flow

### 1. Task Creation
```python
task = Task(
    title="Research topic",
    description="Learn about X",
    agent_type=AgentType.RESEARCH,
    priority=Priority.NORMAL
)
```

### 2. Decision Making
```python
decision = await decision_engine.evaluate_task(task)
# Groq analyzes: Should we do this? When? How?
```

### 3. Mode-Based Routing
```python
if mode == INTERACTIVE:
    present to user, wait for approval
elif mode == AUTONOMOUS:
    execute immediately
else:  # SUPERVISED
    execute, ask only if critical
```

### 4. Agent Dispatch
```python
agent = agent_manager.get_agent(task.agent_type)
result = await agent.execute(task)
```

### 5. Result Storage
```python
task.status = COMPLETED
task.result = result
completed_tasks.append(task)
context.update_from_completed_task(task)
```

## Workflow Execution Flow

### 1. Workflow Definition
```python
workflow = Workflow("Research & Report")
workflow.add_step("research", RESEARCH, handler=...)
workflow.add_step("analyze", RESEARCH, depends_on=["research"], ...)
workflow.add_step("write", ASSISTANT, depends_on=["analyze"], ...)
```

### 2. Dependency Resolution
- Topological sort of steps
- Check for cycles
- Validate dependencies

### 3. Step Execution
- For each step:
  - Check dependencies are satisfied
  - Get agent for step type
  - Execute with timeout
  - Store results
  - Pass to next step

### 4. Workflow Completion
- All steps succeeded: COMPLETED
- Any step failed: FAILED
- User cancelled: CANCELLED

## Performance Considerations

### CPU Usage Optimization
- Batch similar operations
- Use worker threads for I/O
- Lazy load models
- Cache frequently used data

### Memory Management
- Bounded memory histories (max 100 items)
- Clean up old tasks periodically
- Streaming responses from Groq
- Efficient context aggregation

### Decision Latency
- Target: <1 second decisions
- Groq API: 1-3 seconds typically
- Cache common decisions
- Parallel evaluation if possible

## Security & Privacy

### Access Control
- Plugin permission system
- Agent capability restrictions
- Task approval workflow
- Audit logging

### Data Protection
- Encrypt sensitive context
- Local processing for vision
- Secure API key handling
- No unnecessary cloud uploads

### User Privacy
- Only store necessary data
- Allow data deletion
- Transparent about capabilities
- Respect user preferences

## Extension Examples

### Adding Custom Agent
```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("My Agent", AgentType.CUSTOM)
    
    async def process_task(self, task):
        # Implement task processing
        return result

# Register
orchestrator.agent_manager.register_agent(MyAgent())
```

### Creating Custom Workflow
```python
workflow = Workflow("My Workflow")
workflow.add_step("step1", AGENT_TYPE_1, handler=my_handler_1)
workflow.add_step("step2", AGENT_TYPE_2, depends_on=["step1"], handler=my_handler_2)

orchestrator.workflow_engine.register_workflow(workflow)
```

### Building Plugin
```python
class MyPlugin(Plugin):
    async def on_load(self):
        # Initialize
        pass
    
    async def on_enable(self):
        # Activate
        pass
    
    def get_capabilities(self):
        return {"my_tool": "My capability"}

plugin_system.load_plugin(MyPlugin())
```

## Debugging & Monitoring

### System Status
```python
status = orchestrator.get_status()
# Returns: uptime, tasks, decisions, agent metrics, CPU usage
```

### Agent Metrics
```python
metrics = agent_manager.get_agent_metrics()
# Returns: success rates, task counts, performance data
```

### Context Snapshot
```python
context_summary = context_engine.get_summary()
# Human-readable current system state
```

### Decision History
```python
decisions = decision_engine.get_decision_history(limit=10)
# Last 10 decisions with reasoning
```

## Future Enhancements

### Planned Features
1. Multi-user support
2. Distributed agents
3. Machine learning integration
4. Advanced scheduling
5. Predictive workflows
6. Natural language workflow definition

### Research Directions
1. Transfer learning between agents
2. Multi-agent collaboration
3. Hierarchical planning
4. Constraint satisfaction
5. Long-horizon planning

---

**Version**: 5.0.0  
**Status**: Complete  
**Last Updated**: 2026-04-06
