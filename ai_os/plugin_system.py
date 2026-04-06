"""
Plugin System - Extensibility framework for JARVIS

Allows adding:
- New agents
- New tools
- New integrations
- Custom workflows
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class Plugin(ABC):
    """Base class for JARVIS plugins"""
    
    def __init__(self, name: str, version: str, author: str = ""):
        self.id = f"plugin_{name}_{datetime.now().timestamp()}"
        self.name = name
        self.version = version
        self.author = author
        self.enabled = False
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    async def on_load(self):
        """Called when plugin is loaded"""
        raise NotImplementedError()
    
    @abstractmethod
    async def on_unload(self):
        """Called when plugin is unloaded"""
        raise NotImplementedError()
    
    @abstractmethod
    async def on_enable(self):
        """Called when plugin is enabled"""
        raise NotImplementedError()
    
    @abstractmethod
    async def on_disable(self):
        """Called when plugin is disabled"""
        raise NotImplementedError()
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get what this plugin provides"""
        raise NotImplementedError()
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get list of plugin IDs this plugin depends on"""
        raise NotImplementedError()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled,
            "capabilities": self.get_capabilities(),
            "dependencies": self.get_dependencies()
        }


class PluginRegistry:
    """Registry for managing plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.load_order: List[str] = []
    
    def register_plugin(self, plugin: Plugin) -> bool:
        """Register a plugin"""
        if plugin.id in self.plugins:
            return False
        
        self.plugins[plugin.id] = plugin
        self.load_order.append(plugin.id)
        return True
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister a plugin"""
        if plugin_id not in self.plugins:
            return False
        
        del self.plugins[plugin_id]
        self.load_order.remove(plugin_id)
        return True
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def get_plugin_by_name(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name"""
        for plugin in self.plugins.values():
            if plugin.name == name:
                return plugin
        return None
    
    def list_plugins(self, enabled_only: bool = False) -> List[Plugin]:
        """List all plugins"""
        plugins = list(self.plugins.values())
        
        if enabled_only:
            plugins = [p for p in plugins if p.enabled]
        
        return sorted(plugins, key=lambda p: self.load_order.index(p.id))
    
    def check_dependencies(self, plugin: Plugin) -> bool:
        """Check if all plugin dependencies are met"""
        dependencies = plugin.get_dependencies()
        
        for dep_name in dependencies:
            dep = self.get_plugin_by_name(dep_name)
            if not dep or not dep.enabled:
                return False
        
        return True


