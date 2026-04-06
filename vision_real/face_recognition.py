"""
Face Recognition System

Features:
- Face detection
- Face recognition (identify known people)
- Face encoding storage
- Add new faces
- Privacy-aware (local processing)
"""

import face_recognition
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import os


@dataclass
class Face:
    """Detected face."""
    name: str
    encoding: np.ndarray
    location: Tuple[int, int, int, int]  # (top, right, bottom, left)
    distance: float = 0.0  # Distance to known encoding (lower = better match)
    confidence: float = 0.0  # Confidence (0-1)
    timestamp: str = ""


@dataclass
class KnownPerson:
    """Known person with multiple face encodings."""
    name: str
    encodings: List[np.ndarray] = field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""
    photo_path: str = ""
    metadata: Dict = field(default_factory=dict)


class FaceRecognitionEngine:
    """
    Face detection and recognition.
    
    Features:
    - Detect faces in images
    - Match against known people
    - Learn new faces over time
    - Store/load known faces
    """
    
    def __init__(self, model: str = "hog", tolerance: float = 0.6):
        """
        Initialize face recognition.
        
        Args:
            model: "hog" (faster) or "cnn" (more accurate)
            tolerance: Face match tolerance (lower = stricter)
        """
        self.model = model
        self.tolerance = tolerance
        self.known_people = {}
        self.unknown_count = 0
        
        self.db_path = Path("./jarvis_config/known_faces.pkl")
        self.photos_path = Path("./jarvis_config/known_faces")
        
        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.photos_path.mkdir(parents=True, exist_ok=True)
        
        # Load known faces
        self._load_known_faces()
    
    def detect_faces(self, frame: np.ndarray) -> List[Face]:
        """
        Detect all faces in frame.
        
        Args:
            frame: Image frame
            
        Returns:
            List of detected Face objects
        """
        try:
            # Find face locations
            face_locations = face_recognition.face_locations(frame, model=self.model)
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            faces = []
            for location, encoding in zip(face_locations, face_encodings):
                face = Face(
                    name="Unknown",
                    encoding=encoding,
                    location=location
                )
                faces.append(face)
            
            return faces
        
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return []
    
    def recognize_faces(self, frame: np.ndarray) -> List[Face]:
        """
        Detect and recognize faces in frame.
        
        Args:
            frame: Image frame
            
        Returns:
            List of recognized Face objects
        """
        faces = self.detect_faces(frame)
        
        for face in faces:
            name, distance = self._match_face(face.encoding)
            face.name = name
            face.distance = distance
            face.confidence = max(0, 1 - distance)
        
        return faces
    
    def _match_face(self, encoding: np.ndarray) -> Tuple[str, float]:
        """
        Match face encoding to known people.
        
        Returns:
            (name, distance)
        """
        if not self.known_people:
            return "Unknown", 1.0
        
        # Get all known encodings
        known_encodings = []
        known_names = []
        
        for name, person in self.known_people.items():
            for enc in person.encodings:
                known_encodings.append(enc)
                known_names.append(name)
        
        if not known_encodings:
            return "Unknown", 1.0
        
        # Compare faces
        distances = face_recognition.face_distance(known_encodings, encoding)
        
        # Find best match
        best_idx = np.argmin(distances)
        best_distance = distances[best_idx]
        
        if best_distance < self.tolerance:
            return known_names[best_idx], best_distance
        
        return "Unknown", best_distance
    
    def add_person(self, name: str, photo_path: str) -> bool:
        """
        Add new known person from photo.
        
        Args:
            name: Person's name
            photo_path: Path to face photo
            
        Returns:
            Success status
        """
        try:
            # Load image
            image = face_recognition.load_image_file(photo_path)
            
            # Get face encodings
            encodings = face_recognition.face_encodings(image)
            
            if not encodings:
                print(f"❌ No faces found in {photo_path}")
                return False
            
            # Save photo
            dst_path = self.photos_path / f"{name}.jpg"
            if not Path(photo_path).suffix.lower() in ['.jpg', '.jpeg', '.png']:
                # Convert to jpg
                img = cv2.imread(photo_path)
                cv2.imwrite(str(dst_path), img)
            else:
                import shutil
                shutil.copy(photo_path, dst_path)
            
            # Create person
            person = KnownPerson(
                name=name,
                encodings=encodings,
                first_seen=str(Path(photo_path).stat().st_ctime),
                photo_path=str(dst_path)
            )
            
            self.known_people[name] = person
            self._save_known_faces()
            
            print(f"✅ Added person: {name}")
            return True
        
        except Exception as e:
            print(f"❌ Error adding person: {e}")
            return False
    
    def learn_face(self, name: str, encoding: np.ndarray,
                  photo_frame: np.ndarray = None) -> bool:
        """
        Learn new face from encoding (continuous learning).
        
        Args:
            name: Person's name
            encoding: Face encoding
            photo_frame: Optional frame to save
            
        Returns:
            Success status
        """
        try:
            if name not in self.known_people:
                self.known_people[name] = KnownPerson(name=name)
            
            # Add encoding
            self.known_people[name].encodings.append(encoding)
            self.known_people[name].last_seen = str(Path.cwd())
            
            # Save photo if provided
            if photo_frame is not None:
                timestamp = int(Path.cwd().stat().st_ctime)
                photo_name = f"{name}_{timestamp}.jpg"
                photo_path = self.photos_path / photo_name
                
                cv2.imwrite(str(photo_path), photo_frame)
            
            self._save_known_faces()
            
            print(f"✅ Learned face: {name}")
            return True
        
        except Exception as e:
            print(f"❌ Error learning face: {e}")
            return False
    
    def forget_person(self, name: str) -> bool:
        """Remove known person from database."""
        if name in self.known_people:
            del self.known_people[name]
            self._save_known_faces()
            print(f"✅ Forgot person: {name}")
            return True
        
        return False
    
    def _save_known_faces(self) -> None:
        """Save known faces database."""
        try:
            with open(self.db_path, 'wb') as f:
                pickle.dump(self.known_people, f)
        except Exception as e:
            print(f"❌ Error saving known faces: {e}")
    
    def _load_known_faces(self) -> None:
        """Load known faces database."""
        if not self.db_path.exists():
            self.known_people = {}
            return
        
        try:
            with open(self.db_path, 'rb') as f:
                self.known_people = pickle.load(f)
            
            print(f"✅ Loaded {len(self.known_people)} known people")
        
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
            self.known_people = {}
    
    def get_known_people(self) -> List[str]:
        """Get list of known people."""
        return list(self.known_people.keys())
    
    def get_person_info(self, name: str) -> Optional[KnownPerson]:
        """Get info about known person."""
        return self.known_people.get(name)


