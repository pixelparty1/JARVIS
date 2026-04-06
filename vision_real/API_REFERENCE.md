# JARVIS Vision - API Reference

Complete API documentation for all vision components.

---

## CameraManager

Real-time webcam capture and processing.

### Constructor

```python
CameraManager(
    camera_id: int = 0,
    process_every_nth: int = 2,
    target_fps: int = 30,
    buffer_size: int = 10
)
```

**Parameters:**
- `camera_id`: Webcam device ID (0=default)
- `process_every_nth`: Skip frames for performance
- `target_fps`: Target frames per second
- `buffer_size`: Frame buffer size

### Methods

#### `start() -> bool`
Start camera capture.

```python
camera = CameraManager()
if not camera.start():
    print("Failed to start")
```

#### `stop()`
Stop camera capture.

```python
camera.stop()
```

#### `get_frame() -> Optional[CameraFrame]`
Get current frame.

```python
frame = camera.get_frame()
if frame:
    print(f"Frame #{frame.frame_id}")
```

#### `get_frame_copy() -> Optional[np.ndarray]`
Get copy of frame array.

```python
frame_data = camera.get_frame_copy()
```

#### `register_callback(callback, process_every_nth=1)`
Register frame processing callback.

```python
def process(frame: CameraFrame):
    print(f"Processing frame {frame.frame_id}")

camera.register_callback(process, process_every_nth=5)
```

#### `display_frame(frame=None, window_name="JARVIS Camera") -> bool`
Display frame in window.

```python
camera.display_frame()
key = cv2.waitKey(1)
```

#### `get_stats() -> CameraStats`
Get camera statistics.

```python
stats = camera.get_stats()
print(f"FPS: {stats.fps}")
print(f"Errors: {stats.errors}")
```

#### `get_resolution() -> Tuple[int, int]`
Get frame resolution.

```python
width, height = camera.get_resolution()
```

---

## FaceRecognitionEngine

Face detection and recognition.

### Constructor

```python
FaceRecognitionEngine(
    model: str = "hog",
    tolerance: float = 0.6
)
```

**Parameters:**
- `model`: "hog" (faster) or "cnn" (accurate)
- `tolerance`: Match tolerance (lower=stricter)

### Methods

#### `detect_faces(frame) -> List[Face]`
Detect faces in image.

```python
faces = engine.detect_faces(frame)
print(f"Found {len(faces)} faces")
```

#### `recognize_faces(frame) -> List[Face]`
Detect and recognize faces.

```python
faces = engine.recognize_faces(frame)
for face in faces:
    print(f"{face.name}: {face.confidence:.2%}")
```

#### `add_person(name: str, photo_path: str) -> bool`
Add known person from photo.

```python
engine.add_person("Alice", "photo.jpg")
```

#### `learn_face(name: str, encoding, photo_frame=None) -> bool`
Learn face from encoding.

```python
engine.learn_face("Bob", encoding_array, frame)
```

#### `forget_person(name: str) -> bool`
Remove known person.

```python
engine.forget_person("Charlie")
```

#### `get_known_people() -> List[str]`
Get list of known people.

```python
people = engine.get_known_people()
```

#### `get_person_info(name: str) -> Optional[KnownPerson]`
Get person details.

```python
person = engine.get_person_info("Alice")
print(f"Encodings: {len(person.encodings)}")
```

---

## FaceAnalyzer

High-level face analysis.

### Methods

#### `async analyze_frame(frame) -> Dict`
Analyze frame for faces.

```python
result = await analyzer.analyze_frame(frame)
print(f"Found {result['count']} faces")
print(f"Known: {result['known_count']}")
```

#### `draw_faces(frame, faces) -> np.ndarray`
Draw faces on frame.

```python
frame = analyzer.draw_faces(frame, faces)
cv2.imshow("Faces", frame)
```

---

## EmotionDetector

Emotion detection from faces.

### Constructor

```python
EmotionDetector(model: str = "fer2013")
```

### Methods

#### `detect_emotions(frame, enforce_detection=False) -> List[EmotionResult]`
Detect emotions in frame.

```python
emotions = detector.detect_emotions(frame)
for result in emotions:
    print(f"{result.dominant_emotion}: {result.confidence:.2%}")
```

#### `get_emotion_string(emotion_result) -> str`
Get emoji + emotion text.

