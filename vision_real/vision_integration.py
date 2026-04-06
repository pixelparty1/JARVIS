"""
Vision Integration - Real-world JARVIS

Integrates all vision components for real-time intelligent awareness:
- Camera capture
- Face recognition
- Emotion detection
- Gesture control
- Scene understanding
"""

import asyncio
import cv2
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .camera import CameraManager, CameraFrame, draw_text, draw_box
from .face_recognition import FaceRecognitionEngine, FaceAnalyzer
from .emotion_detection import EmotionDetector, EmotionMonitor
from .gesture_control import GestureRecognizer, GestureController, Gesture
from .scene_analyzer import SceneAnalyzer, ContextualResponder


@dataclass
class VisionFrame:
    """Processed vision frame with all analysis."""
    frame_id: int
    faces: List[Dict]
    emotions: List[Dict]
    gestures: List[Dict]
    scene_context: Dict
    people: List[str]
    primary_activity: str
    suggestions: List[str]
    timestamp: str = ""


class RealWorldJARVIS:
    """
    Main vision system integrating all components.
    
    Real-time awareness of:
    - Who's present (faces)
    - How they feel (emotions)
    - What they're doing (gestures, activity)
    - Overall context (scene understanding)
    
    Provides intelligent, contextual responses.
    """
    
    def __init__(self, enable_face_learning: bool = True,
                 enable_emotion_alerts: bool = True):
        """
        Initialize JARVIS vision system.
        
        Args:
            enable_face_learning: Learn new faces over time
            enable_emotional_alerts: Alert on concerning emotions
        """
        print("🧠 Initializing JARVIS Vision System...\n")
        
        # Components
        self.camera = CameraManager(process_every_nth=2)
        self.faces = FaceAnalyzer()
        self.emotions = EmotionMonitor(alert_threshold=0.7)
        self.gestures = GestureController()
        self.scene = SceneAnalyzer()
        self.responder = ContextualResponder(self.scene)
        
        # Settings
        self.enable_face_learning = enable_face_learning
        self.enable_emotion_alerts = enable_emotion_alerts
        
        # State
        self.is_running = False
        self.last_people = []
        self.frame_count = 0
        self.callbacks = {}
        
        print("✅ Vision system components initialized")
    
    def start(self) -> bool:
        """Start vision system."""
        if not self.camera.start():
            print("❌ Failed to start camera")
            return False
        
        print("\n✅ JARVIS Vision System Started")
        print("🎥 Real-time awareness enabled\n")
        
        self.is_running = True
        return True
    
    def stop(self) -> None:
        """Stop vision system."""
        self.is_running = False
        self.camera.stop()
        cv2.destroyAllWindows()
        print("✅ Vision system stopped")
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register callback for vision events.
        
        Events: "person_detected", "person_greeting", "emotion_alert", "gesture", "activity_change"
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    async def process_frame(self, frame_data: CameraFrame) -> Optional[VisionFrame]:
        """
        Process single frame with all vision analysis.
        
        Returns:
            VisionFrame with complete analysis
        """
        self.frame_count += 1
        
        frame = frame_data.frame
        
        # 1. Face detection and recognition
        face_results = self.faces.engine.recognize_faces(frame)
        faces = []
        current_people = []
        
        for face in face_results:
            face_info = {
                "name": face.name,
                "confidence": face.confidence,
                "location": face.location
            }
            faces.append(face_info)
            
            if face.name != "Unknown":
                current_people.append(face.name)
            
            # Learn new faces if enabled
            if self.enable_face_learning and face.name == "Unknown":
                # Could auto-learn, but better to ask for permission
                pass
        
        # 2. Emotion detection
        emotion_results = self.emotions.detector.detect_emotions(frame)
        emotions = []
        
        for result in emotion_results:
            emotion_info = {
                "emotion": result.dominant_emotion,
                "confidence": result.confidence,
                "response": self.emotions.detector.get_emotion_response(result)
            }
            emotions.append(emotion_info)
        
        # 3. Gesture detection
        gestures = []
        hand_results = self.gestures.recognizer.detect_hands(frame)
        
        for hand in hand_results:
            if hand.gesture != Gesture.NONE:
                gesture_info = {
                    "gesture": hand.gesture.value,
                    "confidence": hand.gesture_confidence,
                    "hand": hand.handedness
                }
                gestures.append(gesture_info)
        
        # 4. Scene analysis
        additional_context = {
            "previous_people": self.last_people,
            "frame_count": self.frame_count
        }
        
        scene_context = await self.scene.analyze_scene(
            people=faces,
            emotions=emotions,
            gestures=[g["gesture"] for g in gestures],
            additional_context=additional_context
        )
        
        # 5. Detect changes
        people_changed = set(current_people) != set(self.last_people)
        
        if people_changed:
            new_people = set(current_people) - set(self.last_people)
            if new_people:
                await self._trigger_event("person_detected", {
                    "people": list(new_people)
                })
                
                greeting = await self.responder.generate_greeting(
                    [{"name": p, "confidence": 1.0} for p in new_people]
                )
                await self._trigger_event("person_greeting", {
                    "message": greeting
                })
            
            self.last_people = current_people
        
        # 6. Emotion alerts
        if self.enable_emotion_alerts:
            for emotion in emotions:
                if emotion["emotion"] in ["sad", "angry"] and emotion["confidence"] > 0.7:
                    await self._trigger_event("emotion_alert", {
                        "emotion": emotion["emotion"],
                        "message": emotion["response"]
                    })
        
        # 7. Gesture responses
        for gesture in gestures:
            response = await self.responder.generate_gesture_response(gesture["gesture"])
            await self._trigger_event("gesture", {
                "gesture": gesture["gesture"],
                "response": response
            })
        
        # Create vision frame
        vision_frame = VisionFrame(
            frame_id=frame_data.frame_id,
            faces=faces,
            emotions=emotions,
            gestures=gestures,
            scene_context=scene_context.__dict__,
            people=current_people,
            primary_activity=scene_context.activity,
            suggestions=[scene_context.recommendation],
            timestamp=datetime.now().isoformat()
        )
        
        return vision_frame
    
    async def _trigger_event(self, event_type: str, data: Dict) -> None:
        """Trigger registered callbacks."""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"❌ Callback error: {e}")
    
    def draw_analysis(self, frame: CameraFrame,
                     vision_frame: VisionFrame) -> cv2.Mat:
        """Draw all analysis on frame."""
        frame_display = frame.frame.copy()
        
        # Draw faces
        for face_info in vision_frame.faces:
            top, right, bottom, left = face_info["location"]
            
            # Color: green if known, red if unknown
            color = (0, 255, 0) if face_info["name"] != "Unknown" else (0, 0, 255)
            
            cv2.rectangle(frame_display, (left, top), (right, bottom), color, 2)
            
            label = f"{face_info['name']} ({face_info['confidence']:.2f})"
            cv2.rectangle(
                frame_display,
                (left, bottom - 35),
                (right, bottom),
                color,
                cv2.FILLED
            )
            cv2.putText(
                frame_display,
                label,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_DUPLEX,
                0.6,
                (255, 255, 255),
                1
            )
        
        # Draw emotions
        if vision_frame.emotions:
            emotion = vision_frame.emotions[0]
            text = f"😊 {emotion['emotion']} ({emotion['confidence']:.0%})"
            draw_text(frame_display, text, (10, 60), (0, 255, 0))
        
        # Draw gestures
        if vision_frame.gestures:
            for i, gesture in enumerate(vision_frame.gestures):
                text = f"✋ {gesture['gesture']}"
                draw_text(frame_display, text, (10, 90 + i*30), (255, 0, 0))
        
        # Draw activity
        activity_text = f"Activity: {vision_frame.primary_activity}"
        draw_text(frame_display, activity_text, (10, frame_display.shape[0] - 40), (255, 255, 0))
        
        # Draw suggestion
        if vision_frame.suggestions:
            suggestion_text = f"💡 {vision_frame.suggestions[0][:50]}..."
            draw_text(frame_display, suggestion_text, (10, frame_display.shape[0] - 10), (0, 255, 255))
        
        # Draw FPS
        draw_text(frame_display, f"FPS: {self.camera.stats.fps:.1f}", (10, 30), (0, 255, 0))
        
        return frame_display
    
    async def run_async(self, display: bool = True, duration: int = None) -> None:
        """
        Run vision system (async).
        
        Args:
            display: Show live video
            duration: Run for N seconds (None = forever)
        """
        if not self.is_running:
            self.start()
        
        start_time = datetime.now().timestamp() if duration else None
        
        while self.is_running:
            try:
                # Check timeout
                if duration and start_time:
                    if (datetime.now().timestamp() - start_time) > duration:
                        break
                
                # Get frame
                camera_frame = self.camera.get_frame()
                if camera_frame is None:
                    await asyncio.sleep(0.01)
                    continue
                
                # Process every nth frame to reduce latency
                if (camera_frame.frame_id % 2) == 0:
                    vision_frame = await self.process_frame(camera_frame)
                    
                    if display and vision_frame:
                        frame_display = self.draw_analysis(camera_frame, vision_frame)
                        
                        cv2.imshow("JARVIS Vision", frame_display)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
                
                await asyncio.sleep(0.01)
            
            except Exception as e:
                print(f"❌ Run error: {e}")
                await asyncio.sleep(0.1)
    
    def run(self, display: bool = True) -> None:
        """Run vision system (blocking)."""
        if not self.is_running:
            self.start()
        
        print("📹 Running JARVIS Vision (press 'q' to quit)\n")
        
        try:
            while self.is_running:
                camera_frame = self.camera.get_frame()
                
                if camera_frame:
                    vision_frame = asyncio.run(self.process_frame(camera_frame))
                    
                    if display and vision_frame:
                        frame_display = self.draw_analysis(camera_frame, vision_frame)
                        cv2.imshow("JARVIS Vision", frame_display)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted")
        
        finally:
            self.stop()


# Example usage
if __name__ == "__main__":
    print("🚀 JARVIS Real-World Vision System\n")
    
    # Initialize
    jarvis = RealWorldJARVIS(
        enable_face_learning=True,
        enable_emotion_alerts=True
    )
    
    # Register callbacks
    def on_person_detected(data):
        print(f"\n👋 Person detected: {data['people']}")
    
    def on_gesture(data):
        print(f"\n✋ Gesture: {data['gesture']}")
        print(f"   Response: {data['response']}")
    
    jarvis.register_callback("person_detected", on_person_detected)
    jarvis.register_callback("gesture", on_gesture)
    
    # Run
    try:
        jarvis.run(display=True)
    except KeyboardInterrupt:
        print("\nShutdown...")