class FaceAnalyzer:
    """Higher-level face analysis."""
    
    def __init__(self):
        """Initialize face analyzer."""
        self.engine = FaceRecognitionEngine()
        self.face_history = {}  # Track seen faces
    
    async def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze frame for faces.
        
        Returns:
            {
                "faces": [{"name": "John", "confidence": 0.95, ...}],
                "count": 1,
                "known_count": 1,
                "unknown_count": 0
            }
        """
        faces = self.engine.recognize_faces(frame)
        
        result = {
            "faces": [],
            "count": len(faces),
            "known_count": 0,
            "unknown_count": 0
        }
        
        for face in faces:
            is_known = face.name != "Unknown"
            
            face_info = {
                "name": face.name,
                "confidence": face.confidence,
                "location": face.location,
                "known": is_known
            }
            
            result["faces"].append(face_info)
            
            if is_known:
                result["known_count"] += 1
            else:
                result["unknown_count"] += 1
            
            # Update history
            if face.name not in self.face_history:
                self.face_history[face.name] = {
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "count": 1
                }
            else:
                self.face_history[face.name]["last_seen"] = datetime.now().isoformat()
                self.face_history[face.name]["count"] += 1
        
        return result
    
    def draw_faces(self, frame: np.ndarray, faces: List[Face],
                   show_confidence: bool = True) -> np.ndarray:
        """Draw face boxes and labels on frame."""
        for face in faces:
            top, right, bottom, left = face.location
            
            # Choose color based on if known
            if face.name == "Unknown":
                color = (0, 0, 255)  # Red
            else:
                color = (0, 255, 0)  # Green
            
            # Draw box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label
            label = face.name
            if show_confidence:
                label += f" ({face.confidence:.2f})"
            
            cv2.rectangle(
                frame,
                (left, bottom - 35),
                (right, bottom),
                color,
                cv2.FILLED
            )
            
            cv2.putText(
                frame,
                label,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_DUPLEX,
                0.6,
                (255, 255, 255),
                1
            )
        
        return frame


from datetime import datetime

# Example usage
if __name__ == "__main__":
    print("🧑 Face Recognition Test\n")
    
    engine = FaceRecognitionEngine(model="hog")
    
    print(f"✅ Known people: {engine.get_known_people()}")
    
    # Load test image
    test_image_path = "test_face.jpg"  # Replace with real image
    
    if os.path.exists(test_image_path):
        image = face_recognition.load_image_file(test_image_path)
        faces = engine.recognize_faces(image)
        
        print(f"\n✅ Found {len(faces)} faces:")
        for face in faces:
            print(f"   • {face.name} (confidence: {face.confidence:.2f})")
    else:
        print(f"\n⚠️  Test image not found: {test_image_path}")
