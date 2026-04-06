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
        Convert natural language to structured intent
        
        Args:
            user_input: User's natural language input
            
        Returns:
            JSON intent structure
        """
        intent_prompt = f"""Analyze this user request and convert it to a structured intent JSON.

User request: "{user_input}"

Return ONLY a valid JSON object with these fields:
- "intent": primary action (e.g., "open_app", "get_weather", "add_note", "control_volume", "search_web", "set_timer", "read_note")
- "parameters": dict with specific details needed for the action
- "confidence": 0-1 how confident you are about this interpretation
- "requires_confirmation": boolean if action needs user confirmation

Examples:
{{"intent": "open_app", "parameters": {{"app_name": "chrome"}}, "confidence": 0.95, "requires_confirmation": false}}
{{"intent": "control_volume", "parameters": {{"action": "increase", "amount": 10}}, "confidence": 0.9, "requires_confirmation": false}}
{{"intent": "search_web", "parameters": {{"query": "python programming"}}, "confidence": 0.85, "requires_confirmation": false}}

Return ONLY the JSON, no other text."""
        
        messages = [
            {"role": "system", "content": "You are a JSON intent parser. Return ONLY valid JSON, nothing else."},
            {"role": "user", "content": intent_prompt}
        ]
        
        completion = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,  # Lower temperature for structured output
            max_completion_tokens=500,
            top_p=1.0,
            stream=False
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        try:
            # Extract JSON from response (in case there's extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                intent = json.loads(json_str)
                return intent
        except json.JSONDecodeError:
            pass
        
        # Fallback intent
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
