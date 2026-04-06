# 🤖 JARVIS - Advanced AI Assistant

A scalable, modular AI assistant built with Python and Groq API. Features voice/text interaction, system control, task management, memory, web search, and automation.

## 🎯 Features

### ✅ Core MVP Features (Implemented)

1. **🖥️ System Control**
   - Open/close any application
   - Volume control
   - System information
   - Shutdown/Restart system
   - List running applications

2. **📝 Command Parsing & Routing**
   - Natural language to intent conversion using Groq
   - Intelligent command routing
   - Multi-command support
   - Fallback conversational AI

3. **⏰ Task Management**
   - Timers (with background monitoring)
   - Alarms (scheduled notifications)
   - Persistent task storage
   - Task history

4. **💾 Memory System**
   - User preferences storage
   - Command history
   - Notes management
   - Reminders
   - JSON-based persistence

5. **📝 Notes System**
   - Create/edit/delete notes
   - Tag-based organization
   - Search functionality
   - AI-powered summarization

6. **📋 Clipboard Manager**
   - Clipboard history tracking
   - Clipboard monitoring
   - Search clipboard history
   - Copy/paste automation

7. **📂 File Management**
   - File listing and navigation
   - File search
   - File/folder operations
   - File information retrieval

8. **🌐 Web Search & Summarization**
   - Web search capability
   - Weather information
   - News briefing
   - Content summarization using AI

9. **🎤 Voice I/O (Optional)**
   - Wake word detection ("Jarvis")
   - Voice command recognition
   - Text-to-speech responses
   - Continuous listening mode

### 🌟 AI Capabilities

- **Groq Integration**: Fast, intelligent responses using GPT-OSS-120B model
- **Context Awareness**: Multi-turn conversation memory (last 10 interactions)
- **Intent Detection**: Converts natural language to structured intents
- **Fallback Intelligence**: Graceful handling of unknown commands

## 📦 Installation

