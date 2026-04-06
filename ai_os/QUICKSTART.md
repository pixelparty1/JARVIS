"""
QUICKSTART.md - Get JARVIS AI OS Running in 5 Minutes
"""

# JARVIS AI OS - Quick Start

Transform JARVIS into a full AI Operating System in 5 minutes.

## Installation (2 minutes)

### 1. Prerequisites
```bash
# Requires Python 3.8+
python --version  # Should be 3.8 or higher
```

### 2. Install Dependencies
```bash
pip install groq psutil
```

### 3. Set Groq API Key
```bash
# Get API key from https://console.groq.com
export GROQ_API_KEY=your_key_here

# Or set in Python
import os
os.environ["GROQ_API_KEY"] = "your_key_here"
```

## Basic Usage (3 minutes)

### Option 1: Interactive Mode (Recommended for First Use)

```python
import asyncio
from ai_os import Orchestrator, InputType

async def main():
    # Initialize JARVIS
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Give JARVIS a task
    await orchestrator.process_input(
        InputType.TEXT,
        "Research quantum computing and summarize key concepts"
    )
    
    # Check what JARVIS did
    status = orchestrator.get_status()
    print(f"Tasks completed: {status['tasks_processed']}")
    print(f"Agent performance: {status['agents']}")

asyncio.run(main())
```

### Option 2: Command Line
```bash
cd jarvis/ai_os
python main.py              # Interactive mode - type commands
python main.py --autonomous # Autonomous mode for 5 minutes
python main.py --demo       # Run demo
```

### Option 3: Autonomous Mode

```python
import asyncio
from ai_os import Orchestrator, SystemMode

async def main():
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # JARVIS operates without asking
    orchestrator.set_mode(SystemMode.AUTONOMOUS)
    await orchestrator.run_autonomously(duration_seconds=60)

asyncio.run(main())
```

## Example: Add a Task

```python
from ai_os import Task, AgentType, Priority

# Create a task
task = Task(
    title="Write Python function",
    description="Create a function that sorts a list of dicts by key",
    agent_type=AgentType.CODING,
    priority=Priority.NORMAL,
    context={"language": "python"}
)

# JARVIS executes it
result = await orchestrator.add_task(task)
```

## Example: Run a Workflow

```python
from ai_os import create_research_workflow

# Create workflow
workflow = create_research_workflow()

# Execute
result = await orchestrator.execute_workflow(workflow)

# Check result
print(f"Status: {result['status']}")
print(f"Steps completed: {result['completed_steps']}")
```

## Example: Check Status

```python
status = orchestrator.get_status()

print(f"Mode: {status['mode']}")
print(f"Running: {status['is_running']}")
print(f"Tasks completed: {status['tasks_processed']}")
print(f"Pending tasks: {status['pending_tasks']}")

# Agent performance
print("\nAgents:")
for agent in status['agents']['agents']:
    print(f"  {agent['name']}: {agent['success_rate']:.1%}")
```

## Command Line Usage

### Interactive Mode Commands

```
help              Show available commands
status            Show system status
autonomous        Switch to autonomous mode
task <task>       Add a task (e.g., "task Research AI")
workflow <type>   Run workflow (research, coding, communication)
exit              Exit JARVIS
```

Example session:
```
> task Research machine learning basics
🤔 Decision: Execute task via Research Agent
> status
Mode: interactive
Tasks: 1 completed, 0 pending
> workflow research
Executing Research workflow...
✅ Workflow completed
> exit
```

## What Each Agent Does

1. **Research Agent**
   - Gathers information
   - Analyzes data
   - Creates summaries
   - Example: "Research quantum computing"

2. **Coding Agent**
   - Writes code
   - Debugs errors
   - Tests solutions
   - Example: "Write a Python function to sort lists"

3. **Communication Agent**
   - Composes messages
   - Sends emails
   - Creates reports
   - Example: "Write a summary and send it"

4. **Automation Agent**
   - Creates workflows
   - Automates tasks
   - Manages schedules
   - Example: "Create automation to check email daily"

5. **Personal Assistant**
   - General assistance
   - Answers questions
   - Provides suggestions
   - Example: "What should I do next?"

## Modes Explained

