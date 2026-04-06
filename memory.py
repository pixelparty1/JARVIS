"""
JARVIS Memory Module
Handles persistent memory storage and retrieval
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from config import MEMORY_FILE, LOG_FILE, ENABLE_LOGGING

class Memory:
    """Persistent memory management"""
    
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.log_file = LOG_FILE
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading memory: {e}")
                return self._create_default_memory()
        else:
            return self._create_default_memory()
    
    def _create_default_memory(self) -> Dict:
        """Create default memory structure"""
        return {
            "user_preferences": {},
            "notes": [],
            "reminders": [],
            "commands_history": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving memory: {e}")
    
    def set_preference(self, key: str, value: Any):
        """Set user preference"""
        self.memory["user_preferences"][key] = value
        self._save_memory()
        self.log(f"Set preference: {key} = {value}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.memory["user_preferences"].get(key, default)
    
    def get_all_preferences(self) -> Dict:
        """Get all preferences"""
        return self.memory["user_preferences"].copy()
    
    def add_command_to_history(self, command: str):
        """Add command to history"""
        entry = {
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["commands_history"].append(entry)
        
        # Keep only last 100 commands
        if len(self.memory["commands_history"]) > 100:
            self.memory["commands_history"] = self.memory["commands_history"][-100:]
        
        self._save_memory()
    
    def get_command_history(self, limit: int = 10) -> List[str]:
        """Get recent command history"""
        commands = [item["command"] for item in self.memory["commands_history"][-limit:]]
        return commands[::-1]  # Most recent first
    
    def add_note(self, title: str, content: str, tags: List[str] = None) -> str:
        """
        Add a note
        
        Args:
            title: Note title
            content: Note content
            tags: Optional tags
            
        Returns:
            Note ID
        """
        note_id = f"note_{len(self.memory['notes']) + 1}"
        note = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.memory["notes"].append(note)
        self._save_memory()
        self.log(f"Added note: {title}")
        
        return note_id
    
    def get_notes(self, tag: str = None) -> List[Dict]:
        """Get notes, optionally filtered by tag"""
        if tag:
            return [n for n in self.memory["notes"] if tag in n["tags"]]
        return self.memory["notes"].copy()
    
    def get_note(self, note_id: str) -> Optional[Dict]:
        """Get specific note"""
        for note in self.memory["notes"]:
            if note["id"] == note_id:
                return note
        return None
    
    def update_note(self, note_id: str, title: str = None, content: str = None):
        """Update a note"""
        for note in self.memory["notes"]:
            if note["id"] == note_id:
                if title:
                    note["title"] = title
                if content:
                    note["content"] = content
                note["updated_at"] = datetime.now().isoformat()
                self._save_memory()
                self.log(f"Updated note: {note_id}")
                return True
        return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        for i, note in enumerate(self.memory["notes"]):
            if note["id"] == note_id:
                del self.memory["notes"][i]
                self._save_memory()
                self.log(f"Deleted note: {note_id}")
                return True
        return False
    
    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by content"""
        query = query.lower()
        results = []
        for note in self.memory["notes"]:
            if query in note["title"].lower() or query in note["content"].lower():
                results.append(note)
        return results
    
    def add_reminder(self, title: str, timestamp: str, priority: str = "normal") -> str:
        """
        Add a reminder
        
        Args:
            title: Reminder title
            timestamp: When to remind (ISO format)
            priority: 'low', 'normal', 'high'
            
        Returns:
            Reminder ID
        """
        reminder_id = f"reminder_{len(self.memory['reminders']) + 1}"
        reminder = {
            "id": reminder_id,
            "title": title,
            "timestamp": timestamp,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        self.memory["reminders"].append(reminder)
        self._save_memory()
        self.log(f"Added reminder: {title}")
        
        return reminder_id
    
    def get_pending_reminders(self) -> List[Dict]:
        """Get all pending reminders"""
        return [r for r in self.memory["reminders"] if not r["completed"]]
    
    def complete_reminder(self, reminder_id: str) -> bool:
        """Mark reminder as completed"""
        for reminder in self.memory["reminders"]:
            if reminder["id"] == reminder_id:
                reminder["completed"] = True
                self._save_memory()
                self.log(f"Completed reminder: {reminder_id}")
                return True
        return False
    
    def log(self, message: str):
        """Log action"""
        if ENABLE_LOGGING:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] {message}\n"
                with open(self.log_file, 'a') as f:
                    f.write(log_entry)
            except Exception as e:
                print(f"❌ Logging error: {e}")
    
    def export_memory(self) -> str:
        """Export memory as JSON string"""
        return json.dumps(self.memory, indent=2)
    
    def import_memory(self, json_str: str) -> bool:
        """Import memory from JSON string"""
        try:
            self.memory = json.loads(json_str)
            self._save_memory()
            return True
        except Exception as e:
            print(f"❌ Error importing memory: {e}")
            return False
