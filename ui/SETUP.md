"""
JARVIS UI - Setup and Installation Guide

Comprehensive guide for installing and running the futuristic desktop UI
"""

# Installation & Setup Guide for JARVIS Futuristic UI

## 📋 Prerequisites

- Python 3.8+
- Groq API key (for orchestrator)
- PyQt6 installed

## 🚀 Installation

### 1. Install PyQt6

```bash
pip install PyQt6
```

### 2. Verify JARVIS AI OS is installed

```bash
cd jarvis/ai_os
python -m ai_os --help
```

### 3. Verify UI launcher works

```bash
cd jarvis/ui
python launcher.py
```

## 🎨 Quick Start

### Option 1: Direct Python

```bash
cd jarvis/ui
python launcher.py
```

### Option 2: From AI OS directory

```bash
cd jarvis
python -m ui.launcher
```

## 🎯 Features

### Main Chat Interface
- Type messages and press Enter to send
- JARVIS responds in real-time
- Message history with timestamps
- Smooth animations

### Voice Input
- Click microphone button to activate voice input
- (Optional: requires speech recognition library)
- Visual feedback during listening

### Status Bar
- Real-time clock
- System mode indicator (Ready, Listening, Thinking, Executing)
- CPU and memory usage
- Status animation indicator

### Side Panel
Four tabs for different information:
- **Tasks**: Current and past tasks
- **Notes**: Notes and reminders
- **Memory**: JARVIS memory entries
- **Logs**: Real-time system logs

### Dark Futuristic Theme
- Iron Man-inspired design
- Neon cyan/blue accents (#00d9ff)
- Dark background (#0a0e27)
- Smooth rounded corners
- Glowing effects

## ⌨️ Keyboard Shortcuts

### Global
- `Ctrl + Space` - Focus chat input (coming soon)
- `Escape` - Hide side panel (coming soon)

### Chat
- `Enter` - Send message
- `Shift + Enter` - New line in message

## 🎮 UI Controls

### Window
- Drag title bar to move window
- Click icon to minimize (coming soon)
- Click X to close

### Chat
- Type in input field at bottom
- Click "Send" or press Enter
- Click microphone for voice input

### Panels
- Click tabs to switch between Tasks, Notes, Memory, Logs
- Drag splitter to resize panels
- Click X on side panel to collapse

## 🔧 Customization

### Change Theme Color

Edit theme in `jarvis_ui.py`, find the stylesheet section:

```python
# Change color from #00d9ff (cyan) to your color
# Search and replace: #00d9ff → your_color
```

### Change Font

Edit stylesheet:

```python
# In QLabel styles, change font
# font-family: Segoe UI → your_font
```

### Adjust Window Size

Change in `__init__`:

```python
self.setGeometry(100, 100, 1400, 900)
#                   x    y   width height
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"

```bash
pip install PyQt6
```

### "ImportError: cannot import name 'Orchestrator'"

Make sure JARVIS AI OS is in the parent directory:
```
jarvis/
├── ai_os/  ← Orchestrator here
├── ui/     ← Current directory
└── ...
```

### Window appears empty or blank

- Check Python 3.8+ is being used
- Verify PyQt6 is installed
- Try running with verbose output:
  ```bash
  python -u launcher.py
  ```

### Slow performance or freezing

- Reduce message history
- Close other applications
- Update graphics drivers
- Try running on machine with better specs

## 📊 Architecture

```
launcher.py
    ↓
JarvisLauncher class
    ├── create_app() → Create PyQt6 application
    ├── initialize_orchestrator() → Setup JARVIS backend
    └── setup_callbacks() → Connect UI to orchestrator
    
jarvis_ui.py
    ├── MainWindow (main application)
    │   ├── StatusBar (top)
    │   ├── ChatPanel (center)
    │   └── FeaturesPanel (right side)
    │
    ├── ChatPanel
    │   ├── Chat history (scroll area)
    │   └── Input area (text field + buttons)
    │
    ├── StatusBar
    │   ├── Time display
    │   ├── Mode indicator
    │   ├── System metrics
    │   └── Status animation
    │
    └── FeaturesPanel
        ├── Tasks tab
        ├── Notes tab
        ├── Memory tab
        └── Logs tab
```

## 🔗 Integration Points

### UI → Orchestrator

```python
# Chat input sends to orchestrator
self.window.chat_panel.message_submitted.connect(
    lambda text: orchestrator.process_input(InputType.TEXT, text)
)
```

### Orchestrator → UI

```python
# Orchestrator callbacks update UI
orchestrator.register_callback("task_completed", on_task_completed)
```

## 🎨 Design Philosophy

The UI follows these principles:

1. **Minimal**: No clutter, only essential information
2. **Responsive**: Non-blocking operations
3. **Intuitive**: Natural interaction model
4. **Futuristic**: Premium appearance
5. **Accessible**: Clear information hierarchy

## 🚀 Performance Optimization

### Reduce Memory Usage

Limit message history:
```python
self.max_messages = 100  # In ChatPanel
```

### Improve Responsiveness

Use threading for heavy operations:
```python
thread = threading.Thread(target=heavy_task, daemon=True)
thread.start()
```

### Optimize Rendering

Batch UI updates:
```python
# Instead of multiple updates
for msg in messages:
    ui.add_message(msg)  # Bad
    
# Do this
ui.batch_add_messages(messages)  # Good
```

## 📱 Future Features

Planned enhancements:

- Multi-window support
- Floating mini mode
- Voice output (speech synthesis)
- Gesture recognition
- Eye tracking support
- Virtual assistant avatar
- 3D scene visualization
- AR integration
- Mobile companion app

## 🤝 Contributing

To extend JARVIS UI:

1. **Add new widget**: Inherit from QWidget
2. **Add new panel**: Extend FeaturesPanel
3. **Add new theme**: Create new stylesheet
4. **Add new feature**: Extend MainWindow

Example custom widget:
```python
class MyCustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("myWidget")
        # Your implementation
```

## 📞 Support

### Getting Help
1. Check troubleshooting section above
2. Review JARVIS documentation
3. Check Python/PyQt6 documentation
4. Review launcher.py for integration patterns

### Common Issues

**Message not appearing**
- Check orchestrator connection
- Verify callback is connected
- Check console for errors

**UI not responding**
- Check if orchestrator is blocking
- Use threading for long operations
- Reduce message flush frequency

**Visual glitches**
- Update graphics drivers
- Check PyQt6 version
- Verify OS compatibility

## 📚 Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [JARVIS AI OS Documentation](../ai_os/README.md)
- [Style Sheet Reference](#qss-reference)

## 🎓 QSS Reference

JARVIS uses these QSS selectors:

- `#statusBar` - Top status bar
- `#chatScroll` - Chat history area
- `#chatBubble` - Individual messages
- `#inputFrame` - Bottom input area
- `#featuresPanel` - Right side panel
- `#featuresTabs` - Tab widget

## 🔒 Security Notes

- UI runs in same process as orchestrator
- Use secure API key handling
- Validate user input
- Sanitize displayed text

## 📈 Metrics & Monitoring

Monitor UI performance:

```python
# In MainWindow
self.frame_count = 0
self.start_time = time.time()

# Calculate FPS
fps = self.frame_count / (time.time() - self.start_time)
```

## 🎉 You're Ready!

Launch JARVIS:
```bash
python launcher.py
```

Enjoy the futuristic AI experience! 🚀

---

**Version**: 1.0.0  
**Status**: Production-ready  
**Last Updated**: April 2026
