"""
Scene Analyzer - Intelligent Context Understanding

Features:
- Analyze overall scene context
- Integrate camera, faces, emotions, gestures
- Use Groq for intelligent reasoning
- Generate contextual responses
- Predict user intent
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import base64
import io

try:
    from groq import Groq
except ImportError:
    Groq = None


@dataclass
class SceneContext:
    """Scene analysis context."""
    timestamp: str
    people_present: List[str]
    emotions: Dict[str, Any]
    gestures: List[str]
    activity: str
    energy_level: str  # high, medium, low
    recommendation: str
    urgency: str  # low, medium, high


class SceneAnalyzer:
    """
    Intelligent scene analysis using Groq.
    
    Combines:
    - Face recognition (who's present)
    - Emotion detection (how they feel)
    - Gesture recognition (what they're doing)
    - Context from memory/calendar/email
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize scene analyzer.
        
        Args:
            api_key: Groq API key (if None, will use GROQ_API_KEY env var)
        """
        self.client = None
        if Groq:
            self.client = Groq(api_key=api_key) if api_key else Groq()
        
        self.context_memory = []
        self.max_memory = 50
    
    async def analyze_scene(self,
                           people: List[Dict],
                           emotions: List[Dict],
                           gestures: List[str],
                           additional_context: Dict = None) -> SceneContext:
        """
        Analyze scene and generate context.
        
        Args:
            people: List of {"name": str, "confidence": float}
            emotions: List of {"emotion": str, "confidence": float, "response": str}
            gestures: List of gesture names
            additional_context: Optional context (calendar, email, memory, etc.)
            
        Returns:
            SceneContext with analysis
        """
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            people, emotions, gestures, additional_context
        )
        
        # Get Groq analysis
        analysis = {}
        if self.client:
            analysis = await self._groq_analyze(prompt)
        else:
            # Fallback to simple analysis
            analysis = self._simple_analyze(people, emotions, gestures)
        
        # Create context
        context = SceneContext(
            timestamp=datetime.now().isoformat(),
            people_present=[p["name"] for p in people],
            emotions=self._summarize_emotions(emotions),
            gestures=gestures,
            activity=analysis.get("activity", "unknown"),
            energy_level=analysis.get("energy_level", "medium"),
            recommendation=analysis.get("recommendation", "Keep working!"),
            urgency=analysis.get("urgency", "low")
        )
        
        # Add to memory
        self.context_memory.append(context)
        if len(self.context_memory) > self.max_memory:
            self.context_memory.pop(0)
        
        return context
    
    def _build_analysis_prompt(self,
                               people: List[Dict],
                               emotions: List[Dict],
                               gestures: List[str],
                               additional_context: Dict = None) -> str:
        """Build analysis prompt for Groq."""
        prompt = f"""
You are JARVIS, an intelligent desktop assistant. Analyze this scene and provide insights:

PEOPLE PRESENT:
{json.dumps(people, indent=2)}

DETECTED EMOTIONS:
{json.dumps(emotions, indent=2)}

DETECTED GESTURES:
{json.dumps(gestures, indent=2)}

ADDITIONAL CONTEXT:
{json.dumps(additional_context or {}, indent=2)}

Analyze this scene and respond with a JSON object containing:
{{
    "activity": "what the user appears to be doing",
    "energy_level": "high/medium/low",
    "mood": "overall mood assessment",
    "recommendation": "specific, helpful suggestion based on context",
    "urgency": "low/medium/high - how urgent any intervention is",
    "reasoning": "brief explanation of your analysis"
}}

Be specific and helpful. Consider:
- User's emotional state
- What they might be working on
- Potential needs or pain points
- Best type of assistance
"""
        return prompt
    
    async def _groq_analyze(self, prompt: str) -> Dict:
        """Use Groq to analyze scene."""
        try:
            response = self.client.messages.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                # Try to extract JSON
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    return json.loads(json_str)
            except:
                pass
            
            # Fallback parsing
            return {
                "activity": "analyzing",
                "energy_level": "medium",
                "recommendation": response_text[:100],
                "urgency": "low"
            }
        
        except Exception as e:
            print(f"❌ Groq analysis error: {e}")
            return {}
    
    def _simple_analyze(self,
                       people: List[Dict],
                       emotions: List[Dict],
                       gestures: List[str]) -> Dict:
        """Simple fallback analysis without Groq."""
        # Determine energy level
        energy_level = "medium"
        if emotions:
            sad_sad_count = sum(1 for e in emotions if e["emotion"] == "sad" and e["confidence"] > 0.6)
            if sad_sad_count > 0:
                energy_level = "low"
            elif any(e["emotion"] == "happy" and e["confidence"] > 0.7 for e in emotions):
                energy_level = "high"
        
        # Simple recommendation
        recommendation = "Keep up the great work!"
        if emotions:
            if any(e["emotion"] in ["sad", "angry"] and e["confidence"] > 0.6 for e in emotions):
                recommendation = "Take a break? I'm here to help."
        
        return {
            "activity": "working on something",
            "energy_level": energy_level,
            "recommendation": recommendation,
            "urgency": "low"
        }
    
    def _summarize_emotions(self, emotions: List[Dict]) -> Dict:
        """Summarize emotions."""
        if not emotions:
            return {}
        
        return {
            "dominant": max(emotions, key=lambda x: x["confidence"])["emotion"] if emotions else "neutral",
            "count": len(emotions),
            "summary": emotions
        }
    
    async def predict_next_action(self, context: SceneContext,
                                  history: List[SceneContext] = None) -> str:
        """
        Predict what user might need next.
        
        Args:
            context: Current scene context
            history: Previous contexts for pattern matching
            
        Returns:
            Predicted action/recommendation
        """
        if not self.client:
            return "I'm ready to help!"
        
        # Build history summary
        history_text = ""
        if history:
            for h in history[-5:]:  # Last 5
                history_text += f"- {h.activity} ({h.energy_level} energy)\n"
        
        prompt = f"""Based on this scene analysis and recent activity history, predict what the user might need next and provide a proactive suggestion.

Current Scene:
- Activity: {context.activity}
- Energy Level: {context.energy_level}
- People Present: {', '.join(context.people_present)}
- Emotions: {context.emotions.get('dominant', 'unknown')}

Recent Activity:
{history_text or "No recent history"}

Provide a short, specific, helpful suggestion (1-2 sentences) that JARVIS should offer proactively."""
        
        try:
            response = self.client.messages.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return context.recommendation


class ContextualResponder:
    """
    Generate contextual responses based on scene analysis.
    """
    
    def __init__(self, scene_analyzer: SceneAnalyzer):
        """Initialize responder."""
        self.analyzer = scene_analyzer
    
    async def generate_greeting(self, people: List[Dict]) -> str:
        """Generate personalized greeting."""
        if not people:
            return "No one detected."
        
        names = [p["name"] for p in people if p["name"] != "Unknown"]
        
        if not names:
            return "I detect someone new here. Welcome!"
        
        if len(names) == 1:
            return f"Hello {names[0]}! Good to see you. 👋"
        else:
            names_text = ", ".join(names[:-1]) + f" and {names[-1]}"
            return f"Hello {names_text}! Great to see you all. 👋"
    
    async def generate_emotion_response(self, emotions: List[Dict]) -> str:
        """Generate response based on emotions."""
        if not emotions:
            return "How are you feeling today?"
        
        dominant_emotion = max(emotions, key=lambda x: x["confidence"])
        return dominant_emotion.get("response", "I'm here to help!")
    
    async def generate_gesture_response(self, gesture: str) -> str:
        """Generate response to gesture."""
        responses = {
            "thumbs_up": "Great! I'm glad you're happy with that. 👍",
            "thumbs_down": "Got it, we can improve that. 👎",
            "open_palm": "I'm listening! What do you need?",
            "peace_sign": "Peace! Let's keep that positive energy. ✌️",
            "ok_sign": "Perfect! All good here. 👌",
            "pointing": "I see where you're pointing. What's there?",
            "wave": "Hey there! 👋 What's up?",
            "stop": "Understood! I'll stop what I'm doing."
        }
        
        return responses.get(gesture, "Interesting gesture! What does that mean?")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("🧠 Scene Analyzer Test\n")
        
        analyzer = SceneAnalyzer()
        
        # Test data
        people = [{"name": "Manan", "confidence": 0.95}]
        emotions = [{"emotion": "happy", "confidence": 0.8}]
        gestures = ["open_palm"]
        
        context = await analyzer.analyze_scene(people, emotions, gestures)
        
        print(f"Activity: {context.activity}")
        print(f"Energy: {context.energy_level}")
        print(f"Recommendation: {context.recommendation}")
    
    asyncio.run(test())
