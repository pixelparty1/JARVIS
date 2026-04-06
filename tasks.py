"""
JARVIS Tasks Module
Handles alarms, timers, and task automation
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Callable, Optional, List
import json
from config import TASKS_FILE

class TaskManager:
    """Manages tasks, timers, and alarms"""
    
    def __init__(self):
        self.tasks = {}
        self.timers = {}
        self.alarms = {}
        self.running_tasks = set()
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from file"""
        try:
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', {})
                    self.alarms = data.get('alarms', {})
        except Exception as e:
            print(f"❌ Error loading tasks: {e}")
    
    def _save_tasks(self):
        """Save tasks to file"""
        try:
            data = {
                'tasks': self.tasks,
                'alarms': self.alarms
            }
            with open(TASKS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")
    
    def create_timer(self, duration_seconds: int, name: str = None) -> str:
        """
        Create a timer
        
        Args:
            duration_seconds: Timer duration in seconds
            name: Optional timer name
            
        Returns:
            Timer ID
        """
        timer_id = f"timer_{len(self.timers) + 1}"
        name = name or f"Timer {len(self.timers) + 1}"
        
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        
        self.timers[timer_id] = {
            "name": name,
            "duration": duration_seconds,
            "start_time": datetime.now().isoformat(),
            "end_time": end_time.isoformat(),
            "active": True
        }
        
        print(f"⏱️ Timer '{name}' set for {duration_seconds} seconds")
        
        # Start timer in background
        self._start_timer_thread(timer_id, duration_seconds)
        
        return timer_id
    
    def _start_timer_thread(self, timer_id: str, duration: int):
        """Start timer in background thread"""
        def timer_handler():
            self.running_tasks.add(timer_id)
            time.sleep(duration)
            
            if timer_id in self.timers:
                self.timers[timer_id]["active"] = False
                print(f"🔔 Timer '{self.timers[timer_id]['name']}' finished!")
            
            self.running_tasks.discard(timer_id)
        
        thread = threading.Thread(target=timer_handler, daemon=True)
        thread.start()
    
    def get_timer_status(self, timer_id: str) -> Optional[Dict]:
        """Get timer status"""
        if timer_id not in self.timers:
            return None
        
        timer = self.timers[timer_id]
        if timer["active"]:
            elapsed = (datetime.now() - datetime.fromisoformat(timer["start_time"])).total_seconds()
            remaining = timer["duration"] - elapsed
            return {
                "name": timer["name"],
                "remaining": max(0, int(remaining)),
                "total": timer["duration"],
                "active": True
            }
        
        return timer
    
    def cancel_timer(self, timer_id: str) -> str:
        """Cancel a timer"""
        if timer_id in self.timers:
            self.timers[timer_id]["active"] = False
            return f"✅ Timer '{self.timers[timer_id]['name']}' cancelled"
        return f"❌ Timer not found: {timer_id}"
    
    def list_timers(self) -> str:
        """List all timers"""
        if not self.timers:
            return "No active timers"
        
        result = "⏱️ Active Timers:\n"
        for timer_id, timer in self.timers.items():
            if timer["active"]:
                status = self.get_timer_status(timer_id)
                if status:
                    result += f"  • {status['name']}: {status['remaining']}s remaining\n"
        
        return result
    
    def create_alarm(self, time_str: str, name: str = "Alarm") -> str:
        """
        Create an alarm
        
        Args:
            time_str: Time in HH:MM format or "tomorrow HH:MM", etc.
            name: Alarm name
            
        Returns:
            Alarm ID
        """
        alarm_id = f"alarm_{len(self.alarms) + 1}"
        
        # Parse time (simplified)
        try:
            if ":" in time_str:
                hour, minute = map(int, time_str.split(":"))
                alarm_time = datetime.now().replace(hour=hour, minute=minute, second=0)
                
                # If time is in the past, set for tomorrow
                if alarm_time < datetime.now():
                    alarm_time += timedelta(days=1)
            else:
                return "❌ Invalid time format. Use HH:MM"
        except:
            return "❌ Could not parse time"
        
        self.alarms[alarm_id] = {
            "name": name,
            "time": alarm_time.isoformat(),
            "active": True
        }
        
        # Save to file
        self._save_tasks()
        
        print(f"⏰ Alarm '{name}' set for {alarm_time.strftime('%H:%M')}")
        
        # Start alarm thread
        self._start_alarm_thread(alarm_id, alarm_time)
        
        return alarm_id
    
    def _start_alarm_thread(self, alarm_id: str, alarm_time: datetime):
        """Start alarm check in background"""
        def alarm_handler():
            self.running_tasks.add(alarm_id)
            
            while self.alarms.get(alarm_id, {}).get("active", False):
                current_time = datetime.now()
                
                if current_time >= alarm_time:
                    print(f"\n🔔 ALARM: {self.alarms[alarm_id]['name']}!")
                    self.alarms[alarm_id]["active"] = False
                    self._save_tasks()
                    break
                
                time.sleep(10)  # Check every 10 seconds
            
            self.running_tasks.discard(alarm_id)
        
        thread = threading.Thread(target=alarm_handler, daemon=True)
        thread.start()
    
    def cancel_alarm(self, alarm_id: str) -> str:
        """Cancel an alarm"""
        if alarm_id in self.alarms:
            self.alarms[alarm_id]["active"] = False
            self._save_tasks()
            return f"✅ Alarm cancelled"
        return f"❌ Alarm not found"
    
    def list_alarms(self) -> str:
        """List all active alarms"""
        active_alarms = [a for a in self.alarms.values() if a["active"]]
        
        if not active_alarms:
            return "No active alarms"
        
        result = "⏰ Active Alarms:\n"
        for alarm in active_alarms:
            alarm_time = datetime.fromisoformat(alarm["time"])
            result += f"  • {alarm['name']}: {alarm_time.strftime('%H:%M')}\n"
        
        return result
    
    def schedule_task(self, name: str, callback: Callable, delay_seconds: int):
        """
        Schedule a task to run after delay
        
        Args:
            name: Task name
            callback: Function to execute
            delay_seconds: Delay before execution
            
        Returns:
            Task ID
        """
        task_id = f"task_{len(self.tasks) + 1}"
        
        def task_handler():
            self.running_tasks.add(task_id)
            time.sleep(delay_seconds)
            try:
                callback()
                print(f"✅ Task completed: {name}")
            except Exception as e:
                print(f"❌ Task failed: {name} - {str(e)}")
            finally:
                self.running_tasks.discard(task_id)
        
        thread = threading.Thread(target=task_handler, daemon=True)
        thread.start()
        
        return task_id
    
    def get_running_tasks(self) -> List[str]:
        """Get list of running task IDs"""
        return list(self.running_tasks)


# Make sure os is imported
import os
