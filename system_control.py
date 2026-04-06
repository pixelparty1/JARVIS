"""
JARVIS System Control Module
Handles OS-level actions and system controls
"""

import os
import subprocess
import platform
import psutil
from typing import Dict, Any
from config import COMMON_APP_PATHS

class SystemController:
    """System control and OS interactions"""
    
    @staticmethod
    def open_app(app_name: str) -> str:
        """
        Open an application
        
        Args:
            app_name: Name of application to open
            
        Returns:
            Status message
        """
        app_name = app_name.lower().strip()
        
        # Check if app is in common paths
        if app_name in COMMON_APP_PATHS:
            paths = COMMON_APP_PATHS[app_name]
            for path in paths:
                # Replace {user} with actual username
                path = path.replace("{user}", os.getlogin())
                
                if os.path.exists(path):
                    try:
                        subprocess.Popen(path)
                        return f"✅ Opening {app_name}"
                    except Exception as e:
                        return f"❌ Failed to open {app_name}: {str(e)}"
            
            return f"❌ {app_name} not found at expected locations"
        
        # Fallback: try to open with system default
        try:
            if platform.system() == "Windows":
                os.startfile(app_name)
            else:
                subprocess.Popen(['open', app_name])
            return f"✅ Opening {app_name}"
        except Exception as e:
            return f"❌ Failed to open {app_name}: {str(e)}"
    
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
