# JARVIS Desktop Chat UI - Quickstart Guide

Convert your terminal JARVIS into a modern desktop chat application!

## 🚀 Quick Start (30 seconds)

```bash
# 1. Navigate to JARVIS directory
cd "F:\python bots\bots or personal projects\jarvis"

# 2. Make sure dependencies are installed
pip install PyQt5

# 3. Launch the GUI
python run_jarvis.py
```

That's it! ✨ The desktop application will launch automatically.

## 📋 What Was Added

### New Files Created

```
ui/
├── chat_bubble.py           ← Individual message bubbles
├── chat_widget.py           ← Chat display area
├── worker_threads.py        ← Background processing threads
├── main_window.py           ← Main application window
├── styles.qss               ← Optional styling
├── CHAT_UI_SETUP.md        ← Full documentation
└── CHAT_UI_QUICKSTART.md   ← This file
```

### Updated Files

- `run_jarvis.py` - Now launches GUI by default
- `ui/__init__.py` - Added new UI components

## 🎯 Features Implemented

✅ **Chat Interface**
- Message bubbles (user right, JARVIS left)
- Auto-scrolling to latest message
- Clean dark theme
- Timestamps for messages

✅ **Voice Integration**
- 🎤 Microphone button for voice input
- 🔴 Visual indicator when listening
- Speech-to-text conversion
- Click to listen, speak naturally

✅ **Non-Blocking Processing**
- "Thinking..." indicator while processing
- UI stays responsive
- Threading for all backend calls
- No freezing during API calls

✅ **Backend Integration**
- Connected to brain.py (Groq LLM)
- Integrated with command_router.py
- Support for system commands
- Error handling and fallbacks

✅ **Status Indicators**
- "Ready" - waiting for input
- "Listening..." - awaiting speech
- "Thinking..." - processing response
- "Executing..." - running command

## 📊 UI Layout

```
┌──────────────────────────────────────┐
│  J.A.R.V.I.S                  Ready  │  ← Header
├──────────────────────────────────────┤
│                                      │
│  🤖 JARVIS: Hello! I'm ready...     │  ← Chat area
│        You: Hi JARVIS!               │
│  🤖 JARVIS: At your service.        │
│                                      │
│  🤖 Thinking...                      │
├──────────────────────────────────────┤
│  [Type your message...] [🎤] [Send]  │  ← Input area
└──────────────────────────────────────┘
```

## 🎮 How to Use

### Text Input
1. Type in the message box
2. Press **Enter** or click **Send**
3. JARVIS processes and responds
4. Response appears in chat

### Voice Input
1. Click the **🎤** button (turns to 🔴)
2. Speak your message clearly
3. Speech converts to text automatically
4. Message is sent and processed
5. Response appears in chat

### System Commands
Try these:
- "What time is it?"
- "What's the date?"
- "Open [app name]"
- "Execute [command]"

## 🔧 Command Line Options

```bash
# Launch GUI (default)
python run_jarvis.py

# Force GUI mode explicitly
python run_jarvis.py --gui
python run_jarvis.py --desktop

# Launch CLI mode instead
python run_jarvis.py --text-only
python run_jarvis.py --no-voice

# Enable debug logging
python run_jarvis.py --debug
python run_jarvis.py -d
```

## 🎨 Customization

### Change Colors

Edit `ui/main_window.py`:

```python
# User message bubble (Line ~120)
message_label.setStyleSheet("""
    QLabel {
        background-color: #0D47A1;  # Change to your color
        color: #FFFFFF;
        ...
    }
""")

# JARVIS message bubble (Line ~135)
message_label.setStyleSheet("""
    QLabel {
        background-color: #2C2C2C;  # Change to your color
        ...
    }
""")
```

### Change Window Size

Edit `ui/main_window.py` line ~65:

```python
self.setGeometry(100, 100, 900, 700)  # width=900, height=700
```

### Change Welcome Message

Edit `ui/main_window.py` line ~200:

```python
self.chat_widget.add_message("Your custom message here", is_user=False)
```

## 🔌 Architecture

```
┌─ run_jarvis.py (entry point)
│
├─→ Check for --gui flag (default: yes)
│
├─→ Launch QApplication (Qt GUI framework)
│
└─→ Create JarvisMainWindow
     │
     ├─→ ChatWidget (message display)
     │   ├─→ ChatBubble (individual messages)
     │   └─→ Scrollable area
     │
     ├─→ Input area (text box + buttons)
     │
     └─→ Worker Threads (background processing)
         ├─→ JarvisWorkerThread (AI queries)
         ├─→ VoiceListenerThread (speech recognition)
         └─→ VoiceOutputThread (TTS output)
```

## 🧵 Threading Model

**Why threading?**
- Keeps UI responsive while processing
- No freezing during Groq API calls
- Smooth user experience

