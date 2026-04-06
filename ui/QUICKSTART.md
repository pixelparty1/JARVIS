# JARVIS UI - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
# Navigate to UI directory
cd ui

# Install requirements
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Start JARVIS UI with default interactive mode
python launcher.py

# Or run in autonomous mode
python launcher.py --autonomous

# Or run demo mode (show example interactions)
python launcher.py --demo
```

### 3. First Launch
- UI will open in a frameless window
- Dark theme with neon blue/cyan accents
- Click input area or press `Ctrl+Space` to start typing

---

## UI Features

### Chat Interface
- **Ask JARVIS anything** - Natural language interface
- **Typing animation** - See JARVIS "thinking" in real-time
- **Message history** - Scroll through conversation
- **Clear chat** - Reset conversation at any time

### Voice Input (When Enabled)
- **Press microphone icon** or hold `Space` to record
- **Visual waveform** - See audio levels in real-time
- **Auto-send** - Release to submit voice command

### Status Dashboard
- **Current mode**: Interactive / Autonomous / Supervised
- **System state**: Idle / Listening / Thinking / Executing
- **Active agents**: Which agent is handling your request
- **CPU/Memory**: Real-time system metrics

### Side Panels (`Tab` to switch)
- **Tasks**: Current and queued tasks
- **Notes**: Quick notes panel
- **Memory**: Long-term knowledge base snippets
- **Logs**: System event log

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Space` | Focus input area |
| `Enter` | Send message |
| `Shift+Enter` | New line in input |
| `Tab` | Switch side panels |
| `Ctrl+L` | Clear chat |
| `Ctrl+T` | Toggle always-on-top |
| `Esc` | Close application |
| `Space` (hold) | Record voice (when enabled) |
| `Ctrl+S` | Save chat history |

---

## Examples

### Ask a Question
```
You: What's the weather today?
JARVIS: Checking real-time weather data... [processes] It's 72°F and sunny.
```

### Run a Task
```
You: Create a Python script to analyze data
JARVIS: I'll write that for you... [shows generated code]
```

### Enable Autonomous Mode
```bash
python launcher.py --autonomous
# JARVIS will proactively suggest tasks and execute them
```

### Demo Mode
```bash
python launcher.py --demo
# Shows example workflows and interactions
```

---

## Troubleshooting

### UI Not Starting
```bash
# Check PyQt6 installation
python -c "import PyQt6; print(PyQt6.__version__)"

# Verify Python version
python --version  # Should be 3.8+

# Try in verbose mode
python launcher.py --debug
```

### Voice Not Working
```bash
# Install speech recognition
pip install SpeechRecognition pyttsx3

# Check microphone
python -c "import speech_recognition; r = speech_recognition.Recognizer(); m = speech_recognition.Microphone(); print(m)"
```

### Performance Issues
- Close other applications
- Check CPU/memory in task manager
- Switch to "Interactive" mode (uses less resources)
- Disable animations in theme settings (if custom config added)

### Backend Connection Failed
```bash
# Verify AI OS is in the parent directory
# Try running with --local flag
python launcher.py --local

# Check orchestrator is running
ps aux | grep orchestrator
```

---

## Next Steps

1. **Customize Theme**
   - Edit jarvis_ui.py → ThemeManager class
   - Change color scheme (lines ~150-200)

2. **Connect Voice System**
   - Uncomment voice imports in launcher.py
   - Install SpeechRecognition: `pip install SpeechRecognition`

3. **Add Custom Agents**
   - Edit ai_os/agent_manager.py
   - Add your custom agent class
   - Register in launcher.py

4. **Deploy**
   - Use PyInstaller to create .exe (Windows)
   - Create DMG (macOS) or AppImage (Linux)

---

## Support

For issues or feature requests, check:
- README.md - Full feature documentation
- SETUP.md - Detailed installation guide
- ../ai_os/README.md - Backend documentation
- ../vision_real/README.md - Vision system guide

---

**Enjoy JARVIS! 🚀**
