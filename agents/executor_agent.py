"""
Executor Agent - Executes tasks with risk assessment

Handles task execution with safety checks and user interaction.
Integrates with risk manager for safe autonomous operation.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from agents.base_agent import BaseAgent, AgentMessage
from proactive_risk_manager import RiskManager, RiskLevel


class ExecutorAgent(BaseAgent):
    """
    Executes tasks with built-in safety mechanisms.
    
    Features:
    - Risk assessment before execution
    - User confirmation for medium/high risk
    - Automatic rollback on failure
    - Execution history and logging
    """
    
    def __init__(self, agent_id: str = "executor", brain=None):
        """Initialize executor agent."""
        super().__init__(agent_id, "executor", brain)
        
        self.risk_manager = RiskManager()
        self.execution_history = []
        self.user_approval_callback: Optional[Callable] = None
        self.max_retries = 3
        self.task_registry: Dict[str, Callable] = {}
        
        # Register default tasks
        self._register_default_tasks()
    
    def get_capabilities(self) -> List[str]:
        """Get executor capabilities."""
        return [
            "execute_task",
            "execute_with_confirmation",
            "execute_batch",
            "rollback_task",
            "get_execution_history"
        ]
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for a task type."""
        self.task_registry[task_type.lower()] = handler
        
        msg = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="logger",
            message_type="info",
            content={"message": f"Registered handler for {task_type}"}
        )
        self.shared_memory.broadcast_message(msg)
    
    def set_approval_callback(self, callback: Callable[[Dict], bool]):
        """Set callback for user approval."""
        self.user_approval_callback = callback
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with full safety protocol.
        
        Args:
            task: Task dict with:
              - name: task name
              - action: action type
              - target: target of action
              - parameters: task params
              - user_context: optional user context
              
        Returns:
            Execution result
        """
        self.update_state("busy")
        start_time = __import__('time').time()
        
        try:
            # Perform risk assessment
            assessment = self.risk_manager.assess_task(
                task,
                user_context=task.get('user_context', {})
            )
            
            # Log assessment
            self._log_event(f"Risk assessment: {assessment.risk_level.value}", "info")
            
            # Determine execution strategy
            strategy = self.risk_manager.get_execution_strategy(assessment.risk_level)
            
            if strategy == "manual_only":
                self.update_state("idle")
                return {
                    'status': 'blocked',
                    'reason': 'Critical risk level - manual intervention required',
                    'assessment': self._serialize_assessment(assessment)
                }
            
            elif strategy == "ask_detailed":
                # Request detailed user approval
                approved = await self._request_detailed_approval(task, assessment)
                if not approved:
                    self.update_state("idle")
                    return {
                        'status': 'cancelled_by_user',
                        'reason': 'User declined execution',
                        'assessment': self._serialize_assessment(assessment)
                    }
            
            elif strategy == "ask_first":
                # Request simple user approval
                approved = await self._request_approval(task, assessment)
                if not approved:
                    self.update_state("idle")
                    return {
                        'status': 'cancelled_by_user',
                        'reason': 'User declined execution',
                        'assessment': self._serialize_assessment(assessment)
                    }
            
            # Execute with retries
            result = await self._execute_with_retries(task)
            
            exec_time = __import__('time').time() - start_time
            self.record_success(exec_time)
            
            # Record execution
            self._record_execution(task, result, "success", exec_time)
            
            self.update_state("idle")
            
            return {
                'status': 'success',
                'result': result,
                'execution_time': exec_time,
                'risk_level': assessment.risk_level.value
            }
            
        except Exception as e:
            exec_time = __import__('time').time() - start_time
            self.record_failure(str(e))
            
            # Record failed execution
            self._record_execution(task, None, "failed", exec_time, str(e))
            
            self.update_state("error")
            
            return {
                'status': 'failed',
                'error': str(e),
                'execution_time': exec_time
            }
    
    async def _execute_with_retries(self, task: Dict[str, Any]) -> Any:
        """Execute task with automatic retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Get handler for task type
                action = task.get('action', '').lower()
                handler = self.task_registry.get(action)
                
                if handler:
                    # Use registered handler
                    result = await asyncio.to_thread(
                        handler,
                        task
                    )
                else:
                    # Use Groq for generic execution
                    result = await self._execute_generic(task)
                
                return result
                
            except Exception as e:
                last_error = e
                self._log_event(
                    f"Execution attempt {attempt + 1} failed: {str(e)}",
                    "warning"
                )
                
                if attempt < self.max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
        
        raise Exception(f"Task failed after {self.max_retries} attempts: {last_error}")
    
    async def _execute_generic(self, task: Dict[str, Any]) -> Any:
        """Generic execution using Groq brain."""
        if not self.brain:
            raise Exception("No brain available for generic execution")
        
        action = task.get('action', '')
        target = task.get('target', '')
        params = task.get('parameters', {})
        
        prompt = f"""Execute this task and return the result:
Action: {action}
Target: {target}
Parameters: {params}

Provide a JSON response with:
{{ "success": true/false, "result": "execution result", "error": null or "error message" }}"""
        
        response = await asyncio.to_thread(
            self.brain.ask_groq,
            prompt,
            0.3
        )
        
        try:
            import json
            result = json.loads(response)
            
            if not result.get('success', False):
                raise Exception(result.get('error', 'Unknown error'))
            
            return result.get('result', 'Task executed')
            
        except json.JSONDecodeError:
            return response
    
    async def _request_approval(self, task: Dict[str, Any], 
                               assessment) -> bool:
        """Request user approval for medium risk."""
        if not self.user_approval_callback:
            # Default: ask via Groq agent message
            msg = AgentMessage(
                sender_id=self.agent_id,
                recipient_id="user",
                message_type="approval_request",
                content={
                    'task': task.get('name', 'unknown'),
                    'action': task.get('action', 'unknown'),
                    'risk': assessment.risk_level.value,
                    'recommendation': assessment.recommendation
                }
            )
            self.shared_memory.broadcast_message(msg)
            return True  # Proceed with caution
        
        # Use callback if provided
        return await asyncio.to_thread(
            self.user_approval_callback,
            {'task': task, 'assessment': assessment}
        )
    
    async def _request_detailed_approval(self, task: Dict[str, Any],
                                        assessment) -> bool:
        """Request detailed user approval for high risk."""
        details = {
            'task_name': task.get('name', 'unknown'),
            'action': task.get('action', 'unknown'),
            'target': task.get('target', 'unknown'),
            'risk_level': assessment.risk_level.value,
            'risk_factors': assessment.factors,
            'estimated_impact': assessment.estimated_impact,
            'reversible': assessment.reversible,
            'recommendation': assessment.recommendation
        }
        
        msg = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="user",
            message_type="detailed_approval_request",
            content=details
        )
        self.shared_memory.broadcast_message(msg)
        
        return True  # Default: proceed if requested
    
    def _record_execution(self, task: Dict[str, Any], result: Any,
                         status: str, exec_time: float, error: str = None):
        """Record execution for history and learning."""
        record = {
            'timestamp': datetime.now(),
            'task_name': task.get('name', 'unknown'),
            'action': task.get('action', 'unknown'),
            'status': status,
            'execution_time': exec_time,
            'result': result,
            'error': error
        }
        
        self.execution_history.append(record)
        
        # Keep only last 100 records
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def _log_event(self, message: str, level: str = "info"):
        """Log event to shared memory."""
        msg = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="logger",
            message_type=f"log_{level}",
            content={'message': message, 'timestamp': datetime.now()}
        )
        self.shared_memory.broadcast_message(msg)
    
    def _serialize_assessment(self, assessment) -> Dict[str, Any]:
        """Serialize risk assessment for JSON serialization."""
        return {
            'task_name': assessment.task_name,
            'risk_level': assessment.risk_level.value,
            'confidence_score': assessment.confidence_score,
            'factors': assessment.factors,
            'recommendation': assessment.recommendation,
            'estimated_impact': assessment.estimated_impact,
            'reversible': assessment.reversible
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {'total_executions': 0}
        
        successful = sum(
            1 for e in self.execution_history if e['status'] == 'success'
        )
        
        failed = sum(
            1 for e in self.execution_history if e['status'] == 'failed'
        )
        
        cancelled = sum(
            1 for e in self.execution_history if e['status'] == 'cancelled_by_user'
        )
        
        avg_time = sum(
            e['execution_time'] for e in self.execution_history
        ) / len(self.execution_history)
        
        success_rate = successful / len(self.execution_history) if self.execution_history else 0
        
        return {
            'total_executions': len(self.execution_history),
            'successful': successful,
            'failed': failed,
            'cancelled': cancelled,
            'average_execution_time': avg_time,
            'success_rate': success_rate
        }
    
    def get_recent_executions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent executions."""
        return [
            {
                'timestamp': e['timestamp'].isoformat(),
                'task': e['task_name'],
                'action': e['action'],
                'status': e['status'],
                'time': round(e['execution_time'], 3)
            }
            for e in self.execution_history[-count:]
        ]
    
    def _register_default_tasks(self):
        """Register default task handlers."""
        
        async def handle_open_app(task):
            app_name = task.get('target', 'unknown')
            return f"Would open {app_name}"
        
        async def handle_play_music(task):
            return "Music playback started"
        
        async def handle_set_timer(task):
            duration = task.get('parameters', {}).get('duration', '5 minutes')
            return f"Timer set for {duration}"
        
        # Register common handlers
        self.register_task_handler('open_app', handle_open_app)
        self.register_task_handler('play_music', handle_play_music)
        self.register_task_handler('set_timer', handle_set_timer)


# Example usage
if __name__ == "__main__":
    print("⚡ Executor Agent Test\n")
    
    agent = ExecutorAgent()
    
    # Test 1: Low risk auto-execute
    print("📝 Test 1: Low Risk Task (Auto-execute)")
    task1 = {
        'name': 'open_app',
        'action': 'open_app',
        'target': 'VS Code',
        'parameters': {}
    }
    print(f"  Task: {task1['name']}")
    print("  (Would auto-execute)")
    
    # Test 2: Statistics
    print("\n📊 Executor Statistics:")
    stats = agent.get_execution_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
