# ⚡ JARVIS Agent - Quick Start (5 Minutes)

## Step 1: Start the Agent
```bash
python agent_main.py
```

## Step 2: Choose Interactive Mode
```
Select option: 1
```

## Step 3: Try Your First Goal
```
🤖 JARVIS > goal: Get system information
```

**What happens:**
1. ✅ Agent **plans** the task
2. ✅ Agent **executes** the plan using available tools
3. ✅ Agent **observes** the results
4. ✅ Agent **records** what it learned

Output example:
```
📋 Plan Created:
  Step 1: Get system information using system_info tool
  Step 2: Format results for display

⚙️ Executing Plan...
✅ Step 1 completed
✅ Step 2 completed

✨ Goal completed successfully!
```

---

## Try These Goals

### Simple (5-10 seconds)
```
goal: What is the current system time
goal: List files in current directory
goal: Show my clipboard
```

### Multi-Step (10-20 seconds)
```
goal: Search for Python and create a note with results
goal: Get weather and system info
goal: Find and read a file
```

### Complex (20-30 seconds)
```
goal: Research AI and write a comprehensive summary note
goal: Search multiple topics and combine findings
goal: Collect system data and environment info
```

---

## What Can the Agent Do?

✅ **Search & Information**
- Search the web
- Get weather
- Get news headlines

✅ **File Management**
- List files
- Read/write files
- Search files

✅ **Notes & Memory**
- Create notes
- Search notes
- List all notes

✅ **System Control**
- Get system info
- Open applications
- Control volume

✅ **Automation**
- Set timers
- Set alarms
- Copy to clipboard

---

## Commands in Interactive Mode

```
🤖 JARVIS > goal: [your goal here]    # Execute a goal
🤖 JARVIS > status                    # View agent statistics
🤖 JARVIS > tools                     # List available tools
🤖 JARVIS > history                   # View recent goals
🤖 JARVIS > auto [minutes]            # Run autonomous mode
🤖 JARVIS > exit                      # Exit the agent
```

---

## Magic Moments

### 1. Multi-Step Execution
```
goal: Search for Python best practices and save to a file
```
Agent will:
1. Use search_web tool
2. Summarize results
3. Write to file
4. All in one request! 🎯

### 2. Context Awareness
```
goal: Get weather and create a note about today
```
Agent remembers what "today" means and creates contextual note 🧠

### 3. Failure Recovery
If a tool fails, agent automatically:
- Detects the failure
- Plans a different approach
- Retries up to 2 times
- Or adapts the strategy 💪

### 4. Learning
After each goal, agent learns:
- What worked well
- Common patterns
- Best tools for tasks
- Gets smarter over time 📈

---

## 5-Minute Demo

**Time: 0:00**
```bash
python agent_main.py
```
Press Enter

**Time: 0:05**
```
Select: 1
```
Press Enter

**Time: 0:15**
```
🤖 JARVIS > goal: Get system information
```
Press Enter

**Time: 0:30** ✨
Watch the magic! See the plan, execution, and results!

**Time: 1:00**
```
🤖 JARVIS > goal: Search for AI news and create a summary
```
Press Enter

**Time: 2:00** ✨
Multi-step goal completes!

**Time: 2:30**
```
🤖 JARVIS > status
```
See statistics!

**Time: 3:00**
```
🤖 JARVIS > tools
```
See all available tools!

**Time: 4:00**
```
🤖 JARVIS > auto 2
```
Run autonomous mode for 2 minutes!

**Time: 5:00** 🎉
Done!

---

## Advanced: Run Examples

```bash
python agent_examples.py
```

Choose examples to run:
- Simple goals
- Multi-step workflows
- Complex tasks
- Autonomous operation

---

## Need Help?

📖 **Full Documentation**
- Read: `AGENT_GUIDE.md`

📚 **Original Guides**
- Setup: `QUICKSTART.md`
- Troubleshooting: `DEBUGGING.md`

🔍 **See the Code**
- Main: `agent_main.py`
- Loop: `agent_loop.py`
- Planner: `agent_planner.py`
- Executor: `agent_executor.py`

---

## What's Different from Original JARVIS?

**Original (Reactive)**
```
You: "Get system info"
JARVIS: Executes immediately
```

**New (Autonomous)**
```
You: "Research AI and create a summary"
JARVIS: 
  1. Plans what steps to take
  2. Executes each step with best tools
  3. Checks if goal was achieved
  4. Adapts if something fails
  5. Learns for next time
```

✨ **Much more powerful!**

---

## Pro Tips

💡 **Tip 1: Be specific with goals**
```
GOOD: "Search for Python 3.12 release notes"
BETTER: "Search for Python 3.12 features and create a summary"
BEST: "Research Python 3.12, compare to 3.11, and save as note"
```

💡 **Tip 2: Check agent status**
```
🤖 JARVIS > status
Shows how many tasks completed and success rate
```

💡 **Tip 3: View what agent learned**
Agent learns from each execution and improves!

💡 **Tip 4: Run autonomous mode**
```
🤖 JARVIS > auto 15
Let agent run for 15 minutes autonomously
```

💡 **Tip 5: Mixed mode**
```
Execute interactive goal
Then: auto 5
Then: execute another goal
Mix as you like!
```

---

## Keyboard Shortcuts

```
Ctrl+C     Exit immediately
Ctrl+L     Clear screen (in some terminals)
Tab        Auto-complete some commands
Up/Down    Command history
```

---

## Troubleshooting

**Issue: "No module named brain"**
- Solution: Install requirements: `pip install -r requirements.txt`

**Issue: Agent not responding**
- Solution: Check: `🤖 JARVIS > status`
- Could be Groq API timeout

**Issue: Tool not found**
- Solution: Check: `🤖 JARVIS > tools`
- Review tool name in goal

**Issue: Same error repeating**
- Solution: Agent will retry up to 2 times, then adapt strategy

---

## Fun Experiments

1. **Self-Referential Goal**
   ```
   goal: List all available tools and create a summary of capabilities
   ```

2. **Chained Goals**
   ```
   goal: Search for Python, then summarize, then save to file
   ```

3. **Learning Test**
   ```
   goal: [complex goal]
   status
   goal: [similar goal]
   status
   See success rate improve!
   ```

4. **Autonomous Exploration**
   ```
   auto 10
   Watch agent suggest and execute tasks automatically
   ```

---

## Ready?

```bash
python agent_main.py
```

**Select: 1**

**Type:**
```
goal: Get system information
```

**Press Enter and watch! 🚀**

---

**You've got this! 🤖✨**

The JARVIS Agent System is designed to be:
- ⚡ **Fast** - Execute complex goals in seconds
- 🧠 **Intelligent** - Plans and adapts automatically
- 📈 **Learning** - Gets smarter with each execution
- 🔧 **Powerful** - 25+ built-in tools
- 😊 **Intuitive** - Just speak your goal!

**Let's go! 🚀**
