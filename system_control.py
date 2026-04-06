"""
JARVIS System Control Module
Handles OS-level actions and system controls
"""

import os
import subprocess
import platform
import psutil
import threading
from typing import Dict, Any
from config import COMMON_APP_PATHS

class SystemController:
    """System control and OS interactions"""
    
    def open_app(self, app_name: str) -> str:
        """
        Open an application with multiple app support
        
        Args:
            app_name: Name of application to open
            
        Returns:
            Status message
        """
        app_name_lower = app_name.lower().strip()
        
        # Clean app names
        app_name_lower = app_name_lower.replace('vs code', 'code').replace('visual studio code', 'code')
        
        # Check if app is in common paths
        if app_name_lower in COMMON_APP_PATHS:
            paths = COMMON_APP_PATHS[app_name_lower]
            for path in paths:
                # Replace {user} with actual username
                path = path.replace("{user}", os.getlogin())
                
                if os.path.exists(path):
                    try:
                        subprocess.Popen(path)
                        return f"✅ Opening {app_name}"
                    except Exception as e:
                        return f"❌ Failed to open {app_name}: {str(e)}"
        
        # Direct app routing
        if app_name_lower == 'chrome':
            try:
                subprocess.Popen('chrome')
                return "✅ Opening Chrome"
            except:
                return self._open_chrome()
        
        elif app_name_lower == 'spotify':
            try:
                subprocess.Popen('spotify')
                return "✅ Opening Spotify"
            except Exception as e:
                return f"❌ Spotify error: {str(e)}"
        
        elif app_name_lower == 'code' or app_name_lower == 'vs code':
            try:
                subprocess.Popen('code')
                return "✅ Opening VS Code"
            except Exception as e:
                return f"❌ VS Code error: {str(e)}"
        
        elif app_name_lower == 'brave':
            try:
                subprocess.Popen('brave')
                return "✅ Opening Brave"
            except Exception as e:
                return f"❌ Brave error: {str(e)}"
        
        elif app_name_lower == 'calculator':
            try:
                if platform.system() == "Windows":
                    subprocess.Popen('calc')
                else:
                    subprocess.Popen('calculator')
                return "✅ Opening Calculator"
            except Exception as e:
                return f"❌ Calculator error: {str(e)}"
        
        elif app_name_lower == 'camera':
            try:
                return self._open_camera()
            except Exception as e:
                return f"❌ Camera error: {str(e)}"
        
        elif app_name_lower == 'calendar':
            try:
                import webbrowser
                webbrowser.open("https://calendar.google.com")
                return "✅ Opening Google Calendar"
            except Exception as e:
                return f"❌ Calendar error: {str(e)}"
        
        elif app_name_lower == 'clock':
            try:
                if platform.system() == "Windows":
                    subprocess.Popen('clock')
                else:
                    subprocess.Popen('clock')
                return "✅ Opening Clock"
            except Exception as e:
                return f"❌ Clock error: {str(e)}"
        
        # Fallback: try to open with system default
        try:
            if platform.system() == "Windows":
                os.startfile(app_name)
            else:
                subprocess.Popen(['open', app_name])
            return f"✅ Opening {app_name}"
        except Exception as e:
            return f"❌ Failed to open {app_name}: {str(e)}"
    
    def _open_chrome(self) -> str:
        """Open Chrome"""
        try:
            import webbrowser
            webbrowser.open("https://www.google.com")
            return "✅ Opening Google Chrome"
        except Exception as e:
            return f"❌ Chrome error: {str(e)}"
    
    def _open_camera(self) -> str:
        """Open camera"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "❌ Camera not available"
            
            def camera_thread():
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    cv2.imshow("JARVIS Camera", frame)
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC to close
                        break
                cap.release()
                cv2.destroyAllWindows()
            
            thread = threading.Thread(target=camera_thread, daemon=True)
            thread.start()
            return "✅ Opening camera (press ESC to close)"
        except ImportError:
            return "❌ OpenCV not installed: pip install opencv-python"
        except Exception as e:
            return f"❌ Camera error: {str(e)}"
    
    @staticmethod
    def close_app(app_name: str) -> str:
        """
        Close an application
        
        Args:
            app_name: Name of application to close
            
        Returns:
            Status message
        """
        app_name = app_name.lower().strip()
        
        try:
            # Find process by name
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        return f"✅ Closed {app_name}"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return f"⚠️ {app_name} not found in running processes"
        except Exception as e:
            return f"❌ Error closing {app_name}: {str(e)}"
    
    @staticmethod
    def control_volume(action: str, amount: int = 5) -> str:
        """
        Control system volume
        
        Args:
            action: 'increase', 'decrease', or 'mute'
            amount: Volume adjustment amount
            
        Returns:
            Status message
        """
        try:
            if platform.system() == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                current_vol = volume.GetMasterVolumeLevelScalar()
                
                if action.lower() == "increase":
                    new_vol = min(current_vol + (amount / 100), 1.0)
                elif action.lower() == "decrease":
                    new_vol = max(current_vol - (amount / 100), 0.0)
                elif action.lower() == "mute":
                    volume.SetMute(1, None)
                    return "✅ Volume muted"
                else:
                    return f"❌ Unknown action: {action}"
                
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                return f"✅ Volume {action}d to {int(new_vol * 100)}%"
            else:
                return "⚠️ Volume control not available on this system"
        
        except Exception as e:
            return f"❌ Volume control error: {str(e)}"
    
    @staticmethod
    def get_system_info() -> str:
        """Get system information"""
        try:
            info = {
                "OS": platform.system(),
                "OS Version": platform.release(),
                "Processor": platform.processor(),
                "CPU Count": psutil.cpu_count(),
                "RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "CPU Usage": f"{psutil.cpu_percent()}%",
                "Memory Usage": f"{psutil.virtual_memory().percent}%"
            }
            
            result = "📊 System Information:\n"
            for key, value in info.items():
                result += f"  • {key}: {value}\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting system info: {str(e)}"
    
    @staticmethod
    def shutdown(timeout: int = 60) -> str:
        """
        Shutdown system
        
        Args:
            timeout: Seconds until shutdown
            
        Returns:
            Status message
        """
        try:
            if platform.system() == "Windows":
                subprocess.run(['shutdown', '/s', '/t', str(timeout)], check=True)
            else:
                subprocess.run(['shutdown', '-h', str(timeout)], check=True)
            
            return f"⚠️ System will shutdown in {timeout} seconds"
        except Exception as e:
            return f"❌ Shutdown error: {str(e)}"
    
    @staticmethod
    def restart(timeout: int = 60) -> str:
        """
        Restart system
        
        Args:
            timeout: Seconds until restart
            
        Returns:
            Status message
        """
        try:
            if platform.system() == "Windows":
                subprocess.run(['shutdown', '/r', '/t', str(timeout)], check=True)
            else:
                subprocess.run(['shutdown', '-r', str(timeout)], check=True)
            
            return f"⚠️ System will restart in {timeout} seconds"
        except Exception as e:
            return f"❌ Restart error: {str(e)}"
    
    @staticmethod
    def cancel_shutdown() -> str:
        """Cancel pending shutdown"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['shutdown', '/a'], check=True)
            else:
                # For Linux/Mac
                subprocess.run(['sudo', 'shutdown', '-c'], check=True)
            
            return "✅ Shutdown cancelled"
        except Exception as e:
            return f"❌ Error cancelling shutdown: {str(e)}"
    
    @staticmethod
    def list_running_apps() -> str:
        """List all running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Return unique apps sorted
            unique_apps = sorted(set(apps))
            return f"🖥️ Running applications ({len(unique_apps)}):\n" + \
                   "\n".join([f"  • {app}" for app in unique_apps[:20]]) + \
                   (f"\n  ... and {len(unique_apps) - 20} more" if len(unique_apps) > 20 else "")
        except Exception as e:
            return f"❌ Error listing apps: {str(e)}"
