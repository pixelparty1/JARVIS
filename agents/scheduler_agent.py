"""
Scheduler Agent - Intelligent task scheduling

Manages autonomous execution of time-based and event-based tasks.
Coordinates with predictor and executor agents.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import heapq
from agents.base_agent import BaseAgent, AgentMessage


class ScheduleType(Enum):
    """Task schedule type."""
    ONCE = "once"           # Run once at specific time
    HOURLY = "hourly"       # Run every hour
    DAILY = "daily"         # Run daily at specific time
    WEEKLY = "weekly"       # Run on specific day
    INTERVAL = "interval"   # Run every N seconds/minutes
    PREDICTOR = "predictor" # Run based on predictions


class ScheduledTask:
    """Represents a scheduled task."""
    
    def __init__(self, task_id: str, task: Dict[str, Any],
                 schedule_type: ScheduleType,
                 next_run: datetime,
                 priority: int = 5,
                 recurring: bool = False):
        """Initialize scheduled task."""
        self.task_id = task_id
        self.task = task
        self.schedule_type = schedule_type
        self.next_run = next_run
        self.priority = priority
        self.recurring = recurring
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0
    
    def __lt__(self, other):
        """Comparison for heap queue."""
        if self.next_run != other.next_run:
            return self.next_run < other.next_run
        return self.priority < other.priority
    
    def reschedule(self):
        """Reschedule task based on schedule type."""
        if not self.recurring:
            return False
        
        if self.schedule_type == ScheduleType.HOURLY:
            self.next_run = datetime.now() + timedelta(hours=1)
            return True
        
        elif self.schedule_type == ScheduleType.DAILY:
            hour = self.task.get('scheduled_hour', 9)
            now = datetime.now()
            next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            if next_run <= now:
                next_run += timedelta(days=1)
            
            self.next_run = next_run
            return True
        
        elif self.schedule_type == ScheduleType.WEEKLY:
            day_of_week = self.task.get('scheduled_day', 0)  # 0 = Monday
            hour = self.task.get('scheduled_hour', 9)
            
            now = datetime.now()
            days_ahead = (day_of_week - now.weekday()) % 7
            
            if days_ahead == 0:
                next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    days_ahead = 7
            
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            self.next_run = next_run
            return True
        
        elif self.schedule_type == ScheduleType.INTERVAL:
            interval_seconds = self.task.get('interval_seconds', 300)
            self.next_run = datetime.now() + timedelta(seconds=interval_seconds)
            return True
        
        return False


class SchedulerAgent(BaseAgent):
    """
    Schedules and manages proactive task execution.
    
    Features:
    - Multiple schedule types
    - Priority-based execution
    - Task history tracking
    - Upcoming task monitoring
    """
    
    def __init__(self, agent_id: str = "scheduler", brain=None):
        """Initialize scheduler agent."""
        super().__init__(agent_id, "scheduler", brain)
        
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.task_queue = []  # Min-heap for efficient scheduling
        self.execution_history = []
        self.max_concurrent = 3  # Max concurrent task execution
        
        self.executor_callback: Optional[Callable] = None
    
    def get_capabilities(self) -> List[str]:
        """Get scheduler capabilities."""
        return [
            "schedule_task",
            "reschedule_task",
            "cancel_task",
            "get_upcoming_tasks",
            "execute_pending_tasks"
        ]
    
    def set_executor_callback(self, callback: Callable):
        """Set callback to execute tasks."""
        self.executor_callback = callback
    
    def schedule_task(self, task: Dict[str, Any],
                     schedule_type: ScheduleType,
                     next_run: datetime,
                     task_id: Optional[str] = None,
                     priority: int = 5,
                     recurring: bool = False) -> str:
        """
        Schedule a new task.
        
        Args:
            task: Task dict
            schedule_type: When to run
            next_run: Next execution time
            task_id: Unique task ID (auto-generated if None)
            priority: 1-10 (lower = higher priority)
            recurring: Whether to reschedule after execution
            
        Returns:
            Task ID
        """
        if task_id is None:
            task_id = f"task_{len(self.scheduled_tasks)}_{int(__import__('time').time() * 1000)}"
        
        scheduled = ScheduledTask(
            task_id=task_id,
            task=task,
            schedule_type=schedule_type,
            next_run=next_run,
            priority=priority,
            recurring=recurring
        )
        
        self.scheduled_tasks[task_id] = scheduled
        heapq.heappush(self.task_queue, scheduled)
        
        self._log_event(
            f"Scheduled task '{task['name']}' ({task_id}) for {next_run}",
            "info"
        )
        
        return task_id
    
    def schedule_hourly(self, task: Dict[str, Any], task_id: str = None) -> str:
        """Schedule task to run every hour."""
        next_run = datetime.now() + timedelta(hours=1)
        return self.schedule_task(
            task, ScheduleType.HOURLY, next_run, task_id, recurring=True
        )
    
    def schedule_daily(self, task: Dict[str, Any], hour: int = 9,
                      task_id: str = None) -> str:
        """Schedule task to run daily at specific hour."""
        task['scheduled_hour'] = hour
        
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return self.schedule_task(
            task, ScheduleType.DAILY, next_run, task_id, recurring=True
        )
    
    def schedule_weekly(self, task: Dict[str, Any], day: int = 0,
                       hour: int = 9, task_id: str = None) -> str:
        """
        Schedule task weekly.
        
        Args:
            task: Task dict
            day: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day
            task_id: Optional task ID
        """
        task['scheduled_day'] = day
        task['scheduled_hour'] = hour
        
        now = datetime.now()
        days_ahead = (day - now.weekday()) % 7
        
        if days_ahead == 0:
            next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_run <= now:
                days_ahead = 7
        
        next_run = now + timedelta(days=days_ahead)
        next_run = next_run.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        return self.schedule_task(
            task, ScheduleType.WEEKLY, next_run, task_id, recurring=True
        )
    
    def schedule_at(self, task: Dict[str, Any], when: datetime,
                   task_id: str = None) -> str:
        """Schedule task to run once at specific time."""
        return self.schedule_task(
            task, ScheduleType.ONCE, when, task_id, recurring=False
        )
    
    def schedule_in(self, task: Dict[str, Any], seconds: float,
                   task_id: str = None) -> str:
        """Schedule task to run in N seconds."""
        when = datetime.now() + timedelta(seconds=seconds)
        return self.schedule_task(
            task, ScheduleType.ONCE, when, task_id, recurring=False
        )
    
    def schedule_every(self, task: Dict[str, Any], interval_seconds: float,
                      task_id: str = None) -> str:
        """Schedule task to run every N seconds."""
        task['interval_seconds'] = interval_seconds
        next_run = datetime.now() + timedelta(seconds=interval_seconds)
        
        return self.schedule_task(
            task, ScheduleType.INTERVAL, next_run, task_id, recurring=True
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id not in self.scheduled_tasks:
            return False
        
        del self.scheduled_tasks[task_id]
        self._log_event(f"Cancelled task '{task_id}'", "info")
        return True
    
    def reschedule_task(self, task_id: str, new_next_run: datetime) -> bool:
        """Reschedule a task."""
        if task_id not in self.scheduled_tasks:
            return False
        
        task = self.scheduled_tasks[task_id]
        task.next_run = new_next_run
        
        # Rebuild heap
        self.task_queue = list(self.scheduled_tasks.values())
        heapq.heapify(self.task_queue)
        
        return True
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main scheduler execution loop.
        
        Checks for pending tasks and executes them.
        """
        self.update_state("busy")
        
        try:
            # Get pending tasks
            pending = self.get_pending_tasks()
            
            # Execute with concurrency control
            results = []
            for pending_task in pending[:self.max_concurrent]:
                result = await self._execute_pending_task(pending_task)
                results.append(result)
            
            self.update_state("idle")
            
            return {
                'status': 'success',
                'tasks_executed': len(results),
                'results': results
            }
            
        except Exception as e:
            self.record_failure(str(e))
            self.update_state("error")
            
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _execute_pending_task(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single pending task."""
        task_id = task_info['task_id']
        task = task_info['task']
        
        scheduled_task = self.scheduled_tasks[task_id]
        
        try:
            # Execute via callback
            if self.executor_callback:
                result = await asyncio.to_thread(
                    self.executor_callback,
                    task
                )
            else:
                result = {"status": "no_executor"}
            
            # Update task stats
            scheduled_task.last_run = datetime.now()
            scheduled_task.run_count += 1
            scheduled_task.success_count += 1
            
            # Reschedule if recurring
            if scheduled_task.recurring:
                scheduled_task.reschedule()
                heapq.heappush(self.task_queue, scheduled_task)
            else:
                del self.scheduled_tasks[task_id]
            
            self._log_event(
                f"Executed task '{task['name']}' successfully",
                "info"
            )
            
            # Record execution
            self.execution_history.append({
                'timestamp': datetime.now(),
                'task_id': task_id,
                'task_name': task.get('name', 'unknown'),
                'status': 'success',
                'result': result
            })
            
            return {
                'task_id': task_id,
                'status': 'success',
                'result': result
            }
            
        except Exception as e:
            scheduled_task.failure_count += 1
            
            self._log_event(
                f"Failed to execute task '{task.get('name')}': {str(e)}",
                "error"
            )
            
            # Record failure
            self.execution_history.append({
                'timestamp': datetime.now(),
                'task_id': task_id,
                'task_name': task.get('name', 'unknown'),
                'status': 'failed',
                'error': str(e)
            })
            
            return {
                'task_id': task_id,
                'status': 'failed',
                'error': str(e)
            }
    
    def get_pending_tasks(self, within_seconds: int = 60) -> List[Dict[str, Any]]:
        """
        Get tasks due for execution.
        
        Args:
            within_seconds: Get tasks due within this many seconds
            
        Returns:
            List of pending tasks
        """
        pending = []
        now = datetime.now()
        threshold = now + timedelta(seconds=within_seconds)
        
        for task_id, task in self.scheduled_tasks.items():
            if now <= task.next_run <= threshold:
                pending.append({
                    'task_id': task_id,
                    'task': task.task,
                    'due_in_seconds': (task.next_run - now).total_seconds(),
                    'priority': task.priority
                })
        
        # Sort by due time
        pending.sort(key=lambda x: x['due_in_seconds'])
        
        return pending
    
    def get_upcoming_tasks(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get next N upcoming tasks."""
        upcoming = []
        
        for task in sorted(self.scheduled_tasks.values())[:count]:
            upcoming.append({
                'task_id': task.task_id,
                'task_name': task.task.get('name', 'unknown'),
                'next_run': task.next_run.isoformat(),
                'schedule_type': task.schedule_type.value,
                'priority': task.priority,
                'recurring': task.recurring
            })
        
        return upcoming
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        total_scheduled = len(self.scheduled_tasks)
        
        recurring = sum(
            1 for t in self.scheduled_tasks.values() if t.recurring
        )
        
        one_time = total_scheduled - recurring
        
        total_executions = sum(
            t.run_count for t in self.scheduled_tasks.values()
        )
        
        successful_executions = sum(
            t.success_count for t in self.scheduled_tasks.values()
        )
        
        success_rate = (
            successful_executions / total_executions
            if total_executions > 0 else 0
        )
        
        return {
            'total_scheduled': total_scheduled,
            'recurring_tasks': recurring,
            'one_time_tasks': one_time,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': success_rate,
            'execution_history_size': len(self.execution_history)
        }
    
    def _log_event(self, message: str, level: str = "info"):
        """Log event to shared memory."""
        msg = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="logger",
            message_type=f"log_{level}",
            content={'message': message}
        )
        self.shared_memory.broadcast_message(msg)


# Example usage
if __name__ == "__main__":
    print("⏰ Scheduler Agent Test\n")
    
    agent = SchedulerAgent()
    
    # Test 1: Schedule in 5 seconds
    print("📝 Test 1: Schedule in 5 seconds")
    task1 = {
        'name': 'test_task',
        'action': 'test',
        'target': 'demo'
    }
    task_id = agent.schedule_in(task1, 5)
    print(f"  Scheduled task: {task_id}")
    
    # Test 2: Schedule daily
    print("\n📝 Test 2: Schedule daily at 9 AM")
    task2 = {
        'name': 'daily_backup',
        'action': 'backup',
        'target': 'documents'
    }
    task_id = agent.schedule_daily(task2, hour=9)
    print(f"  Scheduled task: {task_id}")
    
    # Test 3: Get upcoming
    print("\n⏳ Upcoming Tasks:")
    for task in agent.get_upcoming_tasks():
        print(f"  - {task['task_name']}: {task['next_run']}")
    
    # Test 4: Statistics
    print("\n📊 Scheduler Stats:")
    stats = agent.get_scheduler_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
