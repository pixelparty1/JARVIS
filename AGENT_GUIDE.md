# 🤖 JARVIS Autonomous Agent System Guide

## Overview

JARVIS has been upgraded from a reactive assistant to an **autonomous AI agent system** capable of:
- Breaking complex goals into executable steps
- Planning and executing multi-step tasks
- Observing results and adapting dynamically
- Learning from experience
- Operating in fully autonomous mode

---

## 🏗️ Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AGENT LOOP (Main Orchestrator)           │
└─────────────────────────────────────────────────────────────┘
           ↓
┌──────────────────┬──────────────────┬──────────────────┐
│                  │                  │                  │
├──────────────────┴──────────────────┴──────────────────┤
│  1. PLANNER       2. EXECUTOR        3. OBSERVER      │
│  ↓               ↓                  ↓                 │
│  Break goal      Run steps          Check results    │
│  into steps      using tools        Verify success   │
│                                     Decide next      │
└──────────────────┬──────────────────┬──────────────────┘
           ↓
┌──────────────────┬──────────────────┬──────────────────┐
│                  │                  │                  │
├──────────────────┴──────────────────┴──────────────────┤
│     TOOL REGISTRY (Unified Tool Access)              │
│                                                      │
│  System  │  Web  │  Files  │  Notes  │  Tasks      │
└──────────────────────────────────────────────────────┘
```

---

## 🔄 The Agent Loop (Core Algorithm)

### Step 1: PLAN
```
User Goal: "Research AI news and save summary"
    ↓
Planner AI: "I'll break this into steps"
    ↓
Steps:
1. Search web for AI news
2. Extract key points
3. Summarize findings
4. Create note with summary
```

### Step 2: EXECUTE
```
For each step:
  - Call appropriate tool
  - Pass output to next step
  - Store results in shared context
```

### Step 3: OBSERVE
```
After execution:
  - Check if each step succeeded
  - Verify goal achievement
  - Identify any failures
```

### Step 4: REPLAN (if needed)
```
If verification fails:
  - Analyze what went wrong
  - Create new plan
  - Execute again (max 2 retries)
```

---

## 🧠 Core Modules

### 1. Planner (`agent_planner.py`)
**Purpose:** Break goals into executable steps

```python
from agent_planner import Planner

planner = Planner()
plan = planner.plan("Research AI and save notes", context="Focus on recent trends")

# Returns TaskPlan with:
# - steps: List of actions
# - reasoning: Why this approach
# - status: "pending", "completed", "failed"
```

### 2. Tool Registry (`tool_registry.py`)
**Purpose:** Unified access to all tools

```python
from tool_registry import ToolRegistry

registry = ToolRegistry()

# Register a tool
registry.register_tool(
    name="search_web",
    func=lambda query: web.search(query),
    description="Search the web",
    parameters={"query": "string"},
    required=["query"],
    returns="List of results",
    category="web"
)

# Call a tool
success, result = registry.call_tool("search_web", query="AI news")
```

### 3. Executor (`agent_executor.py`)
**Purpose:** Execute planned steps

```python
from agent_executor import Executor

executor = Executor(tool_registry)

# Execute a plan
context = executor.execute_plan(goal, steps)

# Or interactive execution
context = executor.execute_step_by_step(goal, steps)
```

### 4. Observer (`agent_observer.py`)
**Purpose:** Verify execution and provide feedback

```python
from agent_observer import Observer

observer = Observer()

# Observe results
observations = observer.observe(execution_context)

# Check if goal achieved
achieved, explanation = observer.verify_goal_achievement(goal, context)

# Get recommendations
if observer.should_replan(observations):
    # Create new plan
```

### 5. Agent Memory (`agent_memory.py`)
**Purpose:** Store and learn from experience

```python
from agent_memory import AgentMemory

memory = AgentMemory()

# Record outcomes
memory.record_goal_completed(goal, steps_executed, duration)
memory.record_goal_failed(goal, reason, steps_attempted)

# Retrieve similar goals
similar = memory.get_similar_goals(goal)

# Get insights
print(memory.get_memory_insights())
```

### 6. Agent Loop (`agent_loop.py`)
**Purpose:** Orchestrate the complete system

```python
from agent_loop import AgentLoop

agent = AgentLoop()

# Register tools
agent.register_tool(...)

# Execute goal
success, output = agent.execute_goal("Research AI and save notes")

# Run autonomous
agent.run_autonomous_mode(duration_minutes=10)

# Check status
print(agent.get_system_status())
```

---

## 🚀 Quick Start

### 1. Run Agent Main
```bash
python agent_main.py
```

### 2. Choose Mode
```
1. Interactive Mode (control agent)
2. Single Goal (execute one goal)
3. Agent Status (view stats)
4. Autonomous Mode (run continuously)
```

### 3. Execute a Goal
```
🤖 JARVIS > goal: Search for Python tutorials and create a summary note
```

### 4. Watch Agent Work
```
🤔 Planning task: Search for Python tutorials...
✅ Plan created with 3 steps

