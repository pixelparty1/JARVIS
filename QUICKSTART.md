# 🚀 JARVIS - Quick Setup Guide

## ⏱️ 5-Minute Setup

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Verify Setup (1 minute)
```bash
python main.py
```

### Step 3: Choose Input Method (dialogue)
```
Enable voice input/output? (y/n): n
```

### Step 4: Test JARVIS (3 minutes)
```
📝 You: System information
📝 You: Set timer for 5 seconds
📝 You: Add note titled Test with content JARVIS works!
📝 You: List notes
📝 You: quit
```

✅ Done!

---

## 🎯 Common First Commands to Try

### System
```
system information
list running applications
increase volume by 10
```

### Tasks & Time
```
set timer for 5 minutes
set alarm for 14:30
list timers
```

### Notes
```
add note titled Ideas with content Test JARVIS
list notes
search notes for test
```

### Information
```
search web for python
what's the weather
tell me today's news
```

### Files
```
list files
search files for py
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
python -m pip install --upgrade groq speech_recognition pyttsx3
```

### Issue: "Groq API Error"
**Solution:**
- Check internet connection
- Verify API key in `config.py`
- Check rate limits: `https://console.groq.com`

### Issue: "Audio/Microphone problems"
**Solution:**
```bash
pip install pyaudio
# Windows: might need to install from wheel
# Mac: brew install portaudio
# Linux: apt-get install portaudio19-dev
```

### Issue: Voice not working
**Solution:**
- Start with `voice_enabled=False` and use text
- Check microphone: `Settings > Sound`
- Try: `python test_jarvis.py` (option 2)

---

## 📚 File Structure

```
jarvis/
├── main.py              ← Start here
├── config.py            ← Edit for configuration
├── brain.py             ← AI engine
├── memory.py            ← Persistent storage
├── tasks.py             ← Timers/alarms
├── notes.py             ← Notes management
├── test_jarvis.py       ← Run tests here
├── examples.py          ← Advanced examples
└── README.md            ← Full documentation
```

---

## 🧪 Quick Tests

### Test 1: Text-Based
```bash
python main.py
# Choose: n (no voice)
# Type: system information
```

### Test 2: Quick Demo
```bash
python test_jarvis.py
# Choose: 2 (Quick Demo)
```

### Test 3: Full Suite
```bash
python test_jarvis.py
# Choose: 1 (Full Test Suite)
```

### Test 4: Examples
```bash
python examples.py
# Run any example
```

---

## 💡 Tips & Tricks

### Use Text First
Start with text mode to learn JARVIS commands before trying voice.

### Check Logs
```bash
cat jarvis_log.txt  # See all actions
```

### View Memory
```bash
cat jarvis_memory.json  # See stored data
```

### Reset Everything
```bash
rm jarvis_memory.json clipboard_history.json tasks.json jarvis_log.txt
```

---

## 🎤 Enable Voice (Advanced)

### Windows
1. No additional setup usually needed
2. Check: Settings > Sound > Input devices

### Mac
```bash
pip install pyaudio
```

### Linux
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

Then run:
```bash
python main.py
# Choose: y (enable voice)
```

---

## 📊 Example Workflows

### Morning Briefing
```
system information
what's the weather today
tell me about news
list notes
```

### Note Taking
```
add note titled Meeting Notes with content discussion about AI
search notes for AI
read note note_1
```

### Task Management
```
set timer for 25 minutes
set alarm for 15:30
list timers
list alarms
```

### File Management
```
list files
search files for python
open file /path/to/file
```

---

## 🔐 Safety & Permissions

Default settings are safe. For sensitive operations, JARVIS asks for confirmation:
- Delete file
- Shutdown/Restart
- Uninstall app

To modify permissions, edit `config.py`:
```python
CONFIRMATION_REQUIRED_FOR = [
    "delete_file",
    "uninstall_app",
    "shutdown",
]
```

---

## 📈 Next Steps

1. ✅ Basic setup complete
2. ⏭️ Try `test_jarvis.py` for comprehensive testing
3. ⏭️ Run `examples.py` for advanced usage
4. ⏭️ Read `README.md` for full documentation
5. ⏭️ Customize `config.py` for your preferences
6. ⏭️ Build custom handlers by extending `command_router.py`

---

## 🆘 Getting Help

### Check Documentation
- `README.md` - Full documentation
- `config.py` - Configuration options
- `examples.py` - Usage patterns

### Review Logs
```bash
tail -f jarvis_log.txt
```

### Test Components
```bash
python test_jarvis.py
# Choose specific test
```

---

## 🎉 Success Checklist

✅ Python 3.8+ installed  
✅ Dependencies installed (`pip install -r requirements.txt`)  
✅ API key configured in `config.py`  
✅ JARVIS starts without errors  
✅ Text commands work  
✅ Memory files created (`jarvis_memory.json`)  
✅ Log file created (`jarvis_log.txt`)  

**You're ready to use JARVIS! 🚀**

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Run `python test_jarvis.py` to verify setup
3. Review `config.py` for configuration options
4. Check `jarvis_log.txt` for error messages
5. Try `examples.py` to see working code

---

Happy using JARVIS! 🤖✨
