"""
Vision Analyzer Module for JARVIS

Analyzes screen content using Groq AI to provide intelligent suggestions.
Understands context and provides proactive assistance.
"""

import json
import time
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading


@dataclass
class ScreenAnalysis:
    """Result of screen analysis."""
    activity: str
    context: str
    suggestions: List[str]
    timestamp: float
    confidence: float
    relevant_tools: List[str]


class VisionAnalyzer:
    """
    Analyzes screen content and provides context-aware assistance.
    
    Features:
    - Understand what user is doing
    - Detect application context (VS Code, Browser, etc.)
    - Provide intelligent suggestions
    - Track activity history
    - Suggest relevant tools
    """
    
    def __init__(self, brain=None):
        """
        Initialize vision analyzer.
        
        Args:
            brain: Optional Brain instance for Groq API calls
        """
        self.brain = brain
        self.activity_history = []
        self.confidence_threshold = 0.6
        self.max_history = 50
        
        # Known contexts
        self.app_contexts = {
            'vs code': 'Code Editor',
            'visual studio': 'IDE',
            'python': 'Programming',
            'javascript': 'Web Development',
            'google chrome': 'Web Browsing',
            'firefox': 'Web Browsing',
            'terminal': 'Command Line',
            'powershell': 'Command Line',
            'youtube': 'Video Watching',
            'notion': 'Note Taking',
            'slack': 'Communication',
            'discord': 'Communication',
        }
        
        self.action_patterns = {
            'debugging': ['debug', 'error', 'exception', 'traceback', 'breakpoint'],
            'writing': ['editor', 'document', 'text', 'markdown', 'note'],
            'reading': ['article', 'blog', 'documentation', 'readme', 'wiki'],
            'research': ['search', 'google', 'wiki', 'stackoverflow'],
            'coding': ['code', 'python', 'javascript', 'terminal', 'compiler'],
            'communication': ['slack', 'discord', 'email', 'message'],
            'video': ['youtube', 'video', 'streaming', 'player'],
        }
        
        self.suggestion_templates = {
            'code_editor': [
                "Need help debugging this code?",
                "Want me to explain this function?",
                "Should I search for similar code patterns?",
                "Want to refactor this?",
            ],
            'browser': [
                "Summarize this page?",
                "Extract key points?",
                "Save this as a note?",
            ],
            'terminal': [
                "Explain this command?",
                "Need help with the error?",
                "Want to search for a solution?",
            ],
            'video': [
                "Transcribe this video?",
                "Get video summary?",
                "Extract key moments?",
            ],
            'general': [
                "How can I help?",
                "Need any assistance?",
                "Want me to summarize this?",
            ]
        }
    
    def analyze(self, screenshot_text: str, screenshot_name: str = "") -> ScreenAnalysis:
        """
        Analyze screen content and provide suggestions.
        
        Args:
            screenshot_text: OCR-extracted text from screenshot
            screenshot_name: Optional name/title of current window
            
        Returns:
            ScreenAnalysis with insights and suggestions
        """
        try:
            # Detect context from text
            activity = self._detect_activity(screenshot_text, screenshot_name)
            context = self._extract_context(screenshot_text)
            relevant_tools = self._identify_tools(activity)
            
            # Get AI suggestion if brain is available
            if self.brain:
                suggestions = self._get_ai_suggestions(
                    activity, 
                    context, 
                    screenshot_text[:500]  # Limit to first 500 chars for API
                )
            else:
                suggestions = self._get_template_suggestions(activity)
            
            # Create analysis result
            analysis = ScreenAnalysis(
                activity=activity,
                context=context,
                suggestions=suggestions,
                timestamp=time.time(),
                confidence=self._calculate_confidence(screenshot_text),
                relevant_tools=relevant_tools
            )
            
            # Store in history
            self._record_activity(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def _detect_activity(self, text: str, window_name: str = "") -> str:
        """
        Detect what user is doing based on screen content.
        
        Args:
            text: OCR-extracted text
            window_name: Active window name
            
        Returns:
            Activity description
        """
        text_lower = text.lower()
        window_lower = window_name.lower()
        
        # Check for known patterns
        for action, keywords in self.action_patterns.items():
            if any(keyword in text_lower or keyword in window_lower for keyword in keywords):
                return action
        
        # Check window name against known apps
        for app, app_type in self.app_contexts.items():
            if app in window_lower:
                return app_type.lower()
        
        # Default activity based on text length
        if len(text) > 500:
            return "reading"
        elif len(text) > 100:
            return "working"
        else:
            return "general browsing"
    
    def _extract_context(self, text: str) -> str:
        """
        Extract meaningful context from screen content.
        
        Args:
            text: OCR-extracted text
            
        Returns:
            Context summary
        """
        lines = text.split('\n')
        
        # Get first few meaningful lines
        context_lines = []
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                context_lines.append(line.strip())
            if len(context_lines) >= 3:
                break
        
        context = ' '.join(context_lines[:3])
        
        # Truncate if too long
        if len(context) > 200:
            context = context[:197] + "..."
        
        return context
    
    def _identify_tools(self, activity: str) -> List[str]:
        """
        Identify relevant tools for current activity.
        
        Args:
            activity: Current activity type
            
        Returns:
            List of relevant tool names
        """
        tool_mapping = {
            'coding': ['summarize_text', 'search_web', 'create_note'],
            'debugging': ['search_web', 'create_note', 'open_app'],
            'writing': ['create_note', 'summarize_text', 'copy_to_clipboard'],
            'research': ['search_web', 'get_news', 'create_note', 'summarize_text'],
            'reading': ['summarize_text', 'create_note', 'copy_to_clipboard'],
            'communication': ['create_note', 'copy_to_clipboard'],
            'video': ['summarize_text', 'create_note'],
            'programming': ['search_web', 'create_note', 'summarize_text'],
            'web development': ['search_web', 'create_note'],
            'web browsing': ['summarize_text', 'create_note', 'search_web'],
            'command line': ['search_web', 'open_app'],
        }
        
        return tool_mapping.get(activity, ['search_web', 'create_note'])
    
    def _get_template_suggestions(self, activity: str) -> List[str]:
        """
        Get suggestions from templates based on activity.
        
        Args:
            activity: Current activity type
            
        Returns:
            List of suggestion strings
        """
        # Map activity to template
        template_map = {
            'coding': 'code_editor',
            'debugging': 'code_editor',
            'programming': 'code_editor',
            'writing': 'code_editor',
            'reading': 'browser',
            'research': 'browser',
            'web browsing': 'browser',
            'video': 'video',
            'communication': 'general',
            'command line': 'terminal',
        }
        
        template = template_map.get(activity, 'general')
        suggestions = self.suggestion_templates.get(template, self.suggestion_templates['general'])
        
        return suggestions[:3]  # Return top 3
    
    def _get_ai_suggestions(self, activity: str, context: str, text: str) -> List[str]:
        """
        Get AI-powered suggestions using Groq.
        
        Args:
            activity: Current activity
            context: Screen context
            text: OCR text
            
        Returns:
            List of AI suggestions
        """
        try:
            prompt = f"""Analyze this screen activity and provide 2-3 concise, actionable suggestions for how JARVIS can help.

Activity: {activity}
Context: {context}
Screen Content: {text}

Respond with only a JSON array of suggestions:
["suggestion 1", "suggestion 2", "suggestion 3"]

Keep suggestions short, specific, and actionable."""
            
            # Use brain for API call
            response = self.brain.ask_groq(prompt, temperature=0.7)
            
            # Parse JSON response
            try:
                suggestions = json.loads(response)
                return suggestions[:3] if isinstance(suggestions, list) else []
            except json.JSONDecodeError:
                print("⚠️  Could not parse AI suggestions")
                return self._get_template_suggestions(activity)
            
        except Exception as e:
            print(f"⚠️  AI suggestion error: {e}")
            return self._get_template_suggestions(activity)
    
    def _calculate_confidence(self, text: str) -> float:
        """
        Calculate confidence in activity detection.
        
        Args:
            text: OCR text
            
        Returns:
            Confidence score 0.0-1.0
        """
        factors = 0.0
        
        # More text = more confident
        factors += min(len(text) / 1000, 0.3)
        
        # Presence of keywords
        keywords = sum(1 for action_keywords in self.action_patterns.values() 
                      for keyword in action_keywords if keyword in text.lower())
        factors += min(keywords / 10, 0.3)
        
        # Window name helps
        factors += 0.2  # Baseline
        
        return min(factors, 1.0)
    
    def _record_activity(self, analysis: ScreenAnalysis):
        """
        Record activity in history.
        
        Args:
            analysis: ScreenAnalysis result
        """
        self.activity_history.append({
            'activity': analysis.activity,
            'context': analysis.context,
            'timestamp': analysis.timestamp,
            'datetime': datetime.fromtimestamp(analysis.timestamp).isoformat()
        })
        
        # Keep history size manageable
        if len(self.activity_history) > self.max_history:
            self.activity_history = self.activity_history[-self.max_history:]
    
    def get_activity_summary(self) -> Dict:
        """
        Get summary of recent activities.
        
        Returns:
            Dictionary with activity statistics
        """
        if not self.activity_history:
            return {'total_activities': 0}
        
        # Count activities
        activity_counts = {}
        for record in self.activity_history:
            activity = record['activity']
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        # Most recent activity
        recent = self.activity_history[-1]
        
        # Time spent
        if len(self.activity_history) > 1:
            time_spent = self.activity_history[-1]['timestamp'] - self.activity_history[0]['timestamp']
        else:
            time_spent = 0
        
        return {
            'total_activities': len(self.activity_history),
            'activity_types': activity_counts,
            'most_recent': recent['activity'],
            'time_period_seconds': time_spent,
            'recent_activities': self.activity_history[-5:]  # Last 5
        }
    
    def get_activity_pattern(self) -> Optional[str]:
        """
        Identify pattern in user's recent activities.
        
        Returns:
            Description of activity pattern or None
        """
        if len(self.activity_history) < 3:
            return None
        
        # Get last 10 activities
        recent = self.activity_history[-10:]
        activities = [r['activity'] for r in recent]
        
        # Simple pattern detection
        if all(a == activities[0] for a in activities):
            return f"Sustained {activities[0]}"
        
        if activities.count('research') > 3 and activities.count('writing') > 2:
            return "Research and documentation workflow"
        
        if activities.count('coding') + activities.count('debugging') > 5:
            return "Development session"
        
        return "Mixed activities"
    
    def clear_history(self):
        """Clear activity history."""
        self.activity_history.clear()
        print("🗑️  Activity history cleared")
    
    def get_next_suggestion(self, current_activity: str) -> Optional[str]:
        """
        Predict and suggest next action based on pattern.
        
        Args:
            current_activity: Current activity type
            
        Returns:
            Suggested next action
        """
        pattern = self.get_activity_pattern()
        
        # Heuristic suggestions
        suggestions = {
            'research': 'Would you like to save your findings?',
            'coding': 'Need help debugging or testing?',
            'writing': 'Ready to share or publish?',
            'reading': 'Want to summarize what you found?',
            'debugging': 'Should I search for similar issues?',
        }
        
        return suggestions.get(current_activity, None)


# Global instance
_vision_analyzer = None


def get_vision_analyzer(brain=None) -> VisionAnalyzer:
    """Get or create global vision analyzer instance."""
    global _vision_analyzer
    if _vision_analyzer is None:
        _vision_analyzer = VisionAnalyzer(brain)
    return _vision_analyzer


# Example usage
if __name__ == "__main__":
    print("🧠 Vision Analyzer Test")
    
    # Test analysis
    sample_text = """
    def calculate_fibonacci(n):
        if n <= 1:
            return n
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
    
    # TODO: Optimize with memoization
    # WARNING: Stack overflow for large n values
    """
    
    analyzer = VisionAnalyzer()
    analysis = analyzer.analyze(sample_text, "VS Code - main.py")
    
    if analysis:
        print(f"\n📊 Analysis Results:")
        print(f"   Activity: {analysis.activity}")
        print(f"   Context: {analysis.context}")
        print(f"   Confidence: {analysis.confidence:.2f}")
        print(f"   Suggestions: {analysis.suggestions}")
        print(f"   Relevant tools: {analysis.relevant_tools}")
        
        print(f"\n📈 Activity Summary:")
        summary = analyzer.get_activity_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
