# 🐛 JARVIS Debugging Guide

## 🔍 Debugging Checklist

Use this guide to troubleshoot JARVIS issues.

---

## Installation Issues

### Issue: "No module named 'groq'"
```bash
# Solution 1: Reinstall requirements
pip install -r requirements.txt

# Solution 2: Install groq directly
pip install groq

# Solution 3: Upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "No module named 'speech_recognition'"
```bash
pip install SpeechRecognition
```

### Issue: "No module named 'pyaudio'"
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Mac
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Issue: "No module named 'pyttsx3'"
```bash
pip install pyttsx3
```

---

## API Issues

### Issue: "Groq API KeyError"
**Diagnosis:**
```python
# In Python shell
from groq import Groq
client = Groq(api_key="YOUR_KEY")
```

**Solution:**
1. Check `config.py` - API key must be valid
2. Get new key from: https://console.groq.com
3. Test: `pip install groq` and `from groq import Groq`

### Issue: "Groq API connection timeout"
**Solutions:**
- Check internet connection: `ping google.com`
- Check API status: `https://status.groq.com`
- Retry with: `python main.py` (exponential backoff)

### Issue: "Rate limit exceeded"
**Solutions:**
- Wait before making more requests
- Check quota: https://console.groq.com/keys
- Upgrade plan if needed

---

## Voice Issues

### Issue: "Microphone not found"
**Diagnosis:**
```python
import pyaudio
p = pyaudio.PyAudio()
print(p.get_device_count())  # Count of devices
```

**Solutions:**
1. Check OS settings: Settings > Sound > Input
2. Plug in microphone
3. Try different USB port
4. Update audio drivers

### Issue: "Speech recognition fails"
**Diagnosis:**
```bash
python test_jarvis.py
# Choose: 1 (Full Test Suite)
# See if voice test works
```

**Solutions:**
- Speak clearly and slowly
- Reduce background noise
- Check microphone sensitivity
- Try: `SPEECH_RECOGNITION_TIMEOUT = 15` in config.py

### Issue: "Text-to-speech not audible"
**Diagnosis:**
```python
from speaker import VoiceSpeaker
speaker = VoiceSpeaker()
speaker.speak("Test sound")
```

**Solutions:**
1. Check volume: `increase volume by 50`
2. Test speakers separately
3. Try different voice rate in config.py

---

## Memory Issues

### Issue: "Memory file corrupted"
**Solution:**
```bash
# Backup old file
cp jarvis_memory.json jarvis_memory.json.bak

# Reset memory
rm jarvis_memory.json

# JARVIS will create new file on next run
python main.py
```

### Issue: "Notes not persisting"
**Diagnosis:**
```bash
cat jarvis_memory.json | grep -i note
```

**Solutions:**
1. Check file permissions: `chmod 644 jarvis_memory.json`
2. Ensure disk has free space
3. Check `MEMORY_FILE` path in config.py

### Issue: "Clipboard history not working"
```bash
# Check clipboard file
cat clipboard_history.json

# If corrupted, reset
rm clipboard_history.json

# Restart JARVIS
python main.py
```

---

## Command Issues

### Issue: "Command not recognized"
**Debug Steps:**
1. Check spelling: `list files` not `list file`
2. Run `test_jarvis.py` to verify system
3. Check intent parsing:
   ```python
   from brain import JarvisBrain
   brain = JarvisBrain()
   intent = brain.parse_intent("Your command")
   print(intent)
   ```

### Issue: "Intent parsing wrong"
**Solution:**
```python
# In config.py, lower TEMPERATURE for accurate parsing
TEMPERATURE = 0.3  # Lower = more consistent
```

### Issue: "Multi-command not working"
**Debug:**
```python
# Edit main.py and add logging
print(f"Parsed intent: {intent_data}")
print(f"Handler available: {intent in self.handlers}")
```

---

## Performance Issues

### Issue: "JARVIS responds slowly"
**Solutions:**
1. Check internet speed: https://speedtest.net
2. Reduce MAX_TOKENS in config.py
3. Reduce CONVERSATION_HISTORY_LIMIT
4. Check if other processes hogging CPU

### Issue: "High memory usage"
**Solutions:**
1. Clear old notes: `jarvis_log.txt` can grow large
2. Limit clipboard history: `MAX_CLIPBOARD_ENTRIES`
3. Clear conversation history: `brain.clear_history()`

### Issue: "Slow file search"
**Solutions:**
```python
# In config.py
WEB_SEARCH_TIMEOUT = 5  # Reduce timeout
MAX_CLIPBOARD_ENTRIES = 20  # Reduce history
```

---

## Enable Debug Mode

### Step 1: Edit config.py
```python
DEBUG = True
PRINT_STREAM = True
LOG_LEVEL = "DEBUG"
ENABLE_LOGGING = True
```

### Step 2: Run with logging
```bash
python main.py
# Watch logs:
tail -f jarvis_log.txt
```