class PluginSystem:
    """
    Manage plugin lifecycle
    
    Handles:
    - Loading plugins
    - Enabling/disabling plugins
    - Dependency resolution
    - Plugin isolation
    """
    
    def __init__(self):
        self.registry = PluginRegistry()
        self.hooks: Dict[str, List[callable]] = {}
    
    async def load_plugin(self, plugin: Plugin) -> bool:
        """Load a plugin"""
        
        # Register plugin
        if not self.registry.register_plugin(plugin):
            return False
        
        # Call on_load
        try:
            await plugin.on_load()
            return True
        except Exception as e:
            print(f"Error loading plugin {plugin.name}: {e}")
            self.registry.unregister_plugin(plugin.id)
            return False
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        
        plugin = self.registry.get_plugin(plugin_id)
        if not plugin:
            return False
        
        # Disable first
        if plugin.enabled:
            await self.disable_plugin(plugin_id)
        
        # Call on_unload
        try:
            await plugin.on_unload()
            self.registry.unregister_plugin(plugin_id)
            return True
        except Exception as e:
            print(f"Error unloading plugin {plugin.name}: {e}")
            return False
    
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        
        plugin = self.registry.get_plugin(plugin_id)
        if not plugin:
            return False
        
        if plugin.enabled:
            return True
        
        # Check dependencies
        if not self.registry.check_dependencies(plugin):
            print(f"Plugin {plugin.name} has unmet dependencies")
            return False
        
        # Call on_enable
        try:
            await plugin.on_enable()
            plugin.enabled = True
            print(f"✅ Plugin enabled: {plugin.name}")
            return True
        except Exception as e:
            print(f"Error enabling plugin {plugin.name}: {e}")
            return False
    
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        
        plugin = self.registry.get_plugin(plugin_id)
        if not plugin:
            return False
        
        if not plugin.enabled:
            return True
        
        # Check if other plugins depend on this
        for other_plugin in self.registry.list_plugins(enabled_only=True):
            if plugin.name in other_plugin.get_dependencies():
                print(f"Cannot disable {plugin.name}: required by {other_plugin.name}")
                return False
        
        # Call on_disable
        try:
            await plugin.on_disable()
            plugin.enabled = False
            print(f"❌ Plugin disabled: {plugin.name}")
            return True
        except Exception as e:
            print(f"Error disabling plugin {plugin.name}: {e}")
            return False
    
    def register_hook(self, hook_name: str, callback: callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
    
    async def run_hook(self, hook_name: str, *args, **kwargs):
        """Run all callbacks for a hook"""
        if hook_name not in self.hooks:
            return
        
        for callback in self.hooks[hook_name]:
            try:
                if hasattr(callback, "__await__"):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                print(f"Error running hook {hook_name}: {e}")
    
    def get_plugin_list(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get list of plugins"""
        plugins = self.registry.list_plugins(enabled_only=enabled_only)
        return [p.to_dict() for p in plugins]
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins"""
        plugins = self.registry.list_plugins()
        
        return {
            "total_plugins": len(plugins),
            "enabled_plugins": len([p for p in plugins if p.enabled]),
            "disabled_plugins": len([p for p in plugins if not p.enabled]),
            "plugins": [p.to_dict() for p in plugins]
        }


# Example Plugin

class WeatherPlugin(Plugin):
    """Example plugin that provides weather data"""
    
    def __init__(self):
        super().__init__(
            name="Weather",
            version="1.0.0",
            author="JARVIS Team"
        )
    
    async def on_load(self):
        """Load weather plugin"""
        self.metadata["weather_service"] = "OpenWeatherMap"
    
    async def on_unload(self):
        """Unload weather plugin"""
        pass
    
    async def on_enable(self):
        """Enable weather plugin"""
        print("🌤️ Weather plugin enabled")
    
    async def on_disable(self):
        """Disable weather plugin"""
        print("🌤️ Weather plugin disabled")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Weather capabilities"""
        return {
            "get_current_weather": "Get current weather",
            "get_forecast": "Get weather forecast",
            "get_alerts": "Get weather alerts"
        }
    
    def get_dependencies(self) -> List[str]:
        """Dependencies"""
        return []


class NotificationPlugin(Plugin):
    """Example plugin that provides notification system"""
    
    def __init__(self):
        super().__init__(
            name="Notifications",
            version="1.0.0",
            author="JARVIS Team"
        )
        self.notifications: List[Dict[str, Any]] = []
    
    async def on_load(self):
        """Load notification plugin"""
        pass
    
    async def on_unload(self):
        """Unload notification plugin"""
        self.notifications.clear()
    
    async def on_enable(self):
        """Enable notification plugin"""
        print("🔔 Notification plugin enabled")
    
    async def on_disable(self):
        """Disable notification plugin"""
        print("🔔 Notification plugin disabled")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Notification capabilities"""
        return {
            "send_notification": "Send system notification",
            "get_notifications": "Get notification history",
            "clear_notifications": "Clear notifications"
        }
    
    def get_dependencies(self) -> List[str]:
        """Dependencies"""
        return []
    
    async def send_notification(self, title: str, message: str, level: str = "info"):
        """Send a notification"""
        notification = {
            "id": f"notif_{datetime.now().timestamp()}",
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        self.notifications.append(notification)
        print(f"📢 {level.upper()}: {title} - {message}")
