# JARVIS Desktop Chat Application

Modern PyQt5-based desktop chat interface for JARVIS AI system.

## Features

✨ **Modern Chat Interface**
- Clean, intuitive chat bubbles
- User messages on the right (blue)
- JARVIS responses on the left (gray)
- Auto-scrolling to latest message
- Timestamps for each message

🎤 **Voice Integration**
- Click-to-speak microphone button
- Real-time speech recognition
- Voice input displayed in chat
- Optional text-to-speech output
- Visual indicators (listening, thinking, executing)

⚡ **Non-Blocking UI**
- Threading for AI processing
- No UI freezing during API calls
- "Thinking..." indicator during processing
- Smooth message handling

🎨 **Dark Theme**
- Professional dark interface (#121212 background)
- Easy on the eyes
- Modern styling with rounded corners
- Color-coded messages

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or specifically for the UI:

```bash
pip install PyQt5 groq python-dotenv SpeechRecognition pyttsx3
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
ENABLE_VOICE=true
DEBUG_MODE=false
```

## Usage

### Launch GUI (Default)

```bash
python run_jarvis.py
```

This starts the desktop chat application automatically.

### Launch CLI Mode

```bash
python run_jarvis.py --text-only
```

### Launch with Debug Output

```bash
python run_jarvis.py --debug
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--gui` | Force GUI mode (default) |
| `--desktop` | Alias for GUI mode |
| `--text-only` | CLI mode with text input only |
| `--no-voice` | Disable voice (CLI mode) |
| `--debug` | Enable debug logging |
| `-d` | Short form of debug |

## Architecture

### File Structure

```
ui/
├── __init__.py              # Package initialization
├── main_window.py           # Main application window
├── chat_widget.py           # Chat display area
├── chat_bubble.py           # Individual message bubble
├── worker_threads.py        # Threading for backend calls
├── styles.qss              # Optional stylesheet
└── SETUP.md                # This file
```

### Components

#### `JarvisMainWindow` (main_window.py)
- Main application window
- Manages overall UI layout
- Handles user interactions
- Manages worker threads
- Updates status indicators

#### `ChatWidget` (chat_widget.py)
- Displays chat messages
- Handles message bubbles
- Auto-scrolls to latest message
- Shows thinking indicators
- Clears chat on demand

#### `ChatBubble` (chat_bubble.py)
- Individual message display
- Styling based on sender
- Timestamp display
- Word wrapping

#### `Worker Threads` (worker_threads.py)
- `JarvisWorkerThread`: AI query processing
- `VoiceListenerThread`: Speech recognition
- `VoiceOutputThread`: Text-to-speech output

## Usage Examples

### Basic Chat

1. Launch the application: `python run_jarvis.py`
2. Type a message in the input box
3. Press Enter or click Send
4. JARVIS processes and responds
5. Response appears in chat

### Voice Input

1. Click the 🎤 (microphone) button
2. Button changes to 🔴 (recording)
3. Speak your message
4. Speech is converted to text
5. Message appears in chat and is sent

### System Commands

JARVIS supports system commands:
- "What time is it?" - Current time
- "What's the date?" - Current date
- "Open [application]" - Launch application
- "Execute [command]" - Run system command

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send message |
| Tab | Focus to send button |
| Ctrl+L | Clear chat (future feature) |

## Styling

### Dark Theme Colors

| Element | Color | Hex |
|---------|-------|-----|
| Background | Very Dark Gray | #121212 |
| Header | Dark Gray | #1E1E1E |
| Input Back | Medium Gray | #2C2C2C |
| User Message | Deep Blue | #0D47A1 |
| JARVIS Message | Medium Gray | #2C2C2C |
| Voice Button | Green | #4CAF50 |
| Send Button | Deep Blue | #0D47A1 |
| Accent (Focus) | Bright Blue | #1976D2 |

### Customizing Colors

Edit `main_window.py` to change colors:

```python
# User message bubble
message_label.setStyleSheet("""
    QLabel {
        background-color: #0D47A1;  # Change this
        color: #FFFFFF;
        ...
    }
""")
```

## Threading & Performance

The UI uses threading to prevent freezing:

```
User Input
    ↓
JarvisMainWindow.send_message()
    ↓
Create JarvisWorkerThread
    ↓
Thread runs: brain.query(input)
    ↓
Thread emits: response_ready signal
    ↓
Main thread receives signal → Update UI
```

This ensures the UI stays responsive while processing AI queries.

## Error Handling

The application handles:
- **Empty input**: Silently ignores
- **API failure**: Shows error message in chat
- **Voice failure**: Displays error and returns to ready state
- **Thread errors**: Logs errors and maintains UI responsiveness

## Troubleshooting

### PyQt5 Not Found

```bash
pip install PyQt5
```

### Voice Not Working

1. Check microphone is connected
2. Verify `ENABLE_VOICE=true` in `.env`
3. Test with: `python run_jarvis.py --text-only`

### API Key Issues

1. Verify `GROQ_API_KEY` is set in `.env`
2. Check key is valid at console.groq.com
3. Restart application after changing `.env`

### Performance Issues

1. Close other applications
2. Check CPU usage: `python run_jarvis.py --debug`
3. Verify network connection for Groq API

## Development

### Adding Features

1. Modify `JarvisMainWindow` for UI changes
2. Update `worker_threads.py` for backend logic
3. Edit styling in `main_window.py` or `styles.qss`

### Debugging

Enable debug mode to see detailed logs:

```bash
python run_jarvis.py --debug
```

View logs:

```bash
tail -f logs/jarvis.log
```

## Configuration

### Environment Variables

See `.env.example`:

```env
# Groq API
GROQ_API_KEY=your_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TEMPERATURE=0.7

# Voice
ENABLE_VOICE=true
WAKE_WORD=jarvis
VOICE_ENGINE=pyttsx3

# System
DEBUG_MODE=false
LOG_LEVEL=INFO
```

## Performance Tips

1. **Reduce AI response time**: Lower `GROQ_MAX_TOKENS` in config
2. **Faster UI updates**: Disable timestamps if needed
3. **Better responsiveness**: Use threading (already implemented)
4. **Reduce memory**: Limit chat history (optional enhancement)

## Future Features

- 📝 Chat history persistence
- 🎙️ Voice output for responses
- 🎨 Customizable themes
- 📊 Usage statistics
- 🔔 Notification system
- 👥 Multi-user support
- 🔐 User authentication

## FAQ

**Q: Can I use this with other LLM models?**
A: Yes, modify `brain.py` to use different APIs.

**Q: How do I save chat history?**
A: Chat is currently session-based. Persistence is a future feature.

**Q: Can I customize colors?**
A: Yes, edit the stylesheet in `main_window.py`.

**Q: Does it work on macOS/Linux?**
A: Yes, PyQt5 is cross-platform. Voice recognition may require additional setup.

**Q: How do I report bugs?**
A: Check GitHub issues or submit detailed error logs.

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/pixelparty1/JARVIS/issues
- Documentation: See README.md in project root

## License

See LICENSE file in project root.

---

**Happy chatting with JARVIS! 🤖**