### Prerequisites
- Python 3.8+
- Groq API Key (get it from [console.groq.com](https://console.groq.com))
- Windows/Mac/Linux

### Step 1: Clone or Download
```bash
cd jarvis
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key
The Groq API key is already configured in `config.py`. To use your own:
```python
# Edit config.py
GROQ_API_KEY = "your_api_key_here"
```

### Step 5: Run JARVIS
```bash
python main.py
```

## 🚀 Quick Start

### Text-Based Interaction
```bash
python main.py
# When prompted, choose: "Enable voice input/output? (y/n): n"
# Then type commands:
> open chrome
> set timer for 5 minutes
> add note titled Ideas with content "ML projects"
> search web for python tutorials
```

### Voice-Based Interaction (Linux/Mac with audio setup)
```bash
python main.py
# Choose: "Enable voice input/output? (y/n): y"
# Say "Jarvis" to wake up
# Then speak your command: "Open Chrome", "Set timer", etc.
```

## 💬 Example Commands

### System Control
```
"Open Chrome"
"Close Firefox"
"System information"
"Increase volume by 20"
"Decrease volume"
"List running applications"
"Shutdown in 60 seconds"
"Cancel shutdown"
```

### Task Management
```
"Set timer for 5 minutes"
"Set alarm for 14:30"
"List timers"
"List alarms"
"Cancel timer"
```

### Notes & Memory
```
"Add note titled 'Ideas' with content 'Machine learning projects'"
"List notes"
"Search notes for python"
"Read note note_1"
"Delete note note_1"
```

### Web & Information
```
"Search web for python tutorials"
"What's the weather in New York"
"Tell me today's news"
"Search for climate change articles"
```

### Clipboard
```
"Copy to clipboard: Hello World"
"Get clipboard"
"Clipboard history"
"Search clipboard for important"
```

### File Operations
```
"List files in documents"
"Search files for pdf"
"Open file /path/to/file.txt"
"Open folder ~/Downloads"
"Get file information for document.pdf"
```

## 🏗️ Architecture

```
/jarvis
├── main.py                    # Entry point
├── brain.py                   # Groq AI integration
├── listener.py               # Voice input (Speech Recognition)
├── speaker.py                # Voice output (TTS)
├── command_router.py         # Intent detection & routing
├── system_control.py         # OS-level actions
├── memory.py                 # Persistent memory (JSON)
├── tasks.py                  # Timers & alarms
├── notes.py                  # Notes management
├── web_search.py            # Web search & summarization
├── clipboard_manager.py      # Clipboard history
├── file_manager.py          # File operations
├── config.py                # Configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🔌 Module Overview

### brain.py
- Groq API integration
- Conversation history management
- Intent parsing with JSON output
- Streaming response handling

### listener.py & speaker.py
- Voice input recognition
- Wake word detection
- Text-to-speech output
- Background listening threads

### command_router.py
- Routes commands to handlers
- Manages intent-to-action mapping
- Command history tracking
- Extensible handler registration

### system_control.py
- Application launching/closing
- Volume control
- System information retrieval
- Shutdown/restart commands

### memory.py
- User preferences storage
- Command history
- Notes management with tagging
- Reminders and due dates
- JSON-based persistence

### tasks.py
- Timer creation and monitoring
- Alarm scheduling
- Background thread management
- Task persistence

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# API Settings
GROQ_API_KEY = "your_api_key"
GROQ_MODEL = "openai/gpt-oss-120b"

# Voice Settings
WAKE_WORD = "jarvis"
VOICE_ENGINE = "pyttsx3"
VOICE_RATE = 150

# AI Behavior
SYSTEM_PROMPT = "You are JARVIS..."
TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Memory
MEMORY_DB_TYPE = "json"
MAX_CLIPBOARD_ENTRIES = 50

# Safety
CONFIRMATION_REQUIRED_FOR = ["delete_file", "shutdown"]
```

## 🔐 Safety Features

- Confirmation dialogs for sensitive actions
- Action logging
- Permission system
- Safe command parsing
- Input validation

## 🧩 Extensibility

JARVIS is designed to be easily extended:

### Add New Handler
```python
# In main.py
def _handle_custom_action(self, params, intent_data):
    return "Custom response"

# Register it
self.router.register_handler("custom_action", self._handle_custom_action)
```

### Add New Module
1. Create new file (e.g., `smart_home.py`)
2. Implement feature class
3. Import in `main.py`
4. Register handlers

## 🚀 Future Enhancements

- **AI Agents**: Autonomous task planning and execution
- **Screen Understanding**: Vision-based UI interaction
- **Plugin System**: Community plugin marketplace
- **Smart Automation**: Workflow automation
- **IoT Integration**: Smart home devices
- **Advanced Learning**: Adaptive behavior based on user patterns

## 📊 Data Files Generated

When running JARVIS, these files are created:

```
jarvis_memory.json         # User preferences, notes, reminders
tasks.json                 # Timers and alarms
clipboard_history.json     # Clipboard history
jarvis_log.txt            # Action logs
```

## 🐛 Troubleshooting

### Voice Input Not Working
- Ensure microphone is connected and recognized
- Check audio permissions
- Install required audio packages: `pip install pyaudio`

### Groq API Errors
- Verify API key in config.py
- Check internet connection
- Ensure API rate limits not exceeded

### Import Errors
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`
- Check Python version (3.8+)

## 📝 Logs

Check `jarvis_log.txt` for action history and debugging:
```
[2024-04-06 10:30:45] Set preference: user_name = John
[2024-04-06 10:31:12] Added note: Project Ideas
```

## 🤝 Contributing

To extend JARVIS:
1. Create feature module following existing patterns
2. Implement handler class
3. Register handlers in JARVIS.__init__
4. Add tests and documentation

## 📄 License

Built as a sample project. Feel free to use and modify.

## 💡 Tips & Tricks

### Compound Commands
JARVIS handles multi-part commands:
- "Open Chrome and play music"
- "Set timer for 5 minutes and add a note"

### Command Shortcuts
- `help` - Show command help
- `quit` - Exit JARVIS
- `memory` - View stored memory
- `history` - Show command history

### Voice Tips
- Speak clearly for better recognition
- Use consistent wake word trigger
- Adjust VOICE_RATE if speech is too fast/slow

## 🎯 Success Indicators

✅ JARVIS is working if:
- Commands are recognized and executed
- Responses appear in console
- Memory files are created
- Tasks persist after restart
- Voice input works (if enabled)

---

**Built with ❤️ using Groq API**

Questions? Check `config.py` for all available settings!
