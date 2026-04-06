# JARVIS System - Quick Start Guide

## ✅ Setup Complete!

Your JARVIS AI system is now configured with:
- ✅ Groq API integration
- ✅ Wake word detection ("wake up")
- ✅ Voice input/output
- ✅ Single entry point (`run_jarvis.py`)

---

## 🚀 Running JARVIS

### Option 1: Text-Only Mode (Recommended First)
```powershell
python run_jarvis.py --text-only
```

### Option 2: With Voice Input
```powershell
python run_jarvis.py
```

### Option 3: Debug Mode
```powershell
python run_jarvis.py --debug
```

---

## 🧪 Testing

Before running the full system, test the setup:

```powershell
python test_setup.py
```

This verifies:
- ✅ Configuration loaded
- ✅ Groq API connected
- ✅ Brain working
- ✅ Listener ready
- ✅ Speaker ready

---

## 📁 Project Structure

```
jarvis/
├── run_jarvis.py          ← MAIN ENTRY POINT
├── config.py              ← Configuration (auto-loads from .env)
├── .env                   ← Your API key and settings
├── brain.py               ← Groq AI engine
├── listener.py            ← Voice recognition
├── speaker.py             ← Text-to-speech
├── command_router.py      ← Command handling
├── test_setup.py          ← Verification test
├── requirements.txt       ← Dependencies
└── logs/                  ← Logs created automatically
```

---

## 🎤 How to Use

1. **Start JARVIS**
   ```
   python run_jarvis.py --text-only
   ```

2. **System shows prompt:**
   ```
   💤 Ready for input (type 'wake up' or your command):
   ```

3. **Say or type the wake word:**
   ```
   > wake up
   ```

4. **JARVIS responds:**
   ```
   🤖 JARVIS: Yes, I'm here.
   🎤 Listening for command (timeout in 60s)...
   ```

5. **Give a command:**
   ```
   > What time is it?
   ```

6. **JARVIS responds:**
   ```
   🤖 JARVIS: The current time is 3:45 PM.
   
   💤 Ready for input...
   ```

---

## 🔧 Configuration

Edit `.env` to customize:

```env
# Wake word
WAKE_WORD=wake up

# Groq model
GROQ_MODEL=openai/gpt-oss-120b

# Features
ENABLE_VOICE=true
DEBUG_MODE=true
```

---

## 🆘 Troubleshooting

### "GROQ_API_KEY not found"
- Create `.env` file with your Groq API key
- Get free key at: https://console.groq.com

### "No microphone found"
- Use `--text-only` mode: `python run_jarvis.py --text-only`
- Or check your audio settings

### "Groq connection failed"
- Check internet connection
- Verify API key is correct
- Check Groq service status

### "Import errors"
- Install dependencies: `pip install -r requirements.txt`
- Run test: `python test_setup.py`

---

## 📝 Example Commands

Once JARVIS is running:

```
> wake up
🤖 JARVIS: Yes, I'm here.

> What's the weather?
🤖 JARVIS: [Groq-powered response]

> Tell me about artificial intelligence
🤖 JARVIS: [Detailed explanation]

> Open notepad
🤖 JARVIS: Opening notepad...
```

---

## 📊 Features Implemented

✅ **Groq Integration** - Powerful LLM reasoning  
✅ **Wake Word Detection** - "Wake up" activation  
✅ **Voice I/O** - Speech recognition & synthesis  
✅ **Single Entry Point** - `run_jarvis.py`  
✅ **Clean Architecture** - Modular design  
✅ **Error Handling** - Graceful fallbacks  
✅ **Debug Mode** - Full logging  
✅ **Configuration** - All in `.env`  

---

## 🚀 Next Steps

1. Run test: `python test_setup.py`
2. Start with text-only: `python run_jarvis.py --text-only`
3. Try voice mode: `python run_jarvis.py`
4. Enable debug: `python run_jarvis.py --debug`
5. Customize in `.env`

---

**Welcome to JARVIS! 🎉**
