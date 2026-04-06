"""
Screen Capture Module for JARVIS Vision System

Captures screenshots of the entire screen or active window.
Optimized for real-time usage with caching and resizing.
"""

import mss
import threading
import time
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import Optional, Tuple, Dict


class ScreenCapture:
    """
    Real-time screen capture system with optimization.
    
    Features:
    - Full screen capture
    - Active window capture
    - Screenshot caching
    - Thumbnail generation
    - Threading support
    """
    
    def __init__(self, cache_dir: str = "screenshots", max_cache_size: int = 10):
        """
        Initialize screen capture system.
        
        Args:
            cache_dir: Directory to store screenshots
            max_cache_size: Maximum screenshots to keep cached
        """
        self.mss = mss.mss()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_cache_size = max_cache_size
        self.cache = {}  # {timestamp: (screenshot, metadata)}
        self.last_capture_time = 0
        self.last_screenshot = None
        self.capture_lock = threading.Lock()
        
        # Settings
        self.enable_caching = True
        self.thumbnail_size = (640, 360)  # For analysis
        self.min_capture_interval = 2.0  # Seconds between captures
        
    def capture_full_screen(self, resize: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Capture the entire screen.
        
        Args:
            resize: Optional (width, height) to resize screenshot
            
        Returns:
            Screenshot as numpy array (BGR format)
        """
        with self.capture_lock:
            try:
                # Capture primary monitor
                monitor = self.mss.monitors[1]
                screenshot = self.mss.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                img = img[:, :, :3]  # Remove alpha channel, keep BGR
                
                # Resize if requested
                if resize:
                    import cv2
                    img = cv2.resize(img, resize)
                
                # Cache screenshot
                if self.enable_caching:
                    self.last_screenshot = img
                    timestamp = time.time()
                    self.last_capture_time = timestamp
                    self._manage_cache(timestamp, img)
                
                return img
                
            except Exception as e:
                print(f"❌ Screen capture error: {e}")
                return None
    
    def capture_active_window(self, resize: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Capture the active window only.
        
        Args:
            resize: Optional (width, height) to resize screenshot
            
        Returns:
            Screenshot as numpy array
        """
        import pyautogui
        
        with self.capture_lock:
            try:
                # Get window position and size
                # Note: This is system-dependent and may require additional setup
                # For now, falls back to full screen capture
                screenshot = pyautogui.screenshot()
                
                # Convert PIL image to numpy array
                img = np.array(screenshot)
                
                # Resize if requested
                if resize:
                    import cv2
                    img = cv2.resize(img, resize)
                
                return img
                
            except Exception as e:
                print(f"❌ Active window capture error: {e}")
                print("   Falling back to full screen capture...")
                return self.capture_full_screen(resize)
    
    def get_thumbnail(self, max_size: Tuple[int, int] = (640, 360)) -> Optional[np.ndarray]:
        """
        Get a thumbnail of the last screenshot.
        
        Args:
            max_size: Maximum (width, height) of thumbnail
            
        Returns:
            Thumbnail as numpy array or None
        """
        if self.last_screenshot is None:
            return None
        
        import cv2
        try:
            thumbnail = cv2.resize(self.last_screenshot, max_size)
            return thumbnail
        except Exception as e:
            print(f"❌ Thumbnail generation error: {e}")
            return None
    
    def save_screenshot(self, filename: Optional[str] = None) -> Path:
        """
        Save the last captured screenshot to disk.
        
        Args:
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Path to saved screenshot
        """
        import cv2
        
        if self.last_screenshot is None:
            print("❌ No screenshot to save")
            return None
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.cache_dir / filename
            cv2.imwrite(str(filepath), self.last_screenshot)
            
            print(f"✅ Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot save error: {e}")
            return None
    
    def _manage_cache(self, timestamp: float, screenshot: np.ndarray):
        """
        Manage screenshot cache, removing old entries.
        
        Args:
            timestamp: Timestamp of new screenshot
            screenshot: Screenshot image
        """
        self.cache[timestamp] = {
            'image': screenshot,
            'size': screenshot.nbytes,
            'timestamp': datetime.fromtimestamp(timestamp)
        }
        
        # Remove oldest entries if cache is too large
        while len(self.cache) > self.max_cache_size:
            oldest = min(self.cache.keys())
            del self.cache[oldest]
    
    def should_capture_now(self) -> bool:
        """
        Check if enough time has passed to capture new screenshot.
        
        Returns:
            True if capture should happen, False otherwise
        """
        elapsed = time.time() - self.last_capture_time
        return elapsed >= self.min_capture_interval
    
    def get_capture_info(self) -> Dict[str, any]:
        """
        Get information about current screen setup.
        
        Returns:
            Dictionary with monitor info
        """
        monitors = self.mss.monitors
        info = {
            'monitor_count': len(monitors) - 1,  # Exclude virtual monitor
            'monitors': []
        }
        
        for i, monitor in enumerate(monitors[1:]):
            info['monitors'].append({
                'index': i + 1,
                'width': monitor['width'],
                'height': monitor['height'],
                'left': monitor['left'],
                'top': monitor['top']
            })
        
        return info
    
    def set_capture_interval(self, interval: float):
        """
        Set minimum interval between captures.
        
        Args:
            interval: Minimum seconds between captures
        """
        self.min_capture_interval = max(0.5, interval)
        print(f"🔧 Capture interval set to {interval}s")
    
    def enable_cache(self, enable: bool = True):
        """
        Enable or disable screenshot caching.
        
        Args:
            enable: True to enable caching
        """
        self.enable_caching = enable
        if not enable:
            self.cache.clear()
        print(f"💾 Screenshot caching {'enabled' if enable else 'disabled'}")
    
    def clear_cache(self):
        """Clear screenshot cache."""
        self.cache.clear()
        self.last_screenshot = None
        print("🗑️  Screenshot cache cleared")
    
    def get_monitor_count(self) -> int:
        """Get number of monitors connected."""
        return len(self.mss.monitors) - 1
    
    def capture_monitor(self, monitor_index: int = 1, 
                       resize: Optional[Tuple[int, int]] = None) -> Optional[np.ndarray]:
        """
        Capture specific monitor.
        
        Args:
            monitor_index: Monitor index (1-based)
            resize: Optional resize dimensions
            
        Returns:
            Screenshot as numpy array
        """
        with self.capture_lock:
            try:
                if monitor_index < 1 or monitor_index >= len(self.mss.monitors):
                    print(f"❌ Invalid monitor index: {monitor_index}")
                    return None
                
                monitor = self.mss.monitors[monitor_index]
                screenshot = self.mss.grab(monitor)
                
                img = np.array(screenshot)
                img = img[:, :, :3]  # Remove alpha channel
                
                if resize:
                    import cv2
                    img = cv2.resize(img, resize)
                
                return img
                
            except Exception as e:
                print(f"❌ Monitor capture error: {e}")
                return None


# Global instance for easy access
_screen_capture = None


def get_screen_capture() -> ScreenCapture:
    """Get or create global screen capture instance."""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCapture()
    return _screen_capture


# Example usage
if __name__ == "__main__":
    capture = ScreenCapture()
    
    print("📸 Screen Capture Test")
    print(f"Monitor info: {capture.get_capture_info()}")
    
    print("\n📹 Capturing screen...")
    screenshot = capture.capture_full_screen(resize=(800, 600))
    if screenshot is not None:
        print(f"✅ Screenshot captured: {screenshot.shape}")
    
    print("\n💾 Saving screenshot...")
    capture.save_screenshot()
    
    print("\n📊 Cache status:")
    print(f"   Cached screenshots: {len(capture.cache)}")
    print(f"   Last capture time: {datetime.fromtimestamp(capture.last_capture_time)}")
