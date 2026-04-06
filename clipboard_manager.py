"""
JARVIS Clipboard Manager Module
Handles clipboard history and management
"""

import pyperclip
import json
import os
from typing import List, Optional
from datetime import datetime
from config import CLIPBOARD_HISTORY_FILE, MAX_CLIPBOARD_ENTRIES

class ClipboardManager:
    """Clipboard history management"""
    
    def __init__(self):
        self.history_file = CLIPBOARD_HISTORY_FILE
        self.history = self._load_history()
        self.last_clipboard_content = None
    
    def _load_history(self) -> List[dict]:
        """Load clipboard history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading clipboard history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save clipboard history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-MAX_CLIPBOARD_ENTRIES:], f, indent=2)
        except Exception as e:
            print(f"❌ Error saving clipboard history: {e}")
    
    def get_clipboard(self) -> Optional[str]:
        """Get current clipboard content"""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"❌ Error reading clipboard: {e}")
            return None
    
    def set_clipboard(self, text: str) -> bool:
        """
        Set clipboard content
        
        Args:
            text: Text to copy to clipboard
            
        Returns:
            Success status
        """
        try:
            pyperclip.copy(text)
            # Add to history
            self._add_to_history(text)
            print(f"✅ Copied to clipboard ({len(text)} chars)")
            return True
        except Exception as e:
            print(f"❌ Error setting clipboard: {e}")
            return False
    
    def _add_to_history(self, content: str):
        """Add content to clipboard history"""
        entry = {
            "content": content[:500],  # Store first 500 chars
            "length": len(content),
            "timestamp": datetime.now().isoformat()
        }
        
        # Avoid duplicate consecutive entries
        if self.history and self.history[-1]["content"] == entry["content"]:
            return
        
        self.history.append(entry)
        
        # Keep only recent entries
        if len(self.history) > MAX_CLIPBOARD_ENTRIES:
            self.history = self.history[-MAX_CLIPBOARD_ENTRIES:]
        
        self._save_history()
    
    def get_history(self, limit: int = 10) -> str:
        """
        Get clipboard history
        
        Args:
            limit: Number of recent entries to return
            
        Returns:
            Formatted history
        """
        if not self.history:
            return "📋 Clipboard history is empty"
        
        recent = self.history[-limit:][::-1]  # Most recent first
        
        result = f"📋 Clipboard History ({len(recent)} recent):\n\n"
        
        for i, entry in enumerate(recent, 1):
            timestamp = entry["timestamp"]
            content = entry["content"]
            length = entry["length"]
            
            # Truncate for display
            display_content = content[:100] + "..." if len(content) > 100 else content
            
            result += f"{i}. [{timestamp}] ({length} chars)\n"
            result += f"   {display_content}\n\n"
        
        return result
    
    def search_history(self, query: str) -> str:
        """Search clipboard history"""
        query = query.lower()
        results = [h for h in self.history if query in h["content"].lower()]
        
        if not results:
            return f"❌ No clipboard entries found with: {query}"
        
        result = f"🔍 Found {len(results)} matching clipboard entries:\n\n"
        
        for i, entry in enumerate(results[-5:][::-1], 1):  # Show last 5
            result += f"{i}. {entry['content'][:100]}...\n"
        
        return result
    
    def clear_history(self) -> str:
        """Clear clipboard history"""
        self.history = []
        self._save_history()
        return "✅ Clipboard history cleared"
    
    def monitor_clipboard(self, callback, interval: int = 1):
        """
        Monitor clipboard for changes
        
        Args:
            callback: Function to call when clipboard changes
            interval: Check interval in seconds
        """
        import time
        import threading
        
        def monitor():
            while True:
                try:
                    current = self.get_clipboard()
                    
                    if current and current != self.last_clipboard_content:
                        self.last_clipboard_content = current
                        self._add_to_history(current)
                        callback(current)
                    
                    time.sleep(interval)
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    time.sleep(interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
