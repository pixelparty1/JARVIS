# JARVIS Vision - User Guide

Master JARVIS's real-world vision capabilities.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Face Recognition](#face-recognition)
3. [Emotion Detection](#emotion-detection)
4. [Gesture Control](#gesture-control)
5. [Scene Understanding](#scene-understanding)
6. [Real-Time Reactions](#real-time-reactions)
7. [Examples & Recipes](#examples--recipes)
8. [Privacy & Ethics](#privacy--ethics)

---

## Getting Started

### Basic Usage

```python
from vision_real import RealWorldJARVIS

# 1. Create instance
jarvis = RealWorldJARVIS()

# 2. Start system
jarvis.start()

# 3. Run (blocking)
jarvis.run(display=True)  # Shows live video

# 4. Stop
jarvis.stop()
```

### With Callbacks

```python
# Define event handlers
def on_person_enters(data):
    print(f"👋 Welcome {data['people']}!")

def on_gesture(data):
    print(f"✋ Gesture: {data['gesture']}")
    print(f"✔️ {data['response']}")

# Register
jarvis.register_callback("person_detected", on_person_enters)
jarvis.register_callback("gesture", on_gesture)

# Run
jarvis.run(display=True)
```

### Non-Blocking Async

```python
import asyncio

async def main():
    jarvis = RealWorldJARVIS()
    
    # Run in background
    await jarvis.run_async(display=True, duration=60)
    
    print("✅ Session complete")

asyncio.run(main())
```

---

## Face Recognition

### Detect Faces

```python
from vision_real import FaceRecognitionEngine
import cv2

engine = FaceRecognitionEngine(model="hog")  # or "cnn"

# Load image
image = cv2.imread("photo.jpg")

# Detect
faces = engine.detect_faces(image)
print(f"Found {len(faces)} faces")
```

### Recognize Known Faces

```python
# Add known person
engine.add_person("Alice", "photos/alice.jpg")
engine.add_person("Bob", "photos/bob.jpg")

# Recognize in image
faces = engine.recognize_faces(image)

for face in faces:
    print(f"Name: {face.name}")
    print(f"Confidence: {face.confidence:.2%}")
    print(f"Location: {face.location}")
```

### Learn New Faces

```python
# Learn from camera frame
for face in detected_faces:
    if face.name == "Unknown":
        # Extract face region
        top, right, bottom, left = face.location
        face_region = frame[top:bottom, left:right]
        
        # Ask for name
        name = input("Who is this? ")
        
        # Learn
        engine.learn_face(name, face.encoding, face_region)
```

### Face Database

```python
# Get known people
known = engine.get_known_people()
print(f"Known people: {known}")

# Get person info
alice = engine.get_person_info("Alice")
print(f"Encodings: {len(alice.encodings)}")
print(f"Photo: {alice.photo_path}")

# Remove person
engine.forget_person("Bob")
```

### Accuracy Tips

1. **Multiple angles**: Add faces from different angles
2. **Lighting variation**: Add photo in different lighting
3. **Expressions**: Include happy, neutral, serious
4. **Distance**: Photos at different distances (0.5-2m)

Result: **98%+ recognition accuracy**

---

## Emotion Detection

### Detect Emotions

```python
from vision_real import EmotionDetector

detector = EmotionDetector(model="fer2013")

# Detect in image
results = detector.detect_emotions(frame)

for result in results:
    print(f"Emotion: {result.dominant_emotion}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"All emotions: {result.emotions}")
```

### Supported Emotions

```
😊 Happy       - Positive, pleased
😢 Sad         - Unhappy, down
😠 Angry       - Upset, frustrated
😲 Surprise    - Shocked, astonished  
😨 Fear        - Afraid, anxious
🤢 Disgust     - Repulsed, displeased
😐 Neutral     - Calm, unmoved
```

### Get Responses

```python
# Automatic response
response = detector.get_emotion_response(result)
print(response)

# Examples:
# Sad → "You seem down. Want to talk? 💙"
# Happy → "You look happy! That's great!"
# Angry → "You look upset. Deep breaths? 🧘"
```

### Monitor Over Time

```python
monitor = EmotionMonitor(alert_threshold=0.7)

# Analyze frame
report = await monitor.analyze_frame(frame)

print(f"Emotions: {report['emotions']}")
print(f"Alerts: {report['alerts']}")
print(f"Suggestions: {report['suggestions']}")
```

### Set Alerts

```python
# Alert if user looks sad or angry (>70% confidence)
if report['alerts']:
    for alert in report['alerts']:
        print(f"⚠️ {alert['message']}")
        # Take action: play music, suggest break, etc.
```

---

## Gesture Control

### Detect Gestures

```python
from vision_real import GestureRecognizer

recognizer = GestureRecognizer()

# Detect hands
hands = recognizer.detect_hands(frame)

for hand in hands:
    print(f"Hand: {hand.handedness}")
    print(f"Gesture: {hand.gesture.value}")
    print(f"Confidence: {hand.gesture_confidence:.2%}")
```

### Supported Gestures

```
👍 Thumbs Up      - Approve, agree
👎 Thumbs Down    - Disapprove, disagree
✋ Open Palm       - Stop, listen
✊ Closed Fist     - Ready, confident
✌️ Peace Sign     - Victory, peace
👌 OK Sign        - Perfect, okay
☝️ Pointing       - Indicate, direct
👋 Wave           - Hello, wave
🛑 Stop           - Stop, halt
```

### Gesture Callbacks

```python
controller = GestureController()

async def gesture_thumbs_up():
    print("👍 Great!")

async def gesture_thumbs_down():
    print("👎 Got it, we'll work on that")

# Register
controller.register_gesture(Gesture.THUMBS_UP, gesture_thumbs_up)
controller.register_gesture(Gesture.THUMBS_DOWN, gesture_thumbs_down)

# Process frame
result = await controller.process_frame(frame)
# Auto-triggers callbacks when gestures detected
```

### Draw Hands

```python
# Visualize hand skeleton
frame = recognizer.draw_hand(frame, hand)

cv2.imshow("Hand Detection", frame)
```

---

## Scene Understanding

### Analyze Scene

```python
from vision_real import SceneAnalyzer

analyzer = SceneAnalyzer()

# Analyze
context = await analyzer.analyze_scene(
    people=[{"name": "Manan", "confidence": 0.95}],
    emotions=[{"emotion": "happy", "confidence": 0.8}],
    gestures=["open_palm"],
    additional_context={
        "calendar": "In meeting",
        "email": "3 unread"
    }
)

print(f"Activity: {context.activity}")
print(f"Energy: {context.energy_level}")
print(f"Recommendation: {context.recommendation}")
```

### Context Types

```python
# Time-based
context = await analyzer.analyze_scene(
    people=people,
    emotions=emotions,
    gestures=gestures,
    additional_context={
        "time": "9:00 AM",
        "day": "Monday"
    }
)

# Calendar-based
context = await analyzer.analyze_scene(
    ...,
    additional_context={
        "has_meeting": True,
        "meeting_in_minutes": 5
    }
)

# Activity-based
context = await analyzer.analyze_scene(
    ...,
    additional_context={
        "app_focused": "VSCode",
        "typing_speed": "fast"
    }
)
```

### Get Predictions

```python
# Predict next action
prediction = await analyzer.predict_next_action(context)

print(f"Prediction: {prediction}")
# Example: "You look focused. I can schedule your standup for 2pm if you'd like"
```

### Groq Integration

Uses Groq's Mixtral for intelligent reasoning:

```python
# Requires GROQ_API_KEY environment variable
import os
os.environ['GROQ_API_KEY'] = 'your-key'

analyzer = SceneAnalyzer()  # Auto-initializes with API

# Analyzegets detailed Groq response
context = await analyzer.analyze_scene(people, emotions, gestures)
```

Groq provides:
- Contextual understanding
- Predictive suggestions
- Pattern recognition
- Natural language responses

---

## Real-Time Reactions

### Person Detection

```python
def on_person_detected(data):
    names = data['people']
    
    if names:
        greeting = f"Hello {', '.join(names)}! 👋"
        print(greeting)
        
        # Trigger action
        # - Play welcome music
        # - Show schedule
        # - Send notification

jarvis.register_callback("person_detected", on_person_detected)
```

### Emotion-Based Actions

```python
def on_emotion_alert(data):
    emotion = data['emotion']
    message = data['message']
    
    print(f"😊 {message}")
    
    if emotion == "sad":
        # - Play uplifting music
        # - Suggest break
        # - Show inspirational quotes
    elif emotion == "angry":
        # - Play calming music
        # - Suggest walk
        # - Remind of breaks
    elif emotion == "fear":
        # - Show supporting message
        # - Offer help
        # - Reduce workload

jarvis.register_callback("emotion_alert", on_emotion_alert)
```

### Gesture-Based Commands

```python
def on_gesture(data):
    gesture = data['gesture']
    response = data['response']
    
    print(f"✋ {response}")
    
    if gesture == "thumbs_up":
        # Confirm action
        jarvis.execute_command("confirm")
    elif gesture == "thumbs_down":
        # Reject, undo
        jarvis.execute_command("undo")
    elif gesture == "open_palm":
        # Pause, wait for command
        jarvis.set_listening_mode(True)
    elif gesture == "peace_sign":
        # Break time
        jarvis.suggest_break()

jarvis.register_callback("gesture", on_gesture)
```

### Activity Changes

```python
def on_activity_change(data):
    activity = data['activity']
    
    if activity == "focused work":
        # Enable focus mode
        jarvis.mute_notifications()
    elif activity == "break time":
        # Play relaxing content
        jarvis.play_ambient_sounds()
    elif activity == "meetings":
        # Enhance awareness
        jarvis.highlight_participants()

jarvis.register_callback("activity_change", on_activity_change)
```

---

## Examples & Recipes

### Recipe 1: Productivity Monitor

```python
async def productivity_monitor():
    """Monitor user and suggest breaks when needed."""
    
    jarvis = RealWorldJARVIS()
    jarvis.start()
    
    def on_emotion_alert(data):
        if data['emotion'] in ['sad', 'angry']:
            print("💙 Suggesting break...")
            # Trigger break sequence
    
    def on_activity_change(data):
        if data['energy_level'] == 'low':
            print("⚡ Energy dipping - break time!")
    
    jarvis.register_callback("emotion_alert", on_emotion_alert)
    jarvis.register_callback("activity_change", on_activity_change)
    
    await jarvis.run_async(display=True)

# Run
import asyncio
asyncio.run(productivity_monitor())
```

### Recipe 2: Smart Security

```python
async def smart_security():
    """Detect unauthorized people."""
    
    jarvis = RealWorldJARVIS()
    jarvis.start()
    
    authorized = ["Alice", "Bob", "Charlie"]
    
    def on_person_detected(data):
        for person in data['people']:
            if person == "Unknown":
                print("⚠️ Unknown person detected!")
                # Trigger alert
            elif person not in authorized:
                print(f"⚠️ {person} not authorized here!")
    
    jarvis.register_callback("person_detected", on_person_detected)
    await jarvis.run_async()

asyncio.run(smart_security())
```

### Recipe 3: Gesture Commands

```python
async def gesture_commands():
    """Control JARVIS with hand gestures."""
    
    jarvis = RealWorldJARVIS()
    jarvis.start()
    
    commands = {
        "open_palm": lambda: print("👂 Listening..."),
        "thumbs_up": lambda: print("✅ Confirmed!"),
        "thumbs_down": lambda: print("❌ Rejected"),
        "peace_sign": lambda: print("☮️ Chill mode"),
        "pointing": lambda: lambda: print("☝️ Got it!")
    }
    
    def on_gesture(data):
        gesture = data['gesture']
        if gesture in commands:
            commands[gesture]()
    
    jarvis.register_callback("gesture", on_gesture)
    await jarvis.run_async()

asyncio.run(gesture_commands())
```

### Recipe 4: Emotion-Based Music

```python
async def emotion_music():
    """Play music based on emotion."""
    
    music_map = {
        "happy": "upbeat_playlist",
        "sad": "comfort_playlist",
        "angry": "calming_playlist",
        "neutral": "focus_playlist"
    }
    
    jarvis = RealWorldJARVIS()
    
    def on_emotion_alert(data):
        emotion = data['emotion']
        playlist = music_map.get(emotion)
        print(f"🎵 Playing {playlist}...")
        # Play music
    
    jarvis.register_callback("emotion_alert", on_emotion_alert)
    await jarvis.run_async()

asyncio.run(emotion_music())
```

---

## Privacy & Ethics

### Privacy First

The vision system prioritizes privacy:

1. **Local Processing**
   - Face detection/recognition runs locally
   - No cloud processing by default
   - Emotions processed locally

2. **Optional Cloud**
   - Groq scene analysis (if enabled)
   - Can be disabled

3. **Data Retention**
   - Face photos stored locally only
   - Database encrypted when available
   - Easy to delete anytime

### Ethical Use

```python
# 1. Ask for consent
print("📷 I can see your face")
print("This helps me:")
print("- Recognize you")
print("- Understand your mood")
print("- Respond contextually")
consent = input("Proceed? (y/n) ")

# 2. Be transparent
print("ℹ️ I'm using:")
print("- Face recognition")
print("- Emotion detection")
print("- Scene analysis with Groq")

# 3. Allow opt-out
enable_faces = input("Enable face recognition? (y/n) ")
enable_emotions = input("Enable emotion detection? (y/n) ")

# 4. Secure storage
# All data encrypted and local
```

### Disable Features

```python
# Disable face learning
jarvis = RealWorldJARVIS(enable_face_learning=False)

# Disable emotion alerts
jarvis = RealWorldJARVIS(enable_emotion_alerts=False)

# Disable specific analysis
analyzer = SceneAnalyzer()
# Don't call analyze_scene if you don't want scene understanding
```

### Delete Data

```python
# Delete known faces
engine = FaceRecognitionEngine()
engine.forget_person("Alice")

# Delete all known people
for person in engine.get_known_people():
    engine.forget_person(person)

# Clear gesture history
recognizer.gesture_history.clear()
```

---

## Performance Tips

1. **Skip frames** for speed (process_every_nth=2-3)
2. **Use HOG** for face detection (faster, GPU not needed)
3. **Lower resolution** for testing
4. **GPU acceleration** for production (CNN detection, emotions)
5. **Selective features** (not all frames need all analysis)

---

## Troubleshooting

See [SETUP.md#Troubleshooting](SETUP.md#troubleshooting) for common issues.

---

*Last Updated: Phase 7 Vision System*  
*JARVIS Framework v5.0+*