▶️ Step 1: Search web
🔧 Calling tool: search_web
📤 Output: Found 15 results...

▶️ Step 2: Extract content
...

✅ GOAL ACHIEVED!
```

---

## 💡 Examples

### Example 1: Simple Goal
```python
from agent_main import JARVISAgent

agent = JARVISAgent()
success, result = agent.agent.execute_goal("Get system information")
```

### Example 2: Multi-Step Goal
```python
goal = "Search for machine learning basics and save in a note"
success, result = agent.agent.execute_goal(goal)
```

### Example 3: Complex Workflow
```python
goals = [
    "Search for AI news",
    "Summarize the findings",
    "Save to file",
    "Create backup"
]

for goal in goals:
    agent.agent.execute_goal(goal)
```

### Example 4: Autonomous Mode
```python
agent.agent.run_autonomous_mode(duration_minutes=10)
# Agent runs for 10 minutes, suggesting and executing tasks
```

### Example 5: Check Status
```python
print(agent.agent.get_system_status())
# Shows completed tasks, tool stats, recommendations
```

---

## 🔧 Tool System

### Available Tools by Category

#### System Tools
- `open_app` - Open application
- `close_app` - Close application
- `system_info` - Get system info
- `control_volume` - Control volume

#### Web Tools
- `search_web` - Search the internet
- `get_weather` - Get weather info
- `get_news` - Get news briefing

#### File Tools
- `list_files` - List directory
- `search_files` - Search for files
- `write_file` - Write to file
- `read_file` - Read file

#### Note Tools
- `create_note` - Create note
- `list_notes` - List notes
- `search_notes` - Search notes

#### Task Tools
- `set_timer` - Set timer
- `set_alarm` - Set alarm

#### Utility Tools
- `summarize_text` - Summarize content
- `copy_to_clipboard` - Copy text

---

## 🧠 Agent Memory & Learning

### Memory Structure
```json
{
  "agent_profile": { ... },
  "goals_completed": [ ... ],
  "goals_failed": [ ... ],
  "user_preferences": { ... },
  "learned_patterns": { ... },
  "tool_preferences": { ... },
  "execution_stats": { ... }
}
```

### Learning System
Agent learns from each execution:
- **Success Patterns:** What approaches worked well
- **Failure Analysis:** What didn't work and why
- **Tool Preferences:** Which tools are most reliable
- **User Preferences:** What the user prefers

### Retrieve Similar Goals
```python
memory = agent.agent.memory
similar = memory.get_similar_goals("Search for information")
# Returns past goals with similar keywords
```

---

## 📊 Monitoring & Debugging

### Get System Status
```python
print(agent.agent.get_system_status())
```

### Tool Statistics
```python
stats = agent.agent.tool_registry.get_tool_stats()
print(f"Total tools: {stats['total_tools']}")
print(f"Total calls: {stats['total_calls']}")
print(f"Total errors: {stats['total_errors']}")
```

### Execution History
```python
history = agent.agent.executor.get_execution_history(limit=10)
for execution in history:
    print(f"{execution['goal']}: {execution['status']}")
```

### Memory Insights
```python
print(agent.agent.memory.get_memory_insights())
```

---

## 🔄 Replanning & Adaptation

### Automatic Replanning
When agent detects failure:
1. Analyze what went wrong
2. Create new plan addressing the failure
3. Execute new plan
4. Verify success
5. If still failing → Give up or ask for help

### Replanning Triggers
- Tool execution failure
- Output doesn't match expectations
- Verification check fails

### Max Retries
- Default: 2 replan attempts
- Configurable in agent_loop.py

---

## 🤖 Autonomous Mode

### How It Works
```python
agent.run_autonomous_mode(duration_minutes=10)
```

In autonomous mode:
1. Agent suggests next actions based on context
2. Monitors system state
3. Detects opportunities for task execution
4. Proposes and executes tasks automatically
5. Learns from outcomes

### What Agent Suggests
- "You've been working 2 hours, take a break"
- "Failed goals available for retry"
- "System resources show available capacity"
- "Continue previous interrupted task?"

---

## 📈 Advanced Features

### 1. Context Awareness
```python
goal = "Create summary"
# Agent remembers this refers to previous search
# Automatically uses shared data from previous step
```

### 2. Adaptive Complexity Assessment
```python
complexity = agent.agent.planner.estimate_complexity(goal)
# Returns 1-10 based on goal complexity
# Affects number of steps and parallel execution
```

### 3. Tool Recommendations
```python
tools = agent.agent.get_tool_recommendations("Search for information")
# Returns suggested tools based on task
```

### 4. Failure Recovery
```python
failures = agent.agent.executor.analyze_failures()
# Shows:
# - Total failures
# - Most problematic tools
# - Common error patterns
```

---

## 🔐 Safety Features

### Confirmation for Sensitive Actions
Agent asks before:
- Deleting files
- Shutting down system
- Uninstalling applications

### Timeout Protection
- Each tool call has timeout
- Infinite loops are prevented
- Resource limits are enforced

### Action Logging
Every action is logged:
- What was executed
- Parameters used
- Results achieved
- Time taken
- Any errors

---

## 📚 Running Examples

### Run All Examples
```bash
python agent_examples.py
# Then choose "0" to run all
```

### Specific Examples
```
1. Simple Goal Execution
2. Multi-Step Task Planning
3. Context-Aware Execution
4. Intelligent Replanning
5. Autonomous Mode
6. Tool Discovery
7. Agent Memory & Learning
8. Complex Workflow
9. Adaptive Planning
10. Failure Recovery
11. Tool Statistics
12. Export & Analysis
```

---

## 🎯 Use Cases

### Use Case 1: Research Assistant
```
Goal: "Research quantum computing and create summary notes"

