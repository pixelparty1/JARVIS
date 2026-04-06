"""
Real-time Camera System

Features:
- Webcam capture and processing
- Frame optimization (process every nth frame)
- Threading for non-blocking operation
- Frame buffering
- Performance metrics
"""

import cv2
import threading
from typing import Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from pathlib import Path


@dataclass
class CameraFrame:
    """Captured camera frame."""
    frame: np.ndarray
    timestamp: str
    frame_id: int
    width: int
    height: int
    processed: bool = False
    metadata: dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CameraStats:
    """Camera statistics."""
    total_frames: int = 0
    processed_frames: int = 0
    skipped_frames: int = 0
    fps: float = 0.0
    avg_latency_ms: float = 0.0
    errors: int = 0


class CameraManager:
    """
    Manages real-time camera capture and processing.
    
    Features:
    - Non-blocking frame capture (threading)
    - Frame skipping for performance
    - Callback system for frame processing
    - Error handling and recovery
    """
    
    def __init__(self, camera_id: int = 0, process_every_nth: int = 2,
                 target_fps: int = 30, buffer_size: int = 10):
        """
        Initialize camera manager.
        
        Args:
            camera_id: Camera device ID (0 = default)
            process_every_nth: Skip frames for performance
            target_fps: Target frames per second
            buffer_size: Frame buffer size
        """
        self.camera_id = camera_id
        self.process_every_nth = process_every_nth
        self.target_fps = target_fps
        self.buffer_size = buffer_size
        
        self.cap = None
        self.is_running = False
        self.thread = None
        
        self.frame_buffer = []
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        self.frame_id = 0
        self.stats = CameraStats()
        
        self.callbacks = []  # List of (process_every_nth, callback) tuples
        self.error_callback = None
        
        # Timing
        self.last_frame_time = 0
        self.frame_times = []
    
    def initialize(self) -> bool:
        """Initialize camera connection."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                print(f"❌ Failed to open camera {self.camera_id}")
                return False
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            # Get actual resolution
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"✅ Camera initialized: {width}x{height} @ {self.target_fps}fps")
            
            return True
        
        except Exception as e:
            print(f"❌ Camera initialization error: {e}")
            return False
    
    def start(self) -> bool:
        """Start camera capture thread."""
        if self.is_running:
            return True
        
        if not self.initialize():
            return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        
        print("✅ Camera capture started")
        return True
    
    def stop(self) -> None:
        """Stop camera capture."""
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        
        print("✅ Camera capture stopped")
    
    def _capture_loop(self) -> None:
        """Main capture loop (runs in thread)."""
        frame_count = 0
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    self.stats.errors += 1
                    if self.error_callback:
                        self.error_callback("Frame capture failed")
                    continue
                
                self.frame_id += 1
                self.stats.total_frames += 1
                
                # Process every nth frame
                should_process = (self.frame_id % self.process_every_nth) == 0
                
                if should_process:
                    self.stats.processed_frames += 1
                else:
                    self.stats.skipped_frames += 1
                
                # Create frame object
                camera_frame = CameraFrame(
                    frame=frame,
                    timestamp=datetime.now().isoformat(),
                    frame_id=self.frame_id,
                    width=frame.shape[1],
                    height=frame.shape[0]
                )
                
                # Store in buffer
                with self.frame_lock:
                    self.current_frame = camera_frame
                    self.frame_buffer.append(camera_frame)
                    
                    # Keep buffer size limited
                    if len(self.frame_buffer) > self.buffer_size:
                        self.frame_buffer.pop(0)
                
                # Execute callbacks if should process
                if should_process:
                    for interval, callback in self.callbacks:
                        if (self.frame_id % interval) == 0:
                            try:
                                callback(camera_frame)
                            except Exception as e:
                                print(f"❌ Callback error: {e}")
                                self.stats.errors += 1
                
                # Calculate FPS
                now = datetime.now().timestamp()
                if self.last_frame_time:
                    delta = now - self.last_frame_time
                    self.frame_times.append(delta)
                    
                    if len(self.frame_times) > 30:
                        self.frame_times.pop(0)
                    
                    self.stats.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
                
                self.last_frame_time = now
            
            except Exception as e:
                print(f"❌ Capture loop error: {e}")
                self.stats.errors += 1
    
    def get_frame(self) -> Optional[CameraFrame]:
        """Get current frame."""
        with self.frame_lock:
            return self.current_frame
    
    def get_frame_copy(self) -> Optional[np.ndarray]:
        """Get copy of current frame array."""
        with self.frame_lock:
            if self.current_frame is None:
                return None
            return self.current_frame.frame.copy()
    
    def register_callback(self, callback: Callable,
                         process_every_nth: int = 1) -> None:
        """
        Register frame processing callback.
        
        Args:
            callback: Function(CameraFrame) -> None
            process_every_nth: Process every nth frame
        """
        self.callbacks.append((process_every_nth, callback))
        print(f"✅ Registered callback (every {process_every_nth} frames)")
    
    def set_error_callback(self, callback: Callable) -> None:
        """Set error callback."""
        self.error_callback = callback
    
    def get_stats(self) -> CameraStats:
        """Get camera statistics."""
        return self.stats
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get frame resolution (width, height)."""
        if self.current_frame:
            return self.current_frame.width, self.current_frame.height
        return 0, 0
    
    def display_frame(self, frame: np.ndarray = None,
                     window_name: str = "JARVIS Camera") -> bool:
        """
        Display frame in window.
        
        Args:
            frame: Frame to display (uses current if None)
            window_name: Window title
            
        Returns:
            Key press (ord of key, -1 if no key)
        """
        if frame is None:
            frame = self.get_frame_copy()
        
        if frame is None:
            return False
        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        
        return key != 255  # Return True if key pressed
    
    def save_frame(self, filename: str = None) -> Optional[str]:
        """Save current frame to file."""
        frame = self.get_frame_copy()
        if frame is None:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"frame_{timestamp}.jpg"
        
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        cv2.imwrite(str(path), frame)
        print(f"✅ Frame saved: {path}")
        
        return str(path)


