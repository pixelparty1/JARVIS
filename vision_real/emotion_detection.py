"""
Emotion Detection System

Features:
- Detect emotions from faces
- Emotion confidence levels
- Emotion history tracking
- Real-time emotion analysis
"""

from deepface import DeepFace
import cv2
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime


@dataclass
class EmotionResult:
    """Emotion detection result."""
    emotions: Dict[str, float]  # {"happy": 0.8, "sad": 0.1, ...}
    dominant_emotion: str
    confidence: float
    location: tuple = None  # (top, right, bottom, left)
    timestamp: str = ""
    
    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now().isoformat()


class EmotionDetector:
    """
    Detect emotions from face images.
    
    Emotions: angry, disgust, fear, happy, neutral, sad, surprise
    """
    
    def __init__(self, model: str = "fer2013"):
        """
        Initialize emotion detector.
        
        Args:
            model: "fer2013", "vggface", or "mobilenet"
        """
        self.model = model
        self.history = deque(maxlen=100)
        self.stats = {
            "total_detections": 0,
            "errors": 0
        }
    
    def detect_emotions(self, frame: np.ndarray,
                       enforce_detection: bool = False) -> List[EmotionResult]:
        """
        Detect emotions in frame.
        
        Args:
            frame: Image frame
            enforce_detection: Require successful face detection
            
        Returns:
            List of EmotionResult objects
        """
        try:
            # DeepFace analysis
            results = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=enforce_detection,
                silent=True
            )
            
            emotion_results = []
            
            for result in results:
                # Get emotion data
                emotions = result.get('emotion', {})
                dominant = result.get('dominant_emotion', 'neutral')
                
                # Calculate confidence
                confidence = emotions.get(dominant, 0) / 100.0
                
                # Get face location
                region = result.get('region', {})
                location = (
                    region.get('y'),
                    region.get('x') + region.get('w'),
                    region.get('y') + region.get('h'),
                    region.get('x')
                )
                
                emotion_result = EmotionResult(
                    emotions={k: v/100.0 for k, v in emotions.items()},
                    dominant_emotion=dominant,
                    confidence=confidence,
                    location=location
                )
                
                emotion_results.append(emotion_result)
                self.history.append(emotion_result)
            
            self.stats["total_detections"] += len(emotion_results)
            
            return emotion_results
        
        except Exception as e:
            self.stats["errors"] += 1
            return []
    
    def get_emotion_string(self, emotion_result: EmotionResult) -> str:
        """Get human-readable emotion string."""
        emoji_map = {
            "happy": "😊",
            "sad": "😢",
            "angry": "😠",
            "surprise": "😲",
            "fear": "😨",
            "disgust": "🤢",
            "neutral": "😐"
        }
        
        emoji = emoji_map.get(emotion_result.dominant_emotion, "")
        confidence = emotion_result.confidence
        
        return f"{emoji} {emotion_result.dominant_emotion.title()} ({confidence:.0%})"
    
    def get_emotion_response(self, emotion_result: EmotionResult) -> str:
        """Generate contextual response to emotion."""
        emotion = emotion_result.dominant_emotion
        confidence = emotion_result.confidence
        
        responses = {
            "happy": [
                "You look happy! 😊 That's great!",
                "You seem in a good mood!",
                "Smiling suits you! Keep it up!"
            ],
            "sad": [
                "You seem down. Want to talk? 💙",
                "I notice you might be feeling sad. How can I help?",
                "Take a break? I can help you relax."
            ],
            "angry": [
                "You look upset. Deep breaths? 🧘",
                "Everything okay? I'm here to help.",
                "Want to step away and take a break?"
            ],
            "fear": [
                "You seem worried or anxious. 💙",
                "Is there something I can help with?",
                "Take your time. I'm here."
            ],
            "surprise": [
                "Surprised! 😲 What's happening?",
                "Something interesting?",
                "Tell me more!"
            ],
            "neutral": [
                "You seem calm. Ready to work? 👍",
                "Everything alright?",
                "Let me know if you need anything."
            ],
            "disgust": [
                "Something wrong? 🤔",
                "Need a break from this?",
                "I can help you with something else."
            ]
        }
        
        if confidence < 0.3:
            return "I can't quite read your emotion right now."
        
        response_list = responses.get(emotion, ["How are you doing?"])
        return response_list[0]  # Use first response (could randomly select)
    
    def get_average_emotion(self, window: int = 10) -> Optional[Dict]:
        """
        Get average emotion over last N detections.
        
        Args:
            window: Number of recent detections to average
            
        Returns:
            Average emotion dict or None
        """
        if len(self.history) < window:
            window = len(self.history)
        
        if window == 0:
            return None
        
        # Get recent results
        recent = list(self.history)[-window:]
        
        # Average emotions
        emotion_sums = {}
        for result in recent:
            for emotion, value in result.emotions.items():
                emotion_sums[emotion] = emotion_sums.get(emotion, 0) + value
        
        avg_emotions = {
            emotion: (value / window) 
            for emotion, value in emotion_sums.items()
        }
        
        return avg_emotions
    
    def draw_emotion(self, frame: np.ndarray,
                    emotion_result: EmotionResult) -> np.ndarray:
        """Draw emotion on frame."""
        if emotion_result.location is None:
            return frame
        
        top, right, bottom, left = emotion_result.location
        
        # Draw box
        color = self._get_emotion_color(emotion_result.dominant_emotion)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw emotion label
        emotion_text = self.get_emotion_string(emotion_result)
        
        cv2.rectangle(
            frame,
            (left, bottom - 35),
            (right, bottom),
            color,
            cv2.FILLED
        )
        
        cv2.putText(
            frame,
            emotion_text,
            (left + 6, bottom - 6),
            cv2.FONT_HERSHEY_DUPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        return frame
    
    def _get_emotion_color(self, emotion: str) -> tuple:
        """Get color for emotion visualization."""
        color_map = {
            "happy": (0, 255, 0),      # Green
            "sad": (255, 0, 0),        # Blue
            "angry": (0, 0, 255),      # Red
            "fear": (255, 0, 255),     # Magenta
            "surprise": (0, 255, 255), # Yellow
            "disgust": (0, 165, 255),  # Orange
            "neutral": (200, 200, 200) # Gray
        }
        
        return color_map.get(emotion, (255, 255, 255))  # Default white
    
    def draw_emotion_chart(self, frame: np.ndarray,
                          emotion_result: EmotionResult,
                          x: int = 10, y: int = 30) -> np.ndarray:
        """Draw emotion confidence chart on frame."""
        emotions = emotion_result.emotions
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        bar_height = 20
        bar_width = 200
        
        for i, (emotion, confidence) in enumerate(sorted_emotions):
            y_pos = y + (i * bar_height)
            
            # Draw label
            cv2.putText(
                frame,
                emotion,
                (x, y_pos + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )
            
            # Draw bar background
            cv2.rectangle(
                frame,
                (x + 80, y_pos),
                (x + 80 + bar_width, y_pos + bar_height),
                (50, 50, 50),
                -1
            )
            
            # Draw confidence bar
            color = self._get_emotion_color(emotion)
            bar_width_actual = int(bar_width * confidence)
            cv2.rectangle(
                frame,
                (x + 80, y_pos),
                (x + 80 + bar_width_actual, y_pos + bar_height),
                color,
                -1
            )
            
            # Draw percentage
            cv2.putText(
                frame,
                f"{confidence:.0%}",
                (x + 80 + bar_width + 10, y_pos + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )
        
        return frame


class EmotionMonitor:
    """Monitor user emotion over time."""
    
    def __init__(self, alert_threshold: float = 0.7):
        """
        Initialize emotion monitor.
        
        Args:
            alert_threshold: Alert if sad/angry/fear confidence > threshold
        """
        self.detector = EmotionDetector()
        self.alert_threshold = alert_threshold
        self.alerts = []
    
    async def analyze_frame(self, frame: np.ndarray) -> Dict:
        """Analyze frame and return emotion report."""
        results = self.detector.detect_emotions(frame)
        
        report = {
            "detected": len(results) > 0,
            "emotions": [],
            "alerts": [],
            "suggestions": []
        }
        
        for result in results:
            report["emotions"].append({
                "emotion": result.dominant_emotion,
                "confidence": result.confidence,
                "response": self.detector.get_emotion_response(result)
            })
            
            # Check for alerts
            if result.dominant_emotion in ["sad", "angry", "fear"]:
                if result.confidence > self.alert_threshold:
                    alert = {
                        "type": "mood_alert",
                        "emotion": result.dominant_emotion,
                        "confidence": result.confidence,
                        "message": f"User seems {result.dominant_emotion}"
                    }
                    report["alerts"].append(alert)
        
        # Add suggestions
        if len(report["emotions"]) > 0:
            dominant = max(
                report["emotions"],
                key=lambda x: x["confidence"]
            )
            
            suggestions = self._get_suggestions(dominant["emotion"])
            report["suggestions"] = suggestions
        
        return report
    
    def _get_suggestions(self, emotion: str) -> List[str]:
        """Get suggestions based on emotion."""
        suggestion_map = {
            "sad": [
                "Take a 5-minute break",
                "Listen to uplifting music",
                "Step outside for fresh air",
                "Text a friend"
            ],
            "angry": [
                "Take deep breaths",
                "Go for a walk",
                "Do some stretching",
                "Listen to calming music"
            ],
            "fear": [
                "Take your time",
                "Break task into smaller steps",
                "Get support from someone",
                "Practice grounding techniques"
            ],
            "neutral": [
                "Keep up the great work!",
                "Stay hydrated",
                "Take periodic breaks"
            ],
            "happy": [
                "Channel this energy into productivity",
                "Share your joy with others",
                "Tackle that challenging task"
            ]
        }
        
        return suggestion_map.get(emotion, ["Take care of yourself!"])


# Example usage
if __name__ == "__main__":
    print("🎭 Emotion Detection Test\n")
    
    detector = EmotionDetector()
    print("✅ Emotion detector initialized")
    
    # Test with webcam
    print("Starting live emotion detection (press 'q' to quit)...")
