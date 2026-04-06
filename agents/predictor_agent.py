"""
Predictor Agent - Predicts User Needs and Generates Proactive Suggestions

Key component of the proactive JARVIS system.
Uses Groq for intelligent prediction based on behavior patterns.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent, AgentMessage


class PredictorAgent(BaseAgent):
    """
    Predicts user needs based on:
    - Time of day patterns
    - App usage history
    - Recent commands
    - Current context
    
    Uses Groq for sophisticated reasoning about user behavior.
    """
    
    def __init__(self, agent_id: str = "predictor", brain=None):
        """Initialize predictor agent."""
        super().__init__(agent_id, "predictor", brain)
        
        self.prediction_history = []
        self.accuracy_score = 0.5
        self.max_predictions = 5  # Max suggestions to generate
        
        # Prediction confidence thresholds
        self.high_confidence_threshold = 0.8
        self.medium_confidence_threshold = 0.6
    
    def get_capabilities(self) -> List[str]:
        """Get predictor capabilities."""
        return [
            "predict_next_action",
            "suggest_proactive_task",
            "analyze_behavior_pattern",
            "forecast_user_need",
            "recommend_automation"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute prediction task.
        
        Args:
            task: Task dict with:
              - type: prediction task type
              - context: current context
              - behavior_data: user behavior history
              
        Returns:
            Predictions and suggestions
        """
        self.update_state("busy")
        start_time = __import__('time').time()
        
        try:
            task_type = task.get('type', 'predict_next_action')
            
            if task_type == 'predict_next_action':
                result = await self._predict_next_action(task)
            elif task_type == 'suggest_proactive_task':
                result = await self._suggest_proactive_task(task)
            elif task_type == 'forecast_need':
                result = await self._forecast_user_need(task)
            else:
                result = {'error': f'Unknown task type: {task_type}'}
            
            exec_time = __import__('time').time() - start_time
            self.record_success(exec_time)
            self.update_state("idle")
            
            return result
            
        except Exception as e:
            self.record_failure(str(e))
            self.update_state("error")
            return {'error': str(e)}
    
    async def _predict_next_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the next action user will likely take.
        
        Uses current context + behavior history.
        """
        behavior_data = task.get('behavior_data', {})
        context = task.get('context', {})
        
        # Extract relevant information
        current_app = context.get('current_app', 'unknown')
        current_hour = datetime.now().hour
        recent_actions = behavior_data.get('recent_actions', [])
        app_patterns = behavior_data.get('app_patterns', {})
        
        # Build prediction prompt
        prompt = f"""Based on this user behavior data, predict the next 3 actions they're likely to take:

Current Context:
- Active app: {current_app}
- Time: {current_hour}:00
- Recent actions: {', '.join(recent_actions[-5:]) if recent_actions else 'none'}

App Usage Patterns:
{self._format_patterns(app_patterns)}

Provide exactly 3 predictions in this JSON format:
{{
    "predictions": [
        {{"action": "action name", "confidence": 0.95, "reasoning": "why"}},
        {{"action": "action name", "confidence": 0.75, "reasoning": "why"}},
        {{"action": "action name", "confidence": 0.60, "reasoning": "why"}}
    ]
}}