def resize_frame(frame: np.ndarray, scale: float = 0.5) -> np.ndarray:
    """Resize frame for faster processing."""
    height, width = frame.shape[:2]
    new_width = int(width * scale)
    new_height = int(height * scale)
    return cv2.resize(frame, (new_width, new_height))


def draw_fps(frame: np.ndarray, fps: float) -> np.ndarray:
    """Draw FPS on frame."""
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    return frame


def draw_text(frame: np.ndarray, text: str,
             position: Tuple[int, int] = (10, 60),
             color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """Draw text on frame."""
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2
    )
    return frame


def draw_box(frame: np.ndarray, x: int, y: int, w: int, h: int,
            label: str = "", color: Tuple[int, int, int] = (0, 255, 0),
            thickness: int = 2) -> np.ndarray:
    """Draw bounding box on frame."""
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    
    if label:
        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )
    
    return frame


# Example usage
if __name__ == "__main__":
    import time
    
    print("🎥 Camera System Test\n")
    
    # Create camera manager
    camera = CameraManager(process_every_nth=2)
    
    # Start capture
    if not camera.start():
        print("Failed to start camera")
        exit(1)
    
    # Simple callback
    def process_frame(frame: CameraFrame):
        print(f"\n📷 Frame #{frame.frame_id}")
        print(f"   Time: {frame.timestamp}")
        print(f"   Size: {frame.width}x{frame.height}")
    
    camera.register_callback(process_frame, process_every_nth=5)
    
    # Run for 10 seconds
    print("\nCapturing frames... (press 'q' to quit)\n")
    
    try:
        start_time = time.time()
        while time.time() - start_time < 10:
            current_frame = camera.get_frame()
            
            if current_frame:
                frame_display = current_frame.frame.copy()
                frame_display = draw_fps(frame_display, camera.stats.fps)
                camera.display_frame(frame_display)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            
            time.sleep(0.01)
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        
        print("\n📊 Camera Stats:")
        stats = camera.get_stats()
        print(f"   Total frames: {stats.total_frames}")
        print(f"   Processed: {stats.processed_frames}")
        print(f"   Skipped: {stats.skipped_frames}")
        print(f"   Errors: {stats.errors}")
        print(f"   Average FPS: {stats.fps:.1f}")
