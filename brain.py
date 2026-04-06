"""
JARVIS Brain Module
Handles AI reasoning and Groq API interaction
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT, TEMPERATURE, MAX_TOKENS, TOP_P, PRINT_STREAM
import json
from typing import List, Dict, Optional

class JarvisBrain:
    """Core AI reasoning engine using Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversation_history = []
        self.system_prompt = SYSTEM_PROMPT
    
    def _build_messages(self, user_input: str) -> List[Dict]:
        """Build message list with conversation history"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def query(self, user_input: str, stream: bool = True) -> str:
        """
        Query Groq API and get response
        
        Args:
            user_input: User's text input
            stream: Whether to stream the response
            
        Returns:
            Full response text
        """
        messages = self._build_messages(user_input)
        
        completion = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_completion_tokens=MAX_TOKENS,
            top_p=TOP_P,
            stream=stream
        )
        
        full_response = ""
        
        if stream:
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                if PRINT_STREAM:
                    print(content, end="", flush=True)
            if PRINT_STREAM:
                print()  # New line after streaming
        else:
            full_response = completion.choices[0].message.content
        
        # Store in conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": full_response})
        
        return full_response
    
    def parse_intent(self, user_input: str) -> Dict:
        """
        Convert natural language to structured intent (simplified, no JSON parsing)
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Simple intent structure
        """
        command_lower = user_input.lower()
        
        # Simple rule-based intent parsing (no Groq call)
        if any(word in command_lower for word in ['open', 'launch', 'start']):
            app_name = ''
            for app in ['chrome', 'spotify', 'vs code', 'brave', 'calculator', 'camera', 'calendar', 'clock']:
                if app in command_lower:
                    app_name = app
                    break
            if app_name:
                return {
                    "intent": "open_app",
                    "parameters": {"app_name": app_name},
                    "confidence": 0.95,
                    "requires_confirmation": False
                }
        
        if 'search' in command_lower or 'google' in command_lower:
            query = command_lower.replace('search', '').replace('google', '').strip()
            return {
                "intent": "search_web",
                "parameters": {"query": query},
                "confidence": 0.9,
                "requires_confirmation": False
            }
        
        # Default to conversation
        return {
            "intent": "conversation",
            "parameters": {"message": user_input},
            "confidence": 0.8,
            "requires_confirmation": False
        }
        return {
            "intent": "unknown",
            "parameters": {"original_input": user_input},
            "confidence": 0.0,
            "requires_confirmation": False
        }
    
    def add_context(self, context: str):
        """Add contextual information without cluttering history"""
        # These are system messages that guide behavior but don't count as conversation
        pass
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history.copy()
    
    def add_to_history(self, role: str, content: str):
        """Manually add message to history"""
        self.conversation_history.append({"role": role, "content": content})
