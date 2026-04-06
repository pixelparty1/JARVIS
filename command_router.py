"""
JARVIS Command Router Module
Handles intent detection and command routing
"""

import json
from typing import Dict, Callable, Any, Optional
from brain import JarvisBrain

class CommandRouter:
    """Routes user commands to appropriate handlers"""
    
    def __init__(self):
        self.brain = JarvisBrain()
        self.handlers = {}
        self.command_history = []
    
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


class IntentHandler:
    """Base class for intent handlers"""
    
    @staticmethod
    def handle(parameters: Dict, intent_data: Dict) -> Any:
        """
        Handle the intent
        
        Args:
            parameters: Parameters from parsed intent
            intent_data: Full intent data including confidence
            
        Returns:
            Result of handling
        """
        raise NotImplementedError