### Step 3: Check detailed output
```
[2024-04-06 10:30:45] Processing command: open chrome
[2024-04-06 10:30:46] Parsed intent: open_app
[2024-04-06 10:30:46] Executing handler: _handle_open_app
[2024-04-06 10:30:47] Result: ✅ Opening chrome
```

---

## Common Error Messages

### "AttributeError: 'NoneType' object has no attribute"
**Cause:** Null reference error  
**Debug:**
```bash
python -m pdb main.py
# Step through code
```

### "FileNotFoundError: [Errno 2] No such file or directory"
**Cause:** Missing configuration file  
**Solutions:**
1. Check config.py exists
2. Verify file paths in config.py
3. Use absolute paths not relative

### "ConnectionError: No address associated with hostname"
**Cause:** API connection failure  
**Solutions:**
1. Check internet connection
2. Check API endpoint in config.py
3. Try: `python -c "import socket; socket.create_connection(('api.groq.com', 443))"`

---

## Testing & Verification

### Test Each Component
```bash
# Test 1: Brain (AI)
python -c "from brain import JarvisBrain; b = JarvisBrain(); print('✓ Brain OK')"

# Test 2: Memory
python -c "from memory import Memory; m = Memory(); m.set_preference('test', 'ok'); print('✓ Memory OK')"

# Test 3: Tasks
python -c "from tasks import TaskManager; t = TaskManager(); print('✓ Tasks OK')"

# Test 4: Router
python -c "from command_router import CommandRouter; r = CommandRouter(); print('✓ Router OK')"

# Test 5: Full System
python test_jarvis.py
```

### Verify Installation
```bash
python -c "
import sys
print('Python:', sys.version)

packages = ['groq', 'speech_recognition', 'pyttsx3', 'psutil', 'requests']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg}')
    except ImportError:
        print(f'✗ {pkg} - MISSING')
"
```

---

## Data Corruption Recovery

### If jarvis_memory.json is corrupted
```bash
# View the file
cat jarvis_memory.json

# Try to fix (if it's JSON formatting)
python -m json.tool jarvis_memory.json > fixed.json
mv fixed.json jarvis_memory.json

# Or reset completely
rm jarvis_memory.json
# JARVIS will recreate it
```

### If multiple files corrupted
```bash
# Reset everything
rm jarvis_*.json clipboard_*.json tasks.json jarvis_log.txt

# Restart
python main.py
```

---

## Logging & Monitoring

### Enable Full Logging
```python
# config.py
ENABLE_LOGGING = True
LOG_LEVEL = "DEBUG"
PRINT_STREAM = True
```

### View Logs in Real-Time
```bash
tail -f jarvis_log.txt
```

### Analyze Logs
```bash
# Count commands
grep "Set preference\|Added note\|Created timer" jarvis_log.txt | wc -l

# Find errors
grep "Error\|Failed\|Exception" jarvis_log.txt

# Recent actions
tail -20 jarvis_log.txt
```

---

## Network Debugging

### Check Groq API Connection
```python
import socket
try:
    socket.create_connection(("api.groq.com", 443), timeout=5)
    print("✓ Groq API reachable")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Test DNS
```bash
nslookup api.groq.com
# Should resolve to IP address
```

### Test API Key
```python
from groq import Groq
from config import GROQ_API_KEY

try:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "test"}],
        max_completion_tokens=10
    )
    print("✓ API key valid")
except Exception as e:
    print(f"✗ API error: {e}")
```

---

## Performance Profiling

### Profile a Command
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

from main import JARVIS
jarvis = JARVIS(use_voice=False)
jarvis.process_text_input("System information")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

### Memory Profiling
```python
from memory_profiler import profile

@profile
def test_function():
    from main import JARVIS
    jarvis = JARVIS(use_voice=False)
    jarvis.process_text_input("test")

test_function()
```

---

## Getting Help

### 1. Check Logs
```bash
tail -50 jarvis_log.txt
```

### 2. Run Diagnostics
```bash
python test_jarvis.py  # Run full suite
```

### 3. Check Config
```bash
python -c "from config import *; print('DEBUG:', DEBUG)"
```

### 4. Verify Requirements
```bash
pip list | grep -E "groq|speech|pyttsx|psutil"
```

### 5. Test Minimal Example
```python
from brain import JarvisBrain
brain = JarvisBrain()
print(brain.query("Hello"))
```

---

## Reset JARVIS Completely

```bash
# Remove all data
rm -f jarvis_memory.json
rm -f clipboard_history.json
rm -f tasks.json
rm -f jarvis_log.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Start fresh
python main.py
```

---

## 📞 Still Need Help?

1. Check README.md for full documentation
2. Review examples.py for usage patterns
3. Check QUICKSTART.md for common tasks
4. Run test_jarvis.py with different options
5. Enable DEBUG mode and check logs
6. Verify all modules load correctly

---

Good luck debugging! 🚀

Remember: Most issues are related to missing dependencies or API configuration.  
Start with `pip install -r requirements.txt` and verify your API key!
