"""
Orchestrator Agent - Coordinates all specialized agents

Master coordinator that manages inter-agent communication and workflow.
Implements the autonomous loop and proactive behavior orchestration.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent, AgentMessage
from agents.predictor_agent import PredictorAgent
from agents.executor_agent import ExecutorAgent
from agents.scheduler_agent import SchedulerAgent
from agents.memory_agent import MemoryAgent


class Orchestrator(BaseAgent):
    """
    Master orchestrator for proactive JARVIS system.
    
    Coordinates:
    - Prediction engine for user need forecasting
    - Execution layer with risk management
    - Scheduling system for autonomous tasks
    - Memory system for long-term learning
    """
    
    def __init__(self, agent_id: str = "orchestrator", brain=None):
        """Initialize orchestrator."""
        super().__init__(agent_id, "orchestrator", brain)
        
        # Initialize specialized agents
        self.predictor = PredictorAgent("predictor", brain)
        self.executor = ExecutorAgent("executor", brain)
        self.scheduler = SchedulerAgent("scheduler", brain)
        self.memory = MemoryAgent("memory", brain)
        
        # Orchestration state
        self.active_workflows = {}
        self.workflow_history = []
        self.performance_metrics = {}
        
        # Configuration
        self.autonomy_level = "medium"  # low, medium, high
        self.proactivity_enabled = True
        self.background_loop_interval = 30  # seconds
        
        # Set executor callback for scheduler
        self.scheduler.set_executor_callback(self._execute_via_executor)
    
    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities."""
        return [
            "run_autonomous_loop",
            "predict_and_execute",
            "proactive_task_suggestion",
            "coordinate_agents",
            "monitor_performance",
            "adapt_strategy"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration task.
        
        Args:
            task: Task dict with:
              - type: orchestration type
              - context: current context
              - behavior_data: user behavior
        """
        self.update_state("busy")
        
        try:
            task_type = task.get('type', 'autonomous_loop')
            
            if task_type == 'autonomous_loop':
                result = await self._run_autonomous_loop(task)
            elif task_type == 'predict_and_execute':
                result = await self._predict_and_execute(task)
            elif task_type == 'proactive_suggestion':
                result = await self._generate_suggestions(task)
            else:
                result = {'error': f'Unknown task type: {task_type}'}
            
            self.update_state("idle")
            return result
            
        except Exception as e:
            self.record_failure(str(e))
            self.update_state("error")
            return {'error': str(e)}
    
    async def _run_autonomous_loop(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main autonomous operation loop.
        
        Runs background monitoring and proactive task execution.
        """
        loop_duration = task.get('duration_seconds', 300)  # 5 minutes default
        iterations = 0
        start_time = __import__('time').time()
        
        results = []
        
        try:
            while (__import__('time').time() - start_time) < loop_duration:
                iterations += 1
                
                # Phase 1: Get context and predictions
                context = await self._gather_context()
                predictions = await self._get_predictions(context)
                
                # Phase 2: Check scheduler for pending tasks
                pending = self.scheduler.get_pending_tasks(
                    within_seconds=self.background_loop_interval
                )
                
                # Phase 3: Execute scheduled tasks
                for pending_task in pending:
                    exec_result = await self._execute_via_executor(
                        pending_task['task']
                    )
                    results.append(exec_result)
                
                # Phase 4: Generate and execute proactive suggestions
                if self.proactivity_enabled:
                    suggestions = await self._generate_suggestions({
                        'context': context,
                        'predictions': predictions
                    })
                    
                    for suggestion in suggestions.get('suggestions', []):
                        if self._should_execute_suggestion(suggestion):
                            exec_result = await self._execute_via_executor(
                                suggestion
                            )
                            results.append(exec_result)
                
                # Phase 5: Learn from execution
                await self._learn_from_execution(results[-5:] if results else [])
                
                # Wait before next iteration
                await asyncio.sleep(self.background_loop_interval)
            
            return {
                'status': 'completed',
                'iterations': iterations,
                'tasks_executed': len(results),
                'results_summary': self._summarize_results(results),
                'performance': self._calculate_performance_metrics(results)
            }
            
        except asyncio.CancelledError:
            return {
                'status': 'cancelled',
                'iterations_completed': iterations,
                'results': len(results)
            }
    
    async def _predict_and_execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user needs and execute proactive tasks."""
        context = await self._gather_context()
        behavior_data = task.get('behavior_data', {})
        
        # Get predictions
        prediction_task = {
            'type': 'predict_next_action',
            'context': context,
            'behavior_data': behavior_data
        }
        
        predictions = await self.predictor.execute(prediction_task)
        
        # Generate execution plan based on predictions
        execution_plan = self._create_execution_plan(predictions, context)
        
        # Execute high-confidence predictions
        results = []
        for action in execution_plan.get('actions', []):
            if action['confidence'] > 0.75:
                exec_result = await self._execute_via_executor(action)
                results.append(exec_result)
        
        return {
            'status': 'success',
            'predictions': predictions,
            'execution_plan': execution_plan,
            'executed': len(results),
            'results': results
        }
    
    async def _generate_suggestions(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proactive task suggestions."""
        context = task.get('context', {})
        predictions = task.get('predictions', {})
        
        # Get suggestions from predictor
        suggestion_task = {
            'type': 'suggest_proactive_task',
            'context': context,
            'behavior_data': context.get('behavior_data', {})
        }
        
        suggestion_result = await self.predictor.execute(suggestion_task)
        
        # Convert suggestion to executable task
        suggestions = []
        if suggestion_result.get('type') == 'proactive_suggestion':
            sugg = suggestion_result.get('suggestion', {})
            
            suggestions.append({
                'name': sugg.get('suggestion', 'unknown'),
                'action': 'proactive_action',
                'target': sugg.get('suggestion', ''),
                'confidence': sugg.get('confidence', 0.5),
                'risk_level': sugg.get('risk_level', 'low'),
                'parameters': {}
            })
        
        return {
            'suggestions': suggestions,
            'context': context
        }
    
    async def _gather_context(self) -> Dict[str, Any]:
        """Gather current system and user context."""
        # In real implementation, this would:
        # - Check current app
        # - Get user location/availability
        # - Check network status
        # - Get time/calendar info
        
        current_hour = datetime.now().hour
        
        return {
            'current_hour': current_hour,
            'timestamp': datetime.now().isoformat(),
            'user_available': True,  # Would check actual status
            'network_available': True
        }
    
    async def _get_predictions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get behavior predictions."""
        prediction_task = {
            'type': 'predict_next_action',
            'context': context,
            'behavior_data': {
                'recent_actions': [],
                'app_patterns': {}
            }
        }
        
        return await self.predictor.execute(prediction_task)
    
    def _should_execute_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """Determine if suggestion should be auto-executed."""
        risk_level = suggestion.get('risk_level', 'medium')
        confidence = suggestion.get('confidence', 0.5)
        
        # Auto-execute low-risk, high-confidence suggestions
        if risk_level == "low" and confidence > 0.7:
            return True
        
        # For medium autonomy, be more selective
        if self.autonomy_level == "medium":
            return risk_level == "low" and confidence > 0.85
        
        # For low autonomy, never auto-execute
        if self.autonomy_level == "low":
            return False
        
        return False
    
    async def _execute_via_executor(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task through executor agent."""
        return await self.executor.execute(task)
    
    async def _learn_from_execution(self, recent_results: List[Dict[str, Any]]):
        """Learn from execution results."""
        for result in recent_results:
            if result.get('status') == 'success':
                # Store as learned pattern
                task_name = result.get('task_name', 'unknown')
                
                self.memory.store_knowledge(
                    f"successful_task_{task_name}",
                    True,
                    category='learned_tasks',
                    confidence=0.8
                )
    
    def _create_execution_plan(self, predictions: Dict[str, Any],
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan from predictions."""
        actions = []
        
        if predictions.get('type') == 'predictions':
            for pred in predictions.get('predictions', []):
                action = {
                    'name': pred.get('action', 'unknown'),
                    'action': pred.get('action', '').lower(),
                    'confidence': pred.get('confidence', 0.5),
                    'risk_level': 'low',
                    'parameters': {}
                }
                actions.append(action)
        
        return {
            'actions': actions,
            'context': context
        }
    
    def _should_execute_suggestion_old(self, suggestion: Dict[str, Any]) -> bool:
        """Determine if suggestion should be executed."""
        confidence = suggestion.get('confidence', 0.5)
        risk = suggestion.get('risk_level', 'medium')
        
        return confidence > 0.8 or (risk == 'low' and confidence > 0.7)
    
    def _summarize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize execution results."""
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        
        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(results) if results else 0
        }
    
    def _calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        exec_times = [
            r.get('execution_time', 0) for r in results
            if r.get('status') == 'success'
        ]
        
        avg_time = sum(exec_times) / len(exec_times) if exec_times else 0
        
        return {
            'average_execution_time': avg_time,
            'total_tasks': len(results),
            'total_time': sum(exec_times)
        }
    
    def set_autonomy_level(self, level: str):
        """Set autonomy level ('low', 'medium', 'high')."""
        if level in ['low', 'medium', 'high']:
            self.autonomy_level = level
            self._log_event(f"Autonomy level set to {level}")
    
    def set_proactivity(self, enabled: bool):
        """Enable/disable proactive behavior."""
        self.proactivity_enabled = enabled
        self._log_event(f"Proactivity {'enabled' if enabled else 'disabled'}")
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            'status': self.get_status(),
            'autonomy_level': self.autonomy_level,
            'proactivity_enabled': self.proactivity_enabled,
            'background_interval': self.background_loop_interval,
            'agents': {
                'predictor': self.predictor.get_status(),
                'executor': self.executor.get_status(),
                'scheduler': self.scheduler.get_status(),
                'memory': self.memory.get_status()
            },
            'metrics': self.performance_metrics
        }
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics from all agents."""
        return {
            'predictor_stats': self.predictor.get_prediction_stats(),
            'executor_stats': self.executor.get_execution_stats(),
            'scheduler_stats': self.scheduler.get_scheduler_stats(),
            'memory_stats': self.memory.get_memory_stats()
        }
    
    def _log_event(self, message: str, level: str = "info"):
        """Log orchestrator event."""
        msg = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="logger",
            message_type=f"log_{level}",
            content={'message': message, 'timestamp': datetime.now()}
        )
        self.shared_memory.broadcast_message(msg)


# Example usage
if __name__ == "__main__":
    print("🎼 Orchestrator Agent Test\n")
    
    orchestrator = Orchestrator()
    
    print("📋 Orchestrator Capabilities:")
    for cap in orchestrator.get_capabilities():
        print(f"  ✓ {cap}")
    
    print("\n⚙️ Configuration:")
    print(f"  Autonomy Level: {orchestrator.autonomy_level}")
    print(f"  Proactivity: {'Enabled' if orchestrator.proactivity_enabled else 'Disabled'}")
    print(f"  Loop Interval: {orchestrator.background_loop_interval}s")
    
    print("\n🤖 Coordinated Agents:")
    status = orchestrator.get_orchestrator_status()
    for agent_name, agent_status in status['agents'].items():
        print(f"  {agent_name}: {agent_status.get('status', 'unknown')}")
    
    print("\n✨ Ready for autonomous operation!")