### INTERACTIVE (Default)
- JARVIS asks before acting
- Safe and transparent
- You stay in control
- Use for: Learning, sensitive tasks

### AUTONOMOUS
- JARVIS acts immediately
- No interruptions
- Fast and efficient
- Use for: Background work, demos, trusted tasks

### SUPERVISED
- JARVIS acts on normal tasks
- Asks only for critical decisions
- Good balance
- Use for: Mixed workflows

## Common Patterns

### Pattern 1: Simple Task
```python
await orchestrator.process_input(
    InputType.TEXT,
    "Your task here"
)
```

### Pattern 2: Task with Context
```python
await orchestrator.process_input(
    InputType.TEXT,
    "Write code",
    metadata={"language": "python", "topic": "web scraping"}
)
```

### Pattern 3: Workflow
```python
from ai_os import create_research_workflow

workflow = create_research_workflow()
await orchestrator.execute_workflow(workflow)
```

### Pattern 4: Monitor During Execution
```python
def on_task_completed(data):
    print(f"✅ Completed: {data['task_id']}")

orchestrator.register_callback("task_completed", on_task_completed)
```

## Troubleshooting

### Issue: "Groq not configured"
**Solution**: Set GROQ_API_KEY environment variable
```bash
export GROQ_API_KEY=your_actual_key
```

### Issue: "No agent available"
**Solution**: Agent not registered or wrong type
```python
# Check available agents
status = orchestrator.get_status()
print(status['agents'])
```

### Issue: "Task timeout"
**Solution**: Increase timeout in workflow step
```python
step = workflow.add_step(...)
step.timeout = 600  # 10 minutes
```

### Issue: Memory growing
**Solution**: Reduce history sizes in config
```python
orchestrator.config["max_memory_history"] = 50
```

## Next Steps

1. **Explore**: Try different task types
2. **Create**: Build custom workflows
3. **Extend**: Write your own agents
4. **Automate**: Set up autonomous operations
5. **Integrate**: Connect to external APIs

## Performance Tips

1. **Batch Tasks**: Queue multiple tasks before processing
2. **Use Workflow**: Multi-step tasks are more efficient
3. **Leverage Autonomy**: Let JARVIS decide priorities
4. **Cache Results**: Store results to avoid re-processing
5. **Monitor**: Check metrics to optimize

## Further Reading

- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API docs
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
- [CUSTOMIZATION.md](CUSTOMIZATION.md) - Build custom agents

## Key Concepts

### Task
A unit of work that JARVIS executes
```python
task = Task(title="...", description="...", agent_type=...)
```

### Decision
What JARVIS decides to do about a task
```python
decision = Decision(action="...", priority=..., confidence=...)
```

### Workflow
Multi-step pipeline of tasks
```python
workflow = Workflow("...")
workflow.add_step(...)
```

### Agent
Specialized AI worker that executes tasks
```python
agent = agent_manager.get_agent(AgentType.RESEARCH)
```

### Context
Current system state from all phases
```python
context = context_engine.to_dict()
```

## Real-World Example

Run a complete research project:

```python
import asyncio
from ai_os import Orchestrator, SystemMode, InputType, create_research_workflow

async def research_project():
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Manual research input
    print("📚 Step 1: Quick research")
    await orchestrator.process_input(
        InputType.TEXT,
        "Research modern AI techniques"
    )
    
    # Full workflow
    print("\n🔄 Step 2: Full workflow")
    workflow = create_research_workflow()
    result = await orchestrator.execute_workflow(workflow)
    
    # Check status
    print("\n📊 Results:")
    status = orchestrator.get_status()
    print(f"Total tasks: {status['tasks_processed']}")
    
    # Autonomous research for a bit
    print("\n🤖 Step 3: Autonomous learning (30 seconds)")
    orchestrator.set_mode(SystemMode.AUTONOMOUS)
    await orchestrator.run_autonomously(duration_seconds=30)
    
    # Show final status
    final_status = orchestrator.get_status()
    print(f"\n✅ Final: {final_status['tasks_processed']} tasks processed")

asyncio.run(research_project())
```

---

**You're ready!**  
Start with `python main.py` and explore how JARVIS transforms into a full AI Operating System.

**Questions?** Check the troubleshooting section or review ARCHITECTURE.md for details.