```python
text = detector.get_emotion_string(result)
# "😊 Happy (95%)"
```

#### `get_emotion_response(emotion_result) -> str`
Get contextual response.

```python
response = detector.get_emotion_response(result)
# "You look happy! That's great!"
```

#### `draw_emotion(frame, emotion_result) -> np.ndarray`
Draw emotion on frame.

```python
frame = detector.draw_emotion(frame, result)
```

#### `draw_emotion_chart(frame, emotion_result, x, y) -> np.ndarray`
Draw emotion confidence chart.

```python
frame = detector.draw_emotion_chart(frame, result)
```

---

## EmotionMonitor

Monitor emotions over time.

### Constructor

```python
EmotionMonitor(alert_threshold: float = 0.7)
```

### Methods

#### `async analyze_frame(frame) -> Dict`
Analyze frame and get report.

```python
report = await monitor.analyze_frame(frame)
print(f"Emotions: {report['emotions']}")
print(f"Alerts: {report['alerts']}")
print(f"Suggestions: {report['suggestions']}")
```

---

## GestureRecognizer

Hand gesture recognition.

### Methods

#### `detect_hands(frame) -> List[HandDetection]`
Detect hands in frame.

```python
hands = recognizer.detect_hands(frame)
for hand in hands:
    print(f"{hand.handedness}: {hand.gesture.value}")
```

#### `get_gesture_name(gesture) -> str`
Get human-readable gesture name.

```python
name = recognizer.get_gesture_name(Gesture.THUMBS_UP)
# "👍 Thumbs Up"
```

#### `draw_hand(frame, hand) -> np.ndarray`
Draw hand skeleton.

```python
frame = recognizer.draw_hand(frame, hand)
```

---

## GestureController

Map gestures to commands.

### Methods

#### `register_gesture(gesture, callback)`
Register gesture callback.

```python
async def on_thumbs_up():
    print("Approved!")

controller.register_gesture(Gesture.THUMBS_UP, on_thumbs_up)
```

#### `async process_frame(frame) -> Dict`
Process frame and trigger callbacks.

```python
result = await controller.process_frame(frame)
print(f"Triggered: {result['triggered_gestures']}")
```

---

## SceneAnalyzer

Intelligent scene understanding.

### Constructor

```python
SceneAnalyzer(api_key: str = None)
```

### Methods

#### `async analyze_scene(people, emotions, gestures, additional_context=None) -> SceneContext`
Analyze scene and generate context.

```python
context = await analyzer.analyze_scene(
    people=[{"name": "Alice", "confidence": 0.95}],
    emotions=[{"emotion": "happy", "confidence": 0.8}],
    gestures=["open_palm"],
    additional_context={"app_focused": "VSCode"}
)

print(f"Activity: {context.activity}")
print(f"Energy: {context.energy_level}")
print(f"Recommendation: {context.recommendation}")
```

#### `async predict_next_action(context, history=None) -> str`
Predict next user action.

```python
prediction = await analyzer.predict_next_action(context)
```

---

## ContextualResponder

Generate contextual responses.

### Methods

#### `async generate_greeting(people) -> str`
Generate personalized greeting.

```python
greeting = await responder.generate_greeting(
    [{"name": "Alice", "confidence": 0.95}]
)
# "Hello Alice! Good to see you. 👋"
```

#### `async generate_emotion_response(emotions) -> str`
Generate emotion response.

```python
response = await responder.generate_emotion_response(emotions)
```

#### `async generate_gesture_response(gesture) -> str`
Generate gesture response.

```python
response = await responder.generate_gesture_response("thumbs_up")
# "Great! I'm glad you're happy with that. 👍"
```

---

## RealWorldJARVIS

Main vision integration system.

### Constructor

```python
RealWorldJARVIS(
    enable_face_learning: bool = True,
    enable_emotion_alerts: bool = True
)
```

### Methods

#### `start() -> bool`
Start vision system.

```python
if jarvis.start():
    print("✅ Ready")
```

#### `stop()`
Stop vision system.

```python
jarvis.stop()
```

#### `register_callback(event_type, callback)`
Register event callback.

Events:
- `"person_detected"` - Person appears
- `"person_greeting"` - Greeting message
- `"emotion_alert"` - Emotion detected
- `"gesture"` - Gesture recognized
- `"activity_change"` - Activity changes

```python
jarvis.register_callback("person_detected", on_person)
```

