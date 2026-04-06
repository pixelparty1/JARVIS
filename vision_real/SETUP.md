# JARVIS Vision - Setup & Installation

Complete setup guide for real-world vision capabilities.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Dependencies](#dependencies)
4. [Hardware Setup](#hardware-setup)
5. [Configuration](#configuration)
6. [First Run](#first-run)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)

---

## System Requirements

### Minimum
- **Python**: 3.8+
- **RAM**: 4GB (8GB recommended)
- **CPU**: Multi-core processor
- **GPU**: Optional (CUDA for faster face detection with CNN)
- **Webcam**: USB or built-in (720p+)

### Recommended
- **Python**: 3.10+
- **RAM**: 8GB+
- **CPU**: 6+ cores
- **GPU**: NVIDIA GPU with CUDA (significant speedup)
- **Webcam**: 1080p+

### Storage
- 2GB for models (face_recognition, deepface, mediapipe)

---

## Installation

### Step 1: Create Virtual Environment

```bash
python -m venv jarvis_vision
source jarvis_vision/bin/activate  # On Windows: jarvis_vision\Scripts\activate
```

### Step 2: Install Core Dependencies

```bash
pip install opencv-python==4.8.0.74
pip install face-recognition==1.3.5
pip install deepface==0.0.75
pip install mediapipe==0.10.0
pip install groq==0.4.0
pip install numpy==1.24.3
```

### Step 3: System-Specific Installation

#### On Windows
```bash
# Install dlib (required for face_recognition)
pip install dlib
```

#### On macOS
```bash
# Using Homebrew is recommended
brew install cmake
pip install dlib
```

#### On Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3-dev libopenblas-dev liblapack-dev libssl-dev
pip install dlib
```

### Step 4: Verify Installation

```bash
python -c "from vision_real import RealWorldJARVIS; print('✅ Vision system ready!')"
```

---

## Dependencies

### Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **opencv-python** | 4.8+ | Video capture and processing |
| **face-recognition** | 1.3+ | Face detection and recognition |
| **deepface** | 0.0.7+ | Emotion detection |
| **mediapipe** | 0.10+ | Hand gesture recognition |
| **groq** | 0.4+ | AI scene understanding |
| **numpy** | 1.24+ | Array processing |

### Optional Libraries

```bash
# CUDA support (GPU acceleration)
pip install torch torchvision

# Performance profiling
pip install py-cpuinfo psutil
```

### Model Files

Models are automatically downloaded on first use:

- **face_recognition**: ~120MB
- **deepface**: ~350MB
- **mediapipe**: ~50MB

Total: ~500MB

---

## Hardware Setup

### Webcam Setup

1. **Connect USB Webcam**
   - Plug in webcam
   - Test with: `cv2.VideoCapture(0)`

2. **Check Device ID**
   ```python
   import cv2
   for i in range(10):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera {i}: Available")
           cap.release()
   ```

3. **Built-in Laptop Webcam**
   - Usually device ID = 0
   - Verify: `Camera 0: Available`

### Lighting Setup

For best results:
- **Front lighting** (face toward light source)
- **Even illumination** (avoid harsh shadows)
- **Bright room** (minimum 300 lux)
- **Avoid backlighting** (light behind you)

### Positioning

- **Distance**: 0.5-1.5 meters from camera
- **Angle**: Slightly above center or neutral
- **Clear view**: Unobstructed face and hands

---

## Configuration

### Basic Configuration

Create `jarvis_config/vision_config.json`:

```json
{
  "camera": {
    "device_id": 0,
    "width": 1280,
    "height": 720,
    "fps": 30,
    "process_every_nth": 2
  },
  "face_recognition": {
    "model": "hog",
    "tolerance": 0.6,
    "enable_learning": true
  },
  "emotion_detection": {
    "model": "fer2013",
    "alert_threshold": 0.7
  },
  "gesture_control": {
    "min_confidence": 0.5,
    "debounce_frames": 5
  },
  "scene_analysis": {
    "groq_model": "openai/gpt-oss-120b",
    "enable_predictions": true
  },
  "privacy": {
    "local_processing_only": false,
    "store_faces": false,
    "encryption": false
  }
}
```

### Advanced Configuration

#### GPU Acceleration

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use GPU 0

from vision_real import RealWorldJARVIS
jarvis = RealWorldJARVIS()
# Will auto-detect GPU
```

#### Performance Tuning

```python
camera = CameraManager(
    process_every_nth=3,  # Process every 3rd frame (faster)
    target_fps=20  # Lower FPS
)
```

#### Privacy Mode

```python
# Don't store face encodings
face_engine = FaceRecognitionEngine()
# Disable face database storage
```

---

## First Run

### Quick Start

```python
from vision_real import RealWorldJARVIS

# Initialize
jarvis = RealWorldJARVIS(
    enable_face_learning=True,
    enable_emotion_alerts=True
)

# Register callbacks
def on_person_detected(data):
    print(f"👋 Hello {data['people']}!")

jarvis.register_callback("person_detected", on_person_detected)

# Run
jarvis.run(display=True)  # Press 'q' to quit
```

### Expected Output

```
🧠 Initializing JARVIS Vision System...

✅ Vision system components initialized
✅ JARVIS Vision System Started
📹 Running JARVIS Vision (press 'q' to quit)

[Camera shows live feed with analysis]

FPS: 28
👋 Face detected: Manan
😊 Happy (92%)
💡 You look happy! Keeping that positive energy...
```

### Add Known Faces

```python
from vision_real import FaceRecognitionEngine

engine = FaceRecognitionEngine()

# Add person from photo
engine.add_person("Alice", "/path/to/alice.jpg")
engine.add_person("Bob", "/path/to/bob.jpg")

# Verify
print(engine.get_known_people())  # ['Alice', 'Bob']
```

---

## Troubleshooting

### Camera Not Opening

**Error**: `❌ Failed to open camera 0`

**Solutions**:
1. Check device ID
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(cap.isOpened())  # Should be True
   ```

2. Check permissions
   ```bash
   # macOS: Grant camera permission in System Preferences
   # Linux: Add to video group
   sudo usermod -aG video $USER
   ```

3. Try different device ID
   ```python
   camera = CameraManager(camera_id=1)
   ```

### Face Recognition Not Working

**Error**: `❌ No faces found` or `No faces detected`

**Solutions**:
1. **Lighting**: Ensure face is well-lit
2. **Distance**: Move closer (0.5-1.5m)
3. **Model**: Try CNN instead of HOG
   ```python
   engine = FaceRecognitionEngine(model="cnn")
   ```
4. **Test with image**
   ```python
   engine.detect_faces(cv2.imread("test.jpg"))
   ```

### Emotion Detection Slow

**Problem**: Emotion detection adds latency

**Solutions**:
1. Process fewer frames
   ```python
   camera = CameraManager(process_every_nth=3)
   ```

2. Use GPU (if available)
   ```bash
   pip install torch
   ```

3. Reduce frame size
   ```python
   frame = resize_frame(frame, scale=0.5)
   ```

### Hand Detection Not Accurate

**Problem**: MediaPipe not detecting hands

**Solutions**:
1. Ensure good lighting on hands
2. Keep hands in clear view
3. Check confidence threshold
4. Try with different hand position

### Memory Usage High

**Problem**: RAM usage keeps increasing

**Solutions**:
1. Limit frame buffer
   ```python
   camera = CameraManager(buffer_size=5)
   ```

2. Reduce emotion detection frequency
   ```python
   camera.register_callback(emotion_check, process_every_nth=10)
   ```

3. Clear old frames periodically
   ```python
   # In your loop
   if frame_count % 100 == 0:
       import gc
       gc.collect()
   ```

---

## Performance Optimization

### Frame Skipping

Process every 2nd or 3rd frame for speed:

```python
camera = CameraManager(process_every_nth=2)  # 50% reduction
# vs
camera = CameraManager(process_every_nth=3)  # 67% reduction
```

### GPU Acceleration

Significantly faster face detection with CNN:

```python
engine = FaceRecognitionEngine(model="cnn")  # ~50x faster with GPU
```

Requires CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Selective Processing

Only run expensive operations when needed:

```python
# Skip emotion detection for unknown faces
if face.name != "Unknown":
    emotion = detector.detect_emotions(frame)
```

### Threading Model

Camera capture runs in background thread:

```python
camera = CameraManager()
camera.start()  # Background thread

# Main thread can do other work
while camera.is_running:
    frame = camera.get_frame()
    # Process at your pace
```

### Benchmarking

Check performance:

```python
stats = camera.get_stats()
print(f"FPS: {stats.fps:.1f}")
print(f"Processed: {stats.processed_frames}/{stats.total_frames}")
print(f"Errors: {stats.errors}")
```

---

## Environment Setup

### Set Groq API Key

```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

Or in Python:

```python
import os
os.environ['GROQ_API_KEY'] = 'your-groq-api-key-here'

from vision_real import SceneAnalyzer
analyzer = SceneAnalyzer()  # Will use env var
```

### Directory Structure

```
jarvis_config/
├── known_faces.pkl          # Face encodings database
├── known_faces/             # Face photos
│   ├── alice.jpg
│   ├── bob.jpg
│   └── ...
├── vision_config.json       # Configuration
└── logs/
    └── vision.log          # Vision system logs
```

---

## Next Steps

1. **Add known faces** - Build face database
2. **Train on your environment** - Adjust lighting/positioning
3. **Setup webhooks** - Integrate with JARVIS agents
4. **Customize responses** - Create personality
5. **Monitor performance** - Use benchmarking

---

## Performance Targets

| Metric | Target | With GPU |
|--------|--------|----------|
| FPS | 20-30 | 30+ |
| Latency | 50-100ms | 20-50ms |
| Detection Rate | 95%+ | 98%+ |
| Memory | 500MB-1GB | 1-2GB |

---

*Last Updated: Phase 7 Vision System*  
*JARVIS Framework v5.0+*
