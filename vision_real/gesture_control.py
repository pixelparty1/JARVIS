"""
Gesture Control System

Features:
- Hand pose detection
- Gesture recognition
- Gesture-based commands
- Gesture confidence tracking
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque


class Gesture(Enum):
    """Recognized gestures."""
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


@dataclass
class HandDetection:
    """Detected hand."""
    landmarks: np.ndarray  # 21 hand landmarks
    handedness: str  # "Left" or "Right"
    confidence: float
    gesture: Gesture = Gesture.NONE
    gesture_confidence: float = 0.0
    position: Tuple[int, int] = None  # (x, y) of center


class GestureRecognizer:
    """
    Recognize hand gestures.
    
    Uses MediaPipe for hand detection and custom logic for gestures.
    """
    
    def __init__(self):
        """Initialize gesture recognizer."""
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.gesture_history = deque(maxlen=30)
    
    def detect_hands(self, frame: np.ndarray) -> List[HandDetection]:
        """
        Detect hands in frame.
        
        Args:
            frame: Image frame
            
        Returns:
            List of HandDetection objects
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect hands
            results = self.hands.process(rgb_frame)
            
            hands = []
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for landmarks, handedness_info in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
                ):
                    # Extract landmarks
                    landmark_array = np.zeros((21, 2))
                    for i, landmark in enumerate(landmarks.landmark):
                        landmark_array[i] = [landmark.x, landmark.y]
                    
                    # Get hand info
                    hand_label = handedness_info.classification[0].label
                    confidence = handedness_info.classification[0].score
                    
                    # Calculate center position
                    center_x = int(np.mean(landmark_array[:, 0]) * frame.shape[1])
                    center_y = int(np.mean(landmark_array[:, 1]) * frame.shape[0])
                    
                    hand_detection = HandDetection(
                        landmarks=landmark_array,
                        handedness=hand_label,
                        confidence=confidence,
                        position=(center_x, center_y)
                    )
                    
                    # Recognize gesture
                    gesture, conf = self._recognize_gesture(landmark_array)
                    hand_detection.gesture = gesture
                    hand_detection.gesture_confidence = conf
                    
                    hands.append(hand_detection)
            
            return hands
        
        except Exception as e:
            print(f"❌ Hand detection error: {e}")
            return []
    
    def _recognize_gesture(self, landmarks: np.ndarray) -> Tuple[Gesture, float]:
        """
        Recognize gesture from landmarks.
        
        Landmark indices:
        0: Wrist
        5: Index base
        9: Middle base
        13: Ring base
        17: Pinky base
        4: Index tip
        8: Middle tip
        12: Ring tip
        16: Pinky tip
        """
        try:
            # Helper function to calculate distance
            def distance(p1, p2):
                return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            
            wrist = landmarks[0]
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            index_base = landmarks[5]
            middle_base = landmarks[9]
            
            # Calculate finger distances from wrist
            thumb_dist = distance(wrist, thumb_tip)
            index_dist = distance(wrist, index_tip)
            middle_dist = distance(wrist, middle_tip)
            ring_dist = distance(wrist, ring_tip)
            pinky_dist = distance(wrist, pinky_tip)
            
            # Threshold for finger "open"
            threshold = 0.1
            
            # Count fingers up
            fingers_up = 0
            if thumb_dist > threshold:
                fingers_up += 1
            if index_dist > threshold:
                fingers_up += 1
            if middle_dist > threshold:
                fingers_up += 1
            if ring_dist > threshold:
                fingers_up += 1
            if pinky_dist > threshold:
                fingers_up += 1
            
            # Recognize gesture
            if fingers_up == 5:
                return Gesture.OPEN_PALM, 0.9
            elif fingers_up == 0:
                return Gesture.CLOSED_FIST, 0.9
            elif fingers_up == 1 and index_dist > threshold:
                return Gesture.POINTING, 0.8
            elif fingers_up == 2:
                # Peace sign or thumbs up
                if thumb_dist < threshold and index_dist > threshold and middle_dist > threshold:
                    return Gesture.PEACE_SIGN, 0.8
                elif thumb_dist > threshold:
                    return Gesture.THUMBS_UP, 0.8
            elif fingers_up == 3:
                return Gesture.OK_SIGN, 0.7
            
            return Gesture.NONE, 0.0
        
        except Exception as e:
            return Gesture.NONE, 0.0
    
    def get_gesture_name(self, gesture: Gesture) -> str:
        """Get human-readable gesture name."""
        names = {
            Gesture.NONE: "No gesture",
            Gesture.THUMBS_UP: "👍 Thumbs Up",
            Gesture.THUMBS_DOWN: "👎 Thumbs Down",
            Gesture.OPEN_PALM: "✋ Open Palm",
            Gesture.CLOSED_FIST: "✊ Closed Fist",
            Gesture.PEACE_SIGN: "✌️ Peace Sign",
            Gesture.OK_SIGN: "👌 OK Sign",
            Gesture.POINTING: "☝️ Pointing",
            Gesture.WAVE: "👋 Wave",
            Gesture.STOP: "🛑 Stop"
        }
        return names.get(gesture, gesture.value)
    
    def draw_hand(self, frame: np.ndarray,
                 hand: HandDetection) -> np.ndarray:
        """Draw hand skeleton on frame."""
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        landmarks_px = hand.landmarks.copy()
        landmarks_px[:, 0] = landmarks_px[:, 0] * w
        landmarks_px[:, 1] = landmarks_px[:, 1] * h
        
        # Draw connections (skeleton)
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
        ]
        
        for start, end in connections:
            pt1 = tuple(map(int, landmarks_px[start]))
            pt2 = tuple(map(int, landmarks_px[end]))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        
        # Draw landmarks
        for i, landmark in enumerate(landmarks_px):
            pt = tuple(map(int, landmark))
            cv2.circle(frame, pt, 5, (0, 0, 255), -1)
        
        # Draw gesture label
        if hand.gesture != Gesture.NONE:
            gesture_text = self.get_gesture_name(hand.gesture)
            cv2.putText(
                frame,
                gesture_text,
                hand.position,
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
        
        return frame


class GestureController:
    """
    Map gestures to commands.
    """
    
    def __init__(self):
        """Initialize gesture controller."""
        self.recognizer = GestureRecognizer()
        self.gesture_callbacks = {}
        self.hold_duration = {}  # Track how long gesture held
    
    def register_gesture(self, gesture: Gesture, callback) -> None:
        """
        Register callback for gesture.
        
        Args:
            gesture: Gesture to trigger on
            callback: Function to call
        """
        self.gesture_callbacks[gesture] = callback
    
    async def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process frame for gestures.
        
        Returns:
            {
                "hands": [...],
                "triggered_gestures": [...]
            }
        """
        hands = self.recognizer.detect_hands(frame)
        
        triggered = []
        for hand in hands:
            if hand.gesture != Gesture.NONE:
                if hand.gesture not in self.hold_duration:
                    self.hold_duration[hand.gesture] = 0
                
                self.hold_duration[hand.gesture] += 1
                
                # Trigger after 5 frames (debounce)
                if self.hold_duration[hand.gesture] >= 5:
                    if hand.gesture in self.gesture_callbacks:
                        await self.gesture_callbacks[hand.gesture]()
                        triggered.append(hand.gesture.value)
            else:
                # Reset hold
                self.hold_duration = {}
        
        return {
            "hands": hands,
            "triggered_gestures": triggered
        }
    
    def draw_hands(self, frame: np.ndarray, hands: List[HandDetection]) -> np.ndarray:
        """Draw all hands on frame."""
        for hand in hands:
            frame = self.recognizer.draw_hand(frame, hand)
        
        return frame


# Example usage
if __name__ == "__main__":
    print("✋ Gesture Control Test\n")
    
    recognizer = GestureRecognizer()
    print("✅ Gesture recognizer initialized")
    
    print("Starting gesture detection (press 'q' to quit)...")
    print("Try gestures: open palm, closed fist, peace sign, thumbs up\n")