#### `async process_frame(camera_frame) -> Optional[VisionFrame]`
Process single frame.

```python
frame = camera.get_frame()
vision = await jarvis.process_frame(frame)
```

#### `draw_analysis(frame, vision_frame) -> np.ndarray`
Draw all analysis on frame.

```python
display_frame = jarvis.draw_analysis(frame, vision)
cv2.imshow("JARVIS", display_frame)
```

#### `async run_async(display=True, duration=None)`
Run async (non-blocking).

```python
await jarvis.run_async(display=True, duration=60)
```

#### `run(display=True)`
Run blocking.

```python
jarvis.run(display=True)  # Press 'q' to quit
```

---

## Data Types

### CameraFrame

```python
@dataclass
class CameraFrame:
    frame: np.ndarray          # Image data
    timestamp: str             # ISO timestamp
    frame_id: int              # Frame number
    width: int                 # Width pixels
    height: int                # Height pixels
    processed: bool = False
    metadata: dict = None
```

### Face

```python
@dataclass
class Face:
    name: str                  # "Alice" or "Unknown"
    encoding: np.ndarray       # 128-dim encoding
    location: Tuple            # (top, right, bottom, left)
    distance: float = 0.0      # Match distance
    confidence: float = 0.0    # 0-1 confidence
    timestamp: str = ""
```

### EmotionResult

```python
@dataclass
class EmotionResult:
    emotions: Dict[str, float]     # All emotion scores
    dominant_emotion: str          # Highest emotion
    confidence: float              # 0-1 confidence
    location: tuple = None         # Face location
    timestamp: str = ""
```

### HandDetection

```python
@dataclass
class HandDetection:
    landmarks: np.ndarray      # 21 hand landmarks
    handedness: str            # "Left" or "Right"
    confidence: float          # 0-1 confidence
    gesture: Gesture           # Recognized gesture
    gesture_confidence: float  # 0-1 gesture confidence
    position: Tuple[int, int]  # Center (x, y)
```

### SceneContext

```python
@dataclass
class SceneContext:
    timestamp: str             # ISO timestamp
    people_present: List[str]  # ["Alice", "Bob"]
    emotions: Dict             # Emotion summary
    gestures: List[str]        # Detected gestures
    activity: str              # What user doing
    energy_level: str          # "high", "medium", "low"
    recommendation: str        # Suggested action
    urgency: str               # "low", "medium", "high"
```

### VisionFrame

```python
@dataclass
class VisionFrame:
    frame_id: int              # Frame number
    faces: List[Dict]          # Detected faces
    emotions: List[Dict]       # Detected emotions
    gestures: List[Dict]       # Detected gestures
    scene_context: Dict        # Scene analysis
    people: List[str]          # People present
    primary_activity: str      # Main activity
    suggestions: List[str]     # Recommendations
    timestamp: str             # ISO timestamp
```

---

## Enums

### Gesture

```python
class Gesture(Enum):
    NONE = "none"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    OPEN_PALM = "open_palm"
    CLOSED_FIST = "closed_fist"
    PEACE_SIGN = "peace_sign"
    OK_SIGN = "ok_sign"
    POINTING = "pointing"
    WAVE = "wave"
    STOP = "stop"
```

---

## Configuration

### Camera Config

```json
{
  "camera": {
    "device_id": 0,
    "width": 1280,
    "height": 720,
    "fps": 30,
    "process_every_nth": 2
  }
}
```

### Face Recognition Config

```json
{
  "face_recognition": {
    "model": "hog",
    "tolerance": 0.6,
    "enable_learning": true
  }
}
```

### Emotion Config

```json
{
  "emotion_detection": {
    "model": "fer2013",
    "alert_threshold": 0.7
  }
}
```

---

## Error Handling

```python
try:
    jarvis = RealWorldJARVIS()
    jarvis.start()
except Exception as e:
    print(f"Error: {e}")
finally:
    jarvis.stop()
```

---

## Performance Metrics

```python
stats = camera.get_stats()
print(f"Frames: {stats.total_frames}")
print(f"FPS: {stats.fps:.1f}")
print(f"Errors: {stats.errors}")

# Typical performance
# CPU only: 20-30 FPS
# GPU enabled: 30+ FPS
```

---

*Last Updated: Phase 7 Vision System*  
*JARVIS Framework v5.0+*