Agent will:
1. Search web for quantum computing
2. Extract key concepts
3. Summarize findings
4. Create organized notes
5. Verify completion
```

### Use Case 2: Task Automation
```
Goal: "Prepare today's brief - get weather, news, and system status"

Agent will:
1. Get weather report
2. Get news briefing on user's interests
3. Get system status
4. Compile report
5. Save to file
```

### Use Case 3: Data Processing
```
Goal: "Find Python libraries, compare them, write comparison notes"

Agent will:
1. Search for Python libraries
2. Read documentation
3. Analyze features
4. Create comparison document
5. Save results
```

---

## 🔍 Troubleshooting

### Agent doesn't execute steps
- Check tool registry: `print(agent.tool_registry.list_tools())`
- Verify tool parameters match schema
- Check tool implementation for errors

### Replanning happening too often
- Adjust `max_replans` in agent_loop.py
- Review tool implementations
- Check expected_output in plan steps

### Memory not persisting
- Verify `agent_memory.json` file exists
- Check file permissions
- Review memory save errors

### Tools failing
- Check tool function signatures
- Verify parameters are correct type
- Review tool error logs

---

## 📊 Performance Tuning

### For Faster Execution
```python
# Reduce planning details
planner.brain.query(prompt, stream=False)

# Limit execution history
executor.keep_history = False
```

### For Better Accuracy
```python
# Lower temperature for planning
temperature = 0.3

# Expect more detailed planning prompts
# Increase max replans
max_replans = 3
```

---

## 🚀 Next Steps

1. **Try Interactive Mode**
   ```bash
   python agent_main.py
   # Choose option 1
   ```

2. **Run Examples**
   ```bash
   python agent_examples.py
   ```

3. **Create Custom Tools**
   - Review tool_registry.py
   - Add your own tools
   - Register with agent

4. **Build Automation**
   - Design workflows
   - Execute complex goals
   - Monitor and refine

---

## 📖 Architecture Diagram

```
USER GOAL
   ↓
AGENT LOOP begins
   ↓
[PLANNER] Breaks goal into steps
   ↓
[EXECUTOR] Runs each step using TOOL REGISTRY
   ↓
   Every step execution:
   - Tool is called
   - Result stored in CONTEXT
   - Output passed to next step
   ↓
[OBSERVER] Checks each result
   ↓
Goal achieved?
   ├─ YES → SUCCESS (record in MEMORY)
   └─ NO → Should replan?
           ├─ YES → Go to PLANNER (refine)
           └─ NO → FAILED (record in MEMORY)
   ↓
[MEMORY] Stores outcome for learning
   ↓
NEXT ITERATION
```

---

## 📚 Key Files

- `agent_main.py` - **Start here** - Main entry point
- `agent_loop.py` - Orchestration logic
- `agent_planner.py` - Task planning
- `agent_executor.py` - Step execution
- `agent_observer.py` - Result verification
- `agent_memory.py` - Learning system
- `tool_registry.py` - Tool management
- `agent_examples.py` - Usage examples

---

## 🎓 Learning Path

1. **Understand the Loop** → Read this guide
2. **Run Examples** → `python agent_examples.py`
3. **Try Interactive** → `python agent_main.py` → Option 1
4. **Execute Goals** → Test various goals
5. **Check Status** → View agent progress
6. **Create Tools** → Add custom functionality
7. **Build Workflows** → Automate complex tasks

---

## 💬 Common Questions

**Q: Can the agent work offline?**
A: Yes, most tools work offline. Web tools require internet.

**Q: How long does execution take?**
A: Typically 5-30 seconds per goal depending on complexity and tools used.

**Q: Can I interrupt execution?**
A: Yes, press Ctrl+C to stop. Agent will record partial completion.

**Q: Does agent forget between sessions?**
A: No, agent_memory.json persists learning across sessions.

**Q: Can I add custom tools?**
A: Yes, use `agent.register_tool()` to add your own functions.

---

**Happy autonomous tasking! 🚀**

For more information, check the code comments or run examples.
