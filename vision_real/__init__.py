"""
JARVIS Vision - Real-World Intelligence (Phase 7)

Computer vision and AI-powered real-world awareness.

Modules:
- camera: Real-time webcam capture and processing
- face_recognition: Identify and recognize people
- emotion_detection: Detect emotional states using DeepFace
- gesture_control: Hand gesture recognition using MediaPipe
- scene_analyzer: Intelligent context understanding with Groq
- vision_integration: Main system integrating all components

Features:
- Real-time face detection and recognition
- Emotion detection (7 emotions)
- Hand gesture recognition (10+ gestures)
- Smart scene understanding
- Groq-powered contextual responses
- Privacy-aware local processing
- Efficient frame processing (skip frames for speed)
- Multi-hand detection
- Continuous learning

Quick Start:

    from vision_real import RealWorldJARVIS
    
    # Initialize
    jarvis = RealWorldJARVIS()
    
    # Register callbacks
    def on_detection(data):
        print(f"Detected: {data}")
    
    jarvis.register_callback("person_detected", on_detection)
    
    # Run
    jarvis.run(display=True)
"""

__version__ = "1.0.0"
__author__ = "JARVIS Team"

from .camera import CameraManager, CameraFrame, resize_frame, draw_fps, draw_text, draw_box
from .face_recognition import FaceRecognitionEngine, FaceAnalyzer, Face, KnownPerson
from .emotion_detection import EmotionDetector, EmotionMonitor, EmotionResult
from .gesture_control import GestureRecognizer, GestureController, Gesture, HandDetection
from .scene_analyzer import SceneAnalyzer, SceneContext, ContextualResponder
from .vision_integration import RealWorldJARVIS, VisionFrame

__all__ = [
    # Camera system
    "CameraManager",
    "CameraFrame",
    "resize_frame",
    "draw_fps",
    "draw_text",
    "draw_box",
    
    # Face recognition
    "FaceRecognitionEngine",
    "FaceAnalyzer",
    "Face",
    "KnownPerson",
    
    # Emotion detection
    "EmotionDetector",
    "EmotionMonitor",
    "EmotionResult",
    
    # Gesture control
    "GestureRecognizer",
    "GestureController",
    "Gesture",
    "HandDetection",
    
    # Scene analysis
    "SceneAnalyzer",
    "SceneContext",
    "ContextualResponder",
    
    # Main integration
    "RealWorldJARVIS",
    "VisionFrame"
]