Only return the JSON, no other text."""
        
        # Get predictions from Groq
        if self.brain:
            response = await asyncio.to_thread(self.brain.ask_groq, prompt, 0.7)
            
            try:
                import json
                predictions = json.loads(response)
                
                # Store in history
                self.prediction_history.append({
                    'timestamp': datetime.now(),
                    'predictions': predictions['predictions']
                })
                
                return {
                    'type': 'predictions',
                    'predictions': predictions['predictions'],
                    'context': context
                }
                
            except json.JSONDecodeError:
                return {'error': 'Could not parse predictions', 'raw': response}
        else:
            # Fallback heuristic prediction
            return self._heuristic_predict(recent_actions, app_patterns, current_app)
    
    async def _suggest_proactive_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest a proactive task for the user.
        
        Example: "You usually open VS Code at this time. Should I open it?"
        """
        behavior_data = task.get('behavior_data', {})
        context = task.get('context', {})
        
        current_hour = datetime.now().hour
        day_of_week = datetime.now().strftime('%A')
        current_app = context.get('current_app', 'unknown')
        most_used_apps = behavior_data.get('most_used_apps', [])
        
        # Build prompt
        prompt = f"""Given this user's behavior pattern, suggest ONE proactive task to help them:

Time: {day_of_week} at {current_hour}:00
Current app: {current_app}
Most frequently used apps: {', '.join(most_used_apps[:3]) if most_used_apps else 'unknown'}

Suggest a helpful, proactive action they might appreciate now.
You MUST respond with ONLY this JSON (no other text):
{{
    "suggestion": "specific action to take",
    "reasoning": "why this helps",
    "confidence": 0.85,
    "risk_level": "low",
    "estimated_benefit": "what will improve"
}}"""
        
        if self.brain:
            response = await asyncio.to_thread(self.brain.ask_groq, prompt, 0.6)
            
            try:
                import json
                suggestion = json.loads(response)
                return {
                    'type': 'proactive_suggestion',
                    'suggestion': suggestion
                }
            except json.JSONDecodeError:
                return {'error': 'Could not parse suggestion'}
        else:
            # Fallback
            if most_used_apps and most_used_apps[0] not in current_app:
                return {
                    'type': 'proactive_suggestion',
                    'suggestion': {
                        'suggestion': f"Open {most_used_apps[0]}",
                        'reasoning': "You often use this at this time",
                        'confidence': 0.7,
                        'risk_level': 'low'
                    }
                }
            return {'type': 'no_suggestion'}
    
    async def _forecast_user_need(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast what the user will need in the future.
        
        Example: "You'll likely need code review later"
        """
        behavior_data = task.get('behavior_data', {})
        
        # Analyze patterns
        recent_actions = behavior_data.get('recent_actions', [])
        hourly_patterns = behavior_data.get('hourly_patterns', {})
        
        prompt = f"""Analyze this work session and forecast what resources/tools the user will likely need in the next 1-2 hours:

Recent actions: {', '.join(recent_actions[-10:]) if recent_actions else 'unknown'}
Time-based patterns: {str(hourly_patterns)[:200]}

Provide a JSON forecast:
{{
    "likely_needs": ["resource1", "resource2"],
    "preparation_suggestions": ["what to prepare now"],
    "priority": "high/medium/low",
    "reasoning": "brief explanation"
}}"""
        
        if self.brain:
            response = await asyncio.to_thread(self.brain.ask_groq, prompt, 0.5)
            
            try:
                import json
                forecast = json.loads(response)
                return {
                    'type': 'forecast',
                    'forecast': forecast
                }
            except json.JSONDecodeError:
                return {'error': 'Could not parse forecast'}
        
        return {'type': 'no_forecast'}
    
    def _format_patterns(self, patterns: Dict) -> str:
        """Format app patterns for readability."""
        if not patterns:
            return "No patterns available"
        
        lines = []
        for app, data in list(patterns.items())[:5]:
            usage = data.get('usage_count', 0)
            lines.append(f"  - {app}: used {usage} times")
        
        return '\n'.join(lines)
    
    def _heuristic_predict(self, recent_actions: List[str], 
                          patterns: Dict, current_app: str) -> Dict[str, Any]:
        """Fallback heuristic prediction without Groq."""
        predictions = []
        
        # If using coding app, likely to search/debug next
        if 'vs code' in current_app.lower() or 'python' in current_app.lower():
            predictions = [
                {"action": "search_documentation", "confidence": 0.75},
                {"action": "run_debug", "confidence": 0.65},
                {"action": "commit_code", "confidence": 0.55}
            ]
        
        # If in browser, likely to take notes
        elif 'chrome' in current_app.lower() or 'firefox' in current_app.lower():
            predictions = [
                {"action": "create_note", "confidence": 0.70},
                {"action": "extract_text", "confidence": 0.60},
                {"action": "save_url", "confidence": 0.50}
            ]
        
        # Default predictions
        else:
            predictions = [
                {"action": "take_break", "confidence": 0.60},
                {"action": "check_messages", "confidence": 0.55},
                {"action": "open_email", "confidence": 0.50}
            ]
        
        return {
            'type': 'predictions',
            'predictions': predictions,
            'method': 'heuristic'
        }
    
    def evaluate_prediction(self, prediction: str, actual_action: str) -> float:
        """
        Evaluate if prediction was accurate.
        Updates confidence scores.
        
        Returns:
            Accuracy score
        """
        is_correct = prediction.lower() in actual_action.lower()
        
        # Update accuracy
        total = len(self.prediction_history) + 1
        old_acc = self.accuracy_score
        self.accuracy_score = (old_acc * (total - 1) + int(is_correct)) / total
        
        return self.accuracy_score
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics."""
        total_predictions = len(self.prediction_history)
        
        return {
            'total_predictions': total_predictions,
            'accuracy_score': self.accuracy_score,
            'confidence_threshold_high': self.high_confidence_threshold,
            'confidence_threshold_medium': self.medium_confidence_threshold,
            'agent_status': self.get_status()
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    print("🔮 Predictor Agent Test")
    
    agent = PredictorAgent()
    
    # Test prediction
    test_task = {
        'type': 'predict_next_action',
        'context': {
            'current_app': 'VS Code',
            'current_hour': 10
        },
        'behavior_data': {
            'recent_actions': ['open_file', 'browse_code', 'run_debug'],
            'app_patterns': {
                'VS Code': {'usage_count': 50},
                'Chrome': {'usage_count': 40}
            }
        }
    }
    
    print("\n🧠 Prediction Test:")
    print("  (Running async task...)")
    # Async execution would go here in actual usage
    
    print("\n📊 Agent Status:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n📈 Prediction Stats:")
    stats = agent.get_prediction_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