**How it works:**
```
User Input
    ↓
send_message() called
    ↓
Add user message to chat
    ↓
Create JarvisWorkerThread
    ↓
Thread: brain.query(user_input)
    ↓ (non-blocking)
Main thread: Show "Thinking..."
    ↓
Thread: Response ready → emit signal
    ↓
Main thread: Receive signal → Update UI
    ↓
Display JARVIS response
```

## 📱 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Send message |
| **Tab** | Focus to send button |
| **Escape** | Close voice listening (planned) |

## 🐛 Troubleshooting

### GUI doesn't launch

**Error:** "ModuleNotFoundError: No module named 'PyQt5'"

**Fix:**
```bash
pip install PyQt5
```

### No response from JARVIS

**Check 1:** Verify `.env` file has API key
```bash
cat .env | grep GROQ_API_KEY
```

**Check 2:** Enable debug mode
```bash
python run_jarvis.py --debug
```

**Check 3:** Check logs
```bash
tail -f logs/jarvis.log
```

### Voice input not working

**Check 1:** Microphone is connected
```bash
python -c "import speech_recognition as sr; print('Mic works!')"
```

**Check 2:** Enable voice in `.env`
```
ENABLE_VOICE=true
```

**Check 3:** Try text-only first
```bash
python run_jarvis.py --text-only
```

### UI freezes or lags

**Solution 1:** Close other applications to free up resources

**Solution 2:** Check network connection to Groq API

**Solution 3:** Reduce model response size in `.env`
```
GROQ_MAX_TOKENS=512  # was 1024
```

## 📚 File Reference

| File | Purpose |
|------|---------|
| `chat_bubble.py` | Single message display widget |
| `chat_widget.py` | Chat area with scrolling |
| `worker_threads.py` | Background threads for AI, voice, TTS |
| `main_window.py` | Main application window |
| `styles.qss` | Optional global stylesheet |

## 🔄 Integration Points

### With brain.py
```python
response = self.brain.query(user_input, stream=False)
```

### With listener.py
```python
text = self.listener.listen_for_command()
```

### With command_router.py
```python
result = self.command_router.route(user_input)
```

## 🎯 Next Steps

1. **Launch and test:**
   ```bash
   python run_jarvis.py
   ```

2. **Try voice input:**
   - Click the 🎤 button
   - Speak a command
   - Watch it convert to text

3. **Test system commands:**
   - Ask "What time is it?"
   - Say "Execute [system command]"

4. **Customize colors** (optional):
   - Edit color codes in `main_window.py`
   - Restart to see changes

5. **Enable voice output** (optional):
   - Set `ENABLE_VOICE=true` in `.env`
   - JARVIS will speak responses

## 📖 Full Documentation

For complete details, see [CHAT_UI_SETUP.md](./CHAT_UI_SETUP.md)

## ✨ What's Different from CLI

| Feature | CLI | GUI |
|---------|-----|-----|
| Interface | Terminal text | Modern chat bubbles |
| Voice | Command line prompt | Mic button |
| Response time | Shows immediately | "Thinking..." indicator |
| Threading | Blocks on API calls | Non-blocking |
| Visual feedback | Text only | Styled messages |
| Status | Shows status in logs | Status bar |
| Message history | Scrolls off screen | Persistent in chat |
| Mobile-like | No | Yes (chat UI) |

## 🚀 Performance Tips

1. **Faster startup:** Keep chat history  reasonable
2. **Faster responses:** Use shorter model settings
3. **Better UI:** Disable timestamps if needed
4. **Lower CPU:** Reduce logging level

## 💡 Tips & Tricks

**Tip 1:** Use voice input for hands-free operation
```
Click 🎤 → Speak → Automatic processing
```

**Tip 2:** Type complex queries for accuracy
```
Chat bubbles load instantly after typing
```

**Tip 3:** Check debug mode for issues
```bash
python run_jarvis.py --debug
```

## 🎓 Learning Resources

- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Qt Designer](https://doc.qt.io/qt-5/qtdesigner-manual.html)
- [Threading in Python](https://docs.python.org/3/library/threading.html)

## 📝 Known Limitations

- Voice output disabled by default (enable in `.env`)
- Chat history not persisted between sessions
- No user authentication yet
- Single user support only

## 🎉 Features Ready to Go

✅ Chat bubbles
✅ Voice input
✅ Text input
✅ Dark theme
✅ Status indicators
✅ Threading
✅ Error handling
✅ Auto-scrolling
✅ Timestamps
✅ Command routing
✅ Backend integration
✅ Responsive UI

## 📞 Support

**Need help?**
- Check [CHAT_UI_SETUP.md](./CHAT_UI_SETUP.md) for detailed docs
- Run with `--debug` flag for logs
- Check `logs/jarvis.log` for errors
- Review [ui/main_window.py](./main_window.py) source code

---

**Ready to chat? Launch JARVIS now! 🎉**

```bash
python run_jarvis.py
```

Enjoy your new desktop JARVIS! 🤖✨
