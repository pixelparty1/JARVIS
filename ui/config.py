"""
JARVIS UI Configuration

Customize the JARVIS UI behavior, appearance, and shortcuts without editing code.
"""

import json
import os
from pathlib import Path


class UIConfig:
    """Configuration manager for JARVIS UI"""
    
    DEFAULT_CONFIG = {
        # Window Settings
        "window": {
            "width": 800,
            "height": 600,
            "opacity": 0.95,
            "always_on_top": False,
            "show_taskbar": True,
            "frameless": True,
            "draggable": True,
        },
        
        # Theme Settings
        "theme": {
            "name": "neon_dark",
            "primary_color": "#00D9FF",  # Cyan
            "secondary_color": "#0066CC",  # Blue
            "accent_color": "#FF00FF",  # Magenta
            "background_color": "#0A0E27",  # Dark blue-black
            "text_color": "#E0E0E0",  # Light gray
            "success_color": "#00FF00",  # Green
            "error_color": "#FF0000",  # Red
            "warning_color": "#FFD700",  # Gold
        },
        
        # Font Settings
        "fonts": {
            "family": "Consolas",  # Code-like font
            "size_normal": 11,
            "size_large": 13,
            "size_small": 9,
            "monospace": "Courier New",
        },
        
        # Input Settings
        "input": {
            "max_message_length": 5000,
            "enable_voice": True,
            "auto_send_voice": True,
            "voice_sensitivity": 0.7,
            "placeholder_text": "Ask JARVIS anything... (Ctrl+Space)",
        },
        
        # Chat Settings
        "chat": {
            "max_history": 1000,
            "show_timestamps": True,
            "typing_speed": "medium",  # fast, medium, slow
            "auto_scroll": True,
            "enable_markdown": True,
        },
        
        # Side Panel Settings
        "panels": {
            "show_on_startup": False,
            "default_panel": "none",  # none, tasks, notes, memory, logs
            "width": 300,
            "collapsible": True,
            "remember_state": True,
        },
        
        # Status Display Settings
        "status": {
            "show_metrics": True,
            "update_interval": 1000,  # milliseconds
            "show_active_agent": True,
            "show_task_queue": True,
        },
        
        # Animation Settings
        "animations": {
            "enabled": True,
            "smoothness": "medium",  # low, medium, high
            "duration": 300,  # milliseconds
            "fade_messages": True,
            "slide_panels": True,
        },
        
        # Keyboard Shortcuts
        "shortcuts": {
            "send_message": "Return",
            "new_line": "Shift+Return",
            "focus_input": "Ctrl+Space",
            "clear_chat": "Ctrl+L",
            "switch_panels": "Tab",
            "toggle_on_top": "Ctrl+T",
            "save_chat": "Ctrl+S",
            "exit": "Escape",
        },
        
        # Backend Integration
        "backend": {
            "host": "localhost",
            "port": 9000,
            "timeout": 30,
            "auto_reconnect": True,
            "log_level": "INFO",
        },
        
        # Voice Settings (when enabled)
        "voice": {
            "model": "groq",  # groq, google, azure
            "language": "en-US",
            "sample_rate": 16000,
            "chunk_size": 1024,
            "silence_timeout": 2.0,
            "show_waveform": True,
            "amplify_audio": 1.2,
        },
        
        # Behavior Settings
        "behavior": {
            "operation_mode": "interactive",  # interactive, autonomous, supervised
            "auto_execute_tasks": False,
            "confirm_dangerous_actions": True,
            "save_history": True,
            "save_location": "./chat_history",
        },
    }
    
    def __init__(self, config_file=None):
        """Initialize config from file or defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = config_file or self._get_default_config_path()
        self.load()
    
    @staticmethod
    def _get_default_config_path():
        """Get default config file path"""
        config_dir = Path(os.path.expanduser("~")) / ".jarvis"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "ui_config.json"
    
    def load(self):
        """Load config from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(self.config, user_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using defaults...")
    
    def save(self):
        """Save current config to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def _merge_config(self, base, update):
        """Recursively merge update dict into base dict"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key, default=None):
        """Get config value by dot notation (e.g., 'theme.primary_color')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Set config value by dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def reset_to_defaults(self):
        """Reset all config to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def get_all(self):
        """Get entire config"""
        return self.config.copy()
    
    def __repr__(self):
        return f"UIConfig(file={self.config_file})"


# Global config instance
_config_instance = None


def get_config():
    """Get or create global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = UIConfig()
    return _config_instance


def reset_config():
    """Reset global config"""
    global _config_instance
    if _config_instance:
        _config_instance.reset_to_defaults()


# Example usage
if __name__ == "__main__":
    print("JARVIS UI Configuration Manager")
    print()
    
    config = get_config()
    print(f"Config file: {config.config_file}")
    print()
    
    # Show some sample configs
    print("Sample configurations:")
    print(f"  Theme primary color: {config.get('theme.primary_color')}")
    print(f"  Window size: {config.get('window.width')}x{config.get('window.height')}")
    print(f"  Voice enabled: {config.get('input.enable_voice')}")
    print(f"  Send shortcut: {config.get('shortcuts.send_message')}")
    print()
    
    # Example: customize theme
    print("Example: Create custom theme")
    config.set('theme.primary_color', '#00FF00')  # Green instead of cyan
    config.set('theme.background_color', '#000000')  # Pure black
    config.save()
    print(f"  New primary color: {config.get('theme.primary_color')}")
    print("  Config saved!")
    print()
    
    # Show all config keys
    print("All available config sections:")
    for section in config.get_all().keys():
        print(f"  - {section}")
