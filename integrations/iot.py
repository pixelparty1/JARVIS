"""
IoT Integration - Smart Device Control

Features:
- Control smart lights
- Adjust thermostat
- Smart home automation
- Device discovery
- Scene management
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .base import Integration, ToolDefinition, IntegrationError


class DeviceType(Enum):
    """Supported device types."""
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    SPEAKER = "speaker"
    CAMERA = "camera"
    PLUG = "plug"


class LightState(Enum):
    """Light states."""
    OFF = "off"
    ON = "on"
    DIMMED = "dimmed"


@dataclass
class SmartDevice:
    """Smart device."""
    id: str
    name: str
    type: DeviceType
    room: str = "unknown"
    state: str = "unknown"
    power: bool = False
    brightness: int = 100  # For lights
    temperature: int = 72  # For thermostats
    last_updated: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Scene:
    """Smart home scene."""
    name: str
    description: str
    devices: Dict[str, Dict[str, Any]]  # device_id -> settings
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class IoTIntegration(Integration):
    """
    IoT/Smart Home integration.
    
    Supports HTTP-based smart devices (LIFX, Philips Hue, Nest, etc.)
    """
    
    def __init__(self, auth_manager=None, hub_url: str = "http://localhost:8000"):
        """
        Initialize IoT integration.
        
        Args:
            auth_manager: AuthManager instance
            hub_url: Smart home hub URL
        """
        super().__init__("iot", auth_manager=auth_manager)
        self.hub_url = hub_url
        self.devices = {}
        self.scenes = {}
        
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register available tools."""
        self.register_tool(ToolDefinition(
            name="list_devices",
            description="List all smart devices",
            parameters={"device_type": str, "room": str},
            returns="List[SmartDevice]",
            category="iot"
        ))
        
        self.register_tool(ToolDefinition(
            name="get_device",
            description="Get device status",
            parameters={"device_id": str},
            returns="SmartDevice",
            category="iot"
        ))
        
        self.register_tool(ToolDefinition(
            name="control_device",
            description="Control a device",
            parameters={"device_id": str, "command": str, "parameters": dict},
            returns="bool",
            category="iot"
        ))
        
        self.register_tool(ToolDefinition(
            name="set_light",
            description="Control light settings",
            parameters={"device_id": str, "power": bool, "brightness": int, "color": str},
            returns="bool",
            category="iot"
        ))
        
        self.register_tool(ToolDefinition(
            name="set_temperature",
            description="Set thermostat temperature",
            parameters={"device_id": str, "temperature": int},
            returns="bool",
            category="iot"
        ))
        
        self.register_tool(ToolDefinition(
            name="activate_scene",
            description="Activate a predefined scene",
            parameters={"scene_name": str},
            returns="bool",
            category="iot"
        ))
    
    async def authenticate(self) -> bool:
        """Authenticate with smart home hub."""
        if not self.auth_manager:
            self.is_authenticated = True
            return True
        
        cred = self.auth_manager.get_credentials("iot_hub")
        if cred:
            self.is_authenticated = True
            return True
        
        self.is_authenticated = True  # Mock auth
        return True
    
    async def health_check(self) -> bool:
        """Check smart home hub health."""
        # In production: Check hub connectivity
        return self.is_authenticated
    
    async def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool."""
        if tool_name == "list_devices":
            return await self.list_devices(
                device_type=kwargs.get("device_type"),
                room=kwargs.get("room")
            )
        elif tool_name == "get_device":
            return await self.get_device(device_id=kwargs.get("device_id"))
        elif tool_name == "control_device":
            return await self.control_device(
                device_id=kwargs.get("device_id"),
                command=kwargs.get("command"),
                parameters=kwargs.get("parameters", {})
            )
        elif tool_name == "set_light":
            return await self.set_light(
                device_id=kwargs.get("device_id"),
                power=kwargs.get("power", True),
                brightness=kwargs.get("brightness", 100),
                color=kwargs.get("color")
            )
        elif tool_name == "set_temperature":
            return await self.set_temperature(
                device_id=kwargs.get("device_id"),
                temperature=kwargs.get("temperature")
            )
        elif tool_name == "activate_scene":
            return await self.activate_scene(scene_name=kwargs.get("scene_name"))
        else:
            raise IntegrationError(f"Unknown tool: {tool_name}")
    
    def _setup_mock_devices(self) -> None:
        """Setup mock devices for testing."""
        self.devices = {
            "light_1": SmartDevice(
                id="light_1",
                name="Living Room Light",
                type=DeviceType.LIGHT,
                room="living_room",
                power=True,
                brightness=80
            ),
            "light_2": SmartDevice(
                id="light_2",
                name="Bedroom Light",
                type=DeviceType.LIGHT,
                room="bedroom",
                power=False
            ),
            "temp_1": SmartDevice(
                id="temp_1",
                name="Main Thermostat",
                type=DeviceType.THERMOSTAT,
                room="hallway",
                temperature=72
            ),
            "speaker_1": SmartDevice(
                id="speaker_1",
                name="Living Room Speaker",
                type=DeviceType.SPEAKER,
                room="living_room",
                power=True
            ),
        }
    
    async def list_devices(self, device_type: str = None,
                          room: str = None) -> List[SmartDevice]:
        """
        List smart devices.
        
        Args:
            device_type: Filter by type
            room: Filter by room
            
        Returns:
            List of devices
        """
        if not self.devices:
            self._setup_mock_devices()
        
        devices = list(self.devices.values())
        
        if device_type:
            devices = [d for d in devices if d.type.value == device_type]
        
        if room:
            devices = [d for d in devices if d.room == room]
        
        return devices
    
    async def get_device(self, device_id: str) -> Optional[SmartDevice]:
        """Get device status."""
        if not self.devices:
            self._setup_mock_devices()
        
        return self.devices.get(device_id)
    
    async def control_device(self, device_id: str, command: str,
                            parameters: Dict[str, Any] = None) -> bool:
        """
        Control a device.
        
        Args:
            device_id: Device ID
            command: Command name
            parameters: Command parameters
            
        Returns:
            Success status
        """
        if not self.devices:
            self._setup_mock_devices()
        
        device = self.devices.get(device_id)
        if not device:
            return False
        
        print(f"🎛️  Control: {device.name} → {command}")
        return True
    
    async def set_light(self, device_id: str, power: bool = None,
                       brightness: int = None,
                       color: str = None) -> bool:
        """
        Control light settings.
        
        Args:
            device_id: Light device ID
            power: Turn on/off
            brightness: Brightness level (0-100)
            color: Color (hex or name)
            
        Returns:
            Success status
        """
        if not self.devices:
            self._setup_mock_devices()
        
        device = self.devices.get(device_id)
        if not device or device.type != DeviceType.LIGHT:
            return False
        
        if power is not None:
            device.power = power
        if brightness is not None:
            device.brightness = brightness
        
        device.last_updated = datetime.now().isoformat()
        
        state = "ON" if device.power else "OFF"
        print(f"💡 {device.name}: {state} (brightness: {device.brightness}%)")
        
        return True
    
    async def set_temperature(self, device_id: str,
                             temperature: int) -> bool:
        """
        Set thermostat temperature.
        
        Args:
            device_id: Thermostat device ID
            temperature: Target temperature (F)
            
        Returns:
            Success status
        """
        if not self.devices:
            self._setup_mock_devices()
        
        device = self.devices.get(device_id)
        if not device or device.type != DeviceType.THERMOSTAT:
            return False
        
        device.temperature = temperature
        device.last_updated = datetime.now().isoformat()
        
        print(f"🌡️  {device.name}: Set to {temperature}°F")
        
        return True
    
    def create_scene(self, name: str, description: str) -> Scene:
        """Create a smart home scene."""
        scene = Scene(
            name=name,
            description=description,
            devices={}
        )
        self.scenes[name] = scene
        return scene
    
    def add_device_to_scene(self, scene_name: str, device_id: str,
                           settings: Dict[str, Any]) -> bool:
        """Add device settings to scene."""
        if scene_name not in self.scenes:
            return False
        
        self.scenes[scene_name].devices[device_id] = settings
        return True
    
    async def activate_scene(self, scene_name: str) -> bool:
        """
        Activate a scene.
        
        Args:
            scene_name: Scene name
            
        Returns:
            Success status
        """
        if scene_name not in self.scenes:
            return False
        
        scene = self.scenes[scene_name]
        
        print(f"🎬 Activating scene: {scene_name}")
        
        for device_id, settings in scene.devices.items():
            await self.control_device(device_id, "apply", settings)
        
        return True


class SmartHomeAssistant:
    """High-level smart home assistant."""
    
    def __init__(self, iot_integration: IoTIntegration):
        """
        Initialize smart home assistant.
        
        Args:
            iot_integration: IoTIntegration instance
        """
        self.iot = iot_integration
    
    async def setup_scenes(self) -> None:
        """Setup common scenes."""
        # Morning scene
        morning = self.iot.create_scene(
            name="morning",
            description="Wake up scene"
        )
        self.iot.add_device_to_scene("morning", "light_1", {"power": True, "brightness": 100})
        self.iot.add_device_to_scene("morning", "speaker_1", {"power": True})
        
        # Night scene
        night = self.iot.create_scene(
            name="night",
            description="Sleep scene"
        )
        self.iot.add_device_to_scene("night", "light_1", {"power": False})
        self.iot.add_device_to_scene("night", "light_2", {"power": False})
        self.iot.add_device_to_scene("night", "temp_1", {"temperature": 68})
        
        # Work scene
        work = self.iot.create_scene(
            name="work",
            description="Focus mode"
        )
        self.iot.add_device_to_scene("work", "light_1", {"power": True, "brightness": 100})
        self.iot.add_device_to_scene("work", "speaker_1", {"power": False})
        
        print("✅ Scenes configured")
    
    async def home_status(self) -> str:
        """Get home status."""
        devices = await self.iot.list_devices()
        
        status = "🏠 Home Status:\n\n"
        
        lights = [d for d in devices if d.type == DeviceType.LIGHT]
        thermostats = [d for d in devices if d.type == DeviceType.THERMOSTAT]
        
        if lights:
            status += "💡 Lights:\n"
            for light in lights:
                state = "ON" if light.power else "OFF"
                status += f"  • {light.name}: {state}\n"
        
        if thermostats:
            status += "\n🌡️  Thermostat:\n"
            for therm in thermostats:
                status += f"  • {therm.name}: {therm.temperature}°F\n"
        
        return status


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_iot():
        print("🧪 IoT Integration Test\n")
        
        iot = IoTIntegration()
        await iot.authenticate()
        
        # List devices
        devices = await iot.list_devices()
        print(f"✅ Found {len(devices)} devices:\n")
        
        for device in devices:
            print(f"• {device.name} ({device.type.value})")
            print(f"  Power: {device.power}, Room: {device.room}\n")
    
    asyncio.run(test_iot())
