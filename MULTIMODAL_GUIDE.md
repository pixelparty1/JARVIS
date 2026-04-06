# 🤖 JARVIS Multi-Modal Vision System - Complete Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Module Reference](#module-reference)
5. [Usage Examples](#usage-examples)
6. [Advanced Configurations](#advanced-configurations)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Security & Privacy](#security--privacy)
10. [FAQ](#faq)

---

## Overview

### What is Multi-Modal JARVIS?

JARVIS now has **eyes** - it can see and understand your screen in real-time. This enables:

- **Context-aware assistance** - JARVIS knows what you're doing
- **Proactive suggestions** - Smart recommendations based on activity
- **Voice + Vision** - Combine voice commands with screen context
- **Futuristic UI** - Beautiful floating HUD overlay
- **Autonomous workflows** - Agent system uses screen context

### Key Capabilities

```
Screen Analysis Pipeline:
┌─────────────┐
│   Capture   │  📸 Take screenshot every N seconds
└──────┬──────┘
       │
┌──────▼──────┐
│  OCR Text   │  🔤 Extract all visible text
└──────┬──────┘
       │
┌──────▼──────────┐
│   Vision AI     │  🧠 Use Groq to understand context
└──────┬──────────┘
       │
┌──────▼──────────┐
│  Suggestions    │  💡 Get smart recommendations
└──────┬──────────┘
       │
┌──────▼──────────┐
│  HUD Display    │  🎨 Show in floating UI
└──────┬──────────┘
       │
┌──────▼──────────┐
│  Agent System   │  🤖 Execute with context
└─────────────────┘
```

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    JARVIS HUD                           │
│  ┌────────┐ ┌──────────┐ ┌───────────┐ ┌─────────────┐ │
│  │ Status │ │ Messages │ │ Waveform  │ │ Suggestions │ │
│  └────────┘ └──────────┘ └───────────┘ └─────────────┘ │
└────────────────┬──────────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │ Multimodal JARVIS│
        └────────┬────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼───┐ ┌────▼────┐ ┌───▼────┐
│ Vision │ │ Agent   │ │  Voice │
│ System │ │ System  │ │ I/O    │
└────────┘ └─────────┘ └────────┘
     │           │
┌────▼───────────▼────────┐
│  Screen Understanding   │
│  Activity Detection     │
│  Suggestion Generation  │
└─────────────────────────┘
```

### Components

**Vision Module** (`/vision`)
- Screen capture with mss
- OCR with Tesseract
- AI analysis with Groq
- Activity detection

**UI Module** (`/ui`)
- Floating HUD with PyQt5
- Smooth animations
- Voice waveform visualization
- Interactive suggestions

**Integration** (`multimodal.py`)
- Ties everything together
- Manages monitoring loop
- Handles voice + vision
- Connects to agent system

---

## Getting Started

### Quick Installation

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Install Tesseract (Windows)
choco install tesseract

# 3. Verify
python -m vision.screen_capture
```

### First Run

```python
# Start simple monitoring
from multimodal import MultiModalJARVIS

mm = MultiModalJARVIS(enable_hud=True)
mm.start_monitoring()

# Let it run for 30 seconds
import time
time.sleep(30)

# Check activity
summary = mm.get_activity_summary()
print(summary)

mm.close()
```

---

## Module Reference

### Vision Module

#### ScreenCapture
```python
from vision.screen_capture import ScreenCapture

capture = ScreenCapture()

# Capture full screen
screenshot = capture.capture_full_screen()

# Capture with resize
screenshot = capture.capture_full_screen(resize=(800, 600))

# Capture specific monitor
screenshot = capture.capture_monitor(monitor_index=1)

# Save screenshot
path = capture.save_screenshot("my_screenshot.png")

# Get monitor info
info = capture.get_capture_info()

# Configure
capture.set_capture_interval(2.0)
capture.enable_cache(True)
```

#### OCREngine
```python
from vision.ocr import OCREngine

ocr = OCREngine()

# Extract all text
text = ocr.extract_text(screenshot)

# Extract with confidence scores
blocks = ocr.extract_text_with_confidence(screenshot)
for block in blocks:
    print(f"{block.text}: {block.confidence:.2f}")

# Extract URLs
urls = ocr.extract_urls(screenshot)

# Extract emails
emails = ocr.extract_emails(screenshot)

# Extract numbers
numbers = ocr.extract_numbers(screenshot)

# Configure
ocr.set_confidence_threshold(0.7)
ocr.set_languages(['eng', 'fra'])
ocr.toggle_preprocessing(True)
```

#### VisionAnalyzer
```python
from vision.vision_analyzer import VisionAnalyzer
from brain import Brain

brain = Brain()
analyzer = VisionAnalyzer(brain=brain)

# Analyze screen
analysis = analyzer.analyze(text, window_name="VS Code")

# Get results
print(analysis.activity)        # "coding"
print(analysis.context)         # Current activity description
print(analysis.suggestions)     # List of suggestions
print(analysis.confidence)      # 0.0-1.0 confidence score
print(analysis.relevant_tools)  # List of recommended tools

# Get summary
summary = analyzer.get_activity_summary()

# Get pattern
pattern = analyzer.get_activity_pattern()  # Describes activity pattern

# Get next suggestion
next_suggestion = analyzer.get_next_suggestion("coding")
```

### UI Module

#### HUD Manager
```python
from ui.hud import get_hud_manager, HUDMessage

hud = get_hud_manager()

# Display message
hud.display_message("Hello JARVIS!", "info", duration=5)

# Display suggestion
hud.display_suggestion("Summarize this?", callback)

# Set states
hud.set_listening(True)    # Green indicator
hud.set_speaking(True)     # Orange indicator
hud.set_processing(True)   # Purple indicator

# Window control
hud.show()
hud.hide()
hud.toggle_visibility()
```

#### Animations
```python
from ui.animations import Animator, EasingFunction

animator = Animator()

# Create animation
anim_id = animator.animate(
    start=0,
    end=100,
    duration=2.0,
    easing=EasingFunction.EASE_OUT,
    repeat=False,
    on_complete=lambda: print("Done!")
)

# Update
animator.update(delta_time=0.016)

# Get value
value = animator.get_value(anim_id)

# Stop animation
animator.stop(anim_id)
animator.stop_all()
```

#### Waveforms
```python
from ui.waveform import WaveformVisualizer, CircleWaveform

# Linear waveform
waveform = WaveformVisualizer(width=400, height=80, bars=20)
waveform.set_listening()
waveform.update(0.016)
ascii_art = waveform.get_ascii_art()

# Circular waveform
circle = CircleWaveform(radius=50, segments=30)
circle.state = "speaking"
circle.update(0.016)
svg = circle.get_svg()
```

### Multimodal Integration

```python
from multimodal import MultiModalJARVIS
from agent_main import JARVISAgent

# Create with agent
agent = JARVISAgent()
mm = MultiModalJARVIS(agent_system=agent.agent, enable_hud=True)

# Monitoring
mm.start_monitoring()
mm.stop_monitoring()

# Configuration
mm.set_analysis_interval(3.0)
mm.toggle_ocr(True)
mm.toggle_suggestions(True)
mm.toggle_auto_execute(False)

# Voice input
mm.process_voice_input("Summarize this")

# Manual analysis
analysis = mm.screenshot_and_analyze()

# Information
context = mm.get_context()
summary = mm.get_activity_summary()

# Export
mm.export_session("session.json")

# Cleanup
mm.close()
```

---

## Usage Examples

### Example 1: Basic Monitoring

```python
from multimodal import MultiModalJARVIS

mm = MultiModalJARVIS(enable_hud=False)
mm.start_monitoring()

# Monitor for 1 minute
import time
time.sleep(60)

# Get results
summary = mm.get_activity_summary()
print(f"Activities detected: {summary['activities']}")

mm.close()
```

### Example 2: With Agent System

```python
from agent_main import JARVISAgent
from multimodal import MultiModalJARVIS

# Create agent
agent = JARVISAgent()

# Create multi-modal with GUI
mm = MultiModalJARVIS(
    agent_system=agent.agent,
    enable_hud=True
)

# Enable auto-execution
mm.toggle_auto_execute(True)

# Start
mm.start_monitoring()

# Now JARVIS can:
# 1. See what you're doing
# 2. Suggest relevant actions
# 3. Auto-execute suggestions

input("Press Enter to stop...\n")
mm.close()
```

### Example 3: Screenshot Analysis Only

```python
from multimodal import MultiModalJARVIS

mm = MultiModalJARVIS(enable_hud=False)

# One-off analysis
result = mm.screenshot_and_analyze()

if result:
    print(f"Activity: {result['activity']}")
    print(f"Suggestions: {result['suggestions']}")

mm.close()
```

### Example 4: Custom Vision Processing

```python
from vision.vision_analyzer import VisionAnalyzer

class MyAnalyzer(VisionAnalyzer):
    def _detect_activity(self, text, window_name):
        # Custom detection
        if "my_keyword" in text.lower():
            return "my_activity"
        return super()._detect_activity(text, window_name)
    
    def _get_template_suggestions(self, activity):
        if activity == "my_activity":
            return ["Custom suggestion 1", "Custom suggestion 2"]
        return super()._get_template_suggestions(activity)

# Use custom analyzer
analyzer = MyAnalyzer()
analysis = analyzer.analyze(text, window_name)
```

### Example 5: Voice + Screen Context

```python
from multimodal import MultiModalJARVIS
from agent_main import JARVISAgent
from listener import VoiceListener

agent = JARVISAgent()
mm = MultiModalJARVIS(agent_system=agent.agent)
listener = VoiceListener()

mm.start_monitoring()

# Get voice input
audio = listener.listen()  # "Summarize"

# Process with screen context
mm.process_voice_input(audio)
# Automatically uses current screen activity!

mm.close()
```

---

## Advanced Configurations

### Performance Tuning

```python
mm = MultiModalJARVIS()

# Reduce CPU usage
mm.set_analysis_interval(5.0)     # Analyze every 5 seconds
mm.toggle_ocr(False)               # Skip OCR
mm.screen_capture.set_capture_interval(3.0)  # Capture every 3 seconds

# Improve accuracy
mm.ocr_engine.set_confidence_threshold(0.8)  # Higher threshold
mm.ocr_engine.toggle_preprocessing(True)     # Better OCR
mm.set_analysis_interval(2.0)      # More frequent analysis
```

### Custom Detection

```python
from vision.vision_analyzer import VisionAnalyzer

analyzer = VisionAnalyzer()

# Add custom patterns
analyzer.action_patterns['my_action'] = ['keyword1', 'keyword2']
analyzer.app_contexts['my_app'] = 'My Application'
analyzer.suggestion_templates['my_type'] = [
    "Suggestion 1?",
    "Suggestion 2?"
]
```

### Multi-Monitor Setup

```python
from vision.screen_capture import ScreenCapture

capture = ScreenCapture()

# Check available monitors
info = capture.get_capture_info()
print(f"Monitors: {info['monitor_count']}")

# Capture specific monitor
screenshot = capture.capture_monitor(monitor_index=2)
```

### Custom HUD

```python
from ui.hud import JARVISHU D
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

# Create custom HUD
class MyHUD(JARVISHU D):
    def _setup_stylesheet(self):
        # Custom colors
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 60, 0.95);
            }
        """)

hud = MyHUD(app)
hud.show()
sys.exit(app.exec_())
```

---

## Troubleshooting

### Common Issues

**Issue: "No module named pytesseract"**
```bash
pip install pytesseract
```

**Issue: "Tesseract is not installed"**
```bash
# Windows
choco install tesseract

# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr
```

**Issue: HUD doesn't appear**
```bash
# Check PyQt5
pip install PyQt5

# Try headless mode
mm = MultiModalJARVIS(enable_hud=False)

# Check for display
echo $DISPLAY  # Linux only
```

**Issue: Poor OCR accuracy**
```python
# Improve preprocessing
ocr.toggle_preprocessing(True)

# Use multiple languages
ocr.set_languages(['eng', 'fra', 'deu'])

# Increase threshold
ocr.set_confidence_threshold(0.5)  # More permissive
```

**Issue: Agent integration failing**
```python
# Verify agent system
from agent_main import JARVISAgent
agent = JARVISAgent()
success, output = agent.agent.execute_goal("test")

# Pass correct system
mm = MultiModalJARVIS(agent_system=agent.agent)
```

### Debug Mode

```python
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Create multi-modal with verbose
mm = MultiModalJARVIS(enable_hud=True)

# Monitor what's happening
mm.start_monitoring()
print("Debug: Monitoring started")

import time
time.sleep(10)

print("Context:", mm.get_context())
print("Summary:", mm.get_activity_summary())

mm.close()
```

---

## Performance Optimization

### Memory Usage

```python
# Reduce cache
mm.screen_capture.max_cache_size = 5  # Default 10

# Disable caching
mm.screen_capture.enable_cache(False)

# Clear regularly
mm.screen_capture.clear_cache()
```

### CPU Usage

```python
# Lower analysis frequency
mm.set_analysis_interval(10.0)

# Reduce screenshot resolution (default 800x600)
mm.screen_capture.thumbnail_size = (640, 360)

# Disable expensive features
mm.toggle_ocr(False)
mm.toggle_suggestions(False)

# Use async processing
import threading
thread = threading.Thread(target=mm.start_monitoring, daemon=True)
thread.start()
```

### Network Usage

```python
# Cache results
mm.screen_capture.enable_cache(True)

# Batch analysis
# (Only send every Nth analysis to Groq)
results = []
for i in range(5):
    result = mm.screenshot_and_analyze()
    if i % 3 == 0:  # Every 3rd
        results.append(result)
```

---

## Security & Privacy

### Local Processing

```python
# OCR runs locally - no data sent
from vision.ocr import OCREngine
ocr = OCREngine()  # No internet needed

# Screenshot never leaves computer
from vision.screen_capture import ScreenCapture
capture = ScreenCapture()
```

### Selective Sending

```python
# Control what gets analyzed
mm.toggle_ocr(True)   # Extract text locally

# Only send important text
mm.set_analysis_interval(5.0)  # Less frequent

# Can disable analysis
mm.toggle_ocr(False)  # No text extraction
```

### User Consent

```python
# Ask before auto-executing
mm.toggle_auto_execute(False)  # OFF by default

# Manual execution
mm.display_suggestion("Summarize?", callback)
# User clicks to execute
```

### Data Export

```python
# Control exported data
session = mm.export_session("data.json")

# Or selective export
context = mm.get_context()
# Contains: activity, suggestions, timestamp
```

---

## FAQ

**Q: Does JARVIS send my screenshots to servers?**
A: No. Screenshots are processed locally using Tesseract OCR. Only extracted text is sent to Groq API for analysis.

**Q: Can I use this without the HUD?**
A: Yes! Set `enable_hud=False` when creating MultiModalJARVIS.

**Q: What languages does OCR support?**
A: English (eng), French (fra), German (deu), Spanish (spa), Italian (ita), Portuguese (por), Russian (rus), Japanese (jpn), Chinese Simplified (chi_sim), Chinese Traditional (chi_tra), and more.

**Q: How do I extend vision analysis?**
A: Subclass `VisionAnalyzer` and override `_detect_activity()` or other methods.

**Q: Can I use this on multiple monitors?**
A: Yes. Use `screen_capture.capture_monitor(index)` to capture specific monitors.

**Q: How much CPU/memory does it use?**
A: Depends on settings. With defaults: ~5-10% CPU when idle, ~50-100MB RAM. Increase analysis_interval to reduce CPU.

**Q: Can I customize the HUD appearance?**
A: Yes. Edit HUD stylesheets in `ui/hud.py` or subclass `JARVISHU D` for custom UI.

**Q: How do I debug issues?**
A: Enable logging, check console output, and run individual modules separately (e.g., `python -m vision.screen_capture`).

**Q: Is this compatible with existing JARVIS code?**
A: Yes! Multi-Modal is fully compatible with the original system and autonomous agent.

**Q: Can I use this offline?**
A: Screen capture and OCR work offline. Vision analysis requires internet (Groq API).

**Q: How do I report bugs?**
A: Check DEBUGGING.md and multimodal_demo.py for troubleshooting guides.

---

## Next Steps

1. **Try the demo**: `python multimodal_demo.py`
2. **Explore modules**: Review code in `/vision` and `/ui`
3. **Integrate with agent**: Use with `JARVISAgent`
4. **Customize**: Extend analyzers and UI
5. **Deploy**: Add to your workflows

---

**Ready to give JARVIS super vision? 👁️ 🤖**

```bash
python multimodal_demo.py
```

Enjoy the multi-modal experience! ✨
