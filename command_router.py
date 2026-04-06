"""
JARVIS Command Router Module
Handles intent detection and command routing
"""

import json
from typing import Dict, Callable, Any, Optional
from brain import JarvisBrain
from system_control import SystemController

class CommandRouter:
    """Routes user commands to appropriate handlers"""
    
    def __init__(self):
        self.brain = JarvisBrain()
        self.system_control = SystemController()
        self.handlers = {}
        self.command_history = []
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default command handlers"""
        self.handlers['open_app'] = self._handle_open_app
        self.handlers['search_web'] = self._handle_search_web
        self.handlers['conversation'] = self._handle_conversation
    
    def _handle_open_app(self, parameters: Dict, intent_data: Dict) -> str:
        """Handle app opening"""
        app_name = parameters.get('app_name', '').lower()
        
        if app_name == 'chrome':
            return self.system_control.open_app('chrome')
        elif app_name == 'spotify':
            return self.system_control.open_app('spotify')
        elif app_name == 'vs code':
            return self.system_control.open_app('vs code')
        elif app_name == 'brave':
            return self.system_control.open_app('brave')
        elif app_name == 'calculator':
            return self.system_control.open_app('calculator')
        elif app_name == 'camera':
            return self.system_control.open_app('camera')
        elif app_name == 'calendar':
            return self.system_control.open_app('calendar')
        elif app_name == 'clock':
            return self.system_control.open_app('clock')
        else:
            return self.system_control.open_app(app_name)
    
    def _handle_search_web(self, parameters: Dict, intent_data: Dict) -> str:
        """Handle web search"""
        query = parameters.get('query', '').strip()
        if not query:
            return "❌ No search query provided"
        
        try:
            import webbrowser
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"✅ Searching Google for: {query}"
        except Exception as e:
            return f"❌ Search error: {str(e)}"
    
    def _handle_conversation(self, parameters: Dict, intent_data: Dict) -> str:
        """Handle conversational response"""
        message = parameters.get('message', '')
        return self.brain.query(message)
    
    def register_handler(self, intent: str, handler: Callable):
        """
        Register a handler for an intent
        
        Args:
            intent: Intent name (e.g., 'open_app')
            handler: Function to handle this intent
        """
        self.handlers[intent.lower()] = handler
        print(f"✅ Registered handler for intent: {intent}")
    
    def route_command(self, user_input: str) -> Any:
        """
        Parse user input and route to appropriate handler
        
        Args:
            user_input: Natural language user input
            
        Returns:
            Handler result or error message
        """
        print(f"\n🔀 Routing command: {user_input}")
        
        # Store in history
        self.command_history.append(user_input)
        
        # Parse to intent
        intent_data = self.brain.parse_intent(user_input)
        
        print(f"📊 Intent: {intent_data['intent']}")
        print(f"📋 Parameters: {intent_data['parameters']}")
        print(f"🎯 Confidence: {intent_data['confidence']}")
        
        intent = intent_data['intent'].lower()
        parameters = intent_data.get('parameters', {})
        
        # Check if handler exists
        if intent in self.handlers:
            try:
                result = self.handlers[intent](parameters, intent_data)
                return result
            except Exception as e:
                return f"Error executing command: {str(e)}"
        else:
            # Fallback to conversational response
            response = self.brain.query(user_input)
            return response
    
    def handle_unknown_intent(self, intent_data: Dict) -> str:
        """Handle unknown intent gracefully"""
        original_input = intent_data.get('parameters', {}).get('original_input', '')
        response = self.brain.query(original_input)
        return response
    
    def get_command_history(self) -> list:
        """Get command history"""
        return self.command_history.copy()
    
    def clear_history(self):
        """Clear command history"""
        self.command_history = []
