"""
JARVIS Agent Executor Module
Executes planned steps and handles failures
"""

from typing import Dict, Any, List, Tuple, Optional
from tool_registry import ToolRegistry
from brain import JarvisBrain
import json
from datetime import datetime

class ExecutionResult:
    """Result of executing a step"""
    
    def __init__(self, step_num: int, step: Dict, success: bool, output: Any, error: str = ""):
        self.step_num = step_num
        self.step = step
        self.success = success
        self.output = output
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "step_num": self.step_num,
            "action": self.step.get("action"),
            "tool": self.step.get("tool"),
            "success": self.success,
            "output": str(self.output)[:200] if self.output else None,
            "error": self.error,
            "timestamp": self.timestamp
        }


class ExecutionContext:
    """Context for executing a plan"""
    
    def __init__(self, goal: str, steps: List[Dict]):
        self.goal = goal
        self.steps = steps
        self.current_step = 0
        self.results = []
        self.shared_data = {}  # Data passed between steps
        self.status = "running"
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_result(self, result: ExecutionResult):
        """Add execution result"""
        self.results.append(result)
        self.current_step += 1
    
    def set_shared_data(self, key: str, value: Any):
        """Store data to share between steps"""
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """Retrieve shared data"""
        return self.shared_data.get(key, default)
    
    def to_dict(self) -> Dict:
        return {
            "goal": self.goal,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": len(self.steps),
            "results": [r.to_dict() for r in self.results],
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else None
        }


class Executor:
    """Executes planned steps using available tools"""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.brain = JarvisBrain()
        self.tool_registry = tool_registry
        self.execution_history = []
        self.max_retries = 2
    
    def execute_plan(self, goal: str, steps: List[Dict], context_data: Dict = None) -> ExecutionContext:
        """
        Execute all steps in a plan
        
        Args:
            goal: The overall goal
            steps: List of steps to execute
            context_data: Additional context
            
        Returns:
            ExecutionContext with results
        """
        print(f"\n▶️ Executing plan for: {goal}")
        print(f"📋 Total steps: {len(steps)}\n")
        
        context = ExecutionContext(goal, steps)
        
        # Process each step
        for i, step in enumerate(steps, 1):
            print(f"\n{'='*50}")
            print(f"Step {i}/{len(steps)}: {step.get('action', 'Unknown')}")
            print(f"{'='*50}")
            
            result = self._execute_step(i, step, context)
            context.add_result(result)
            
            if not result.success:
                # Decide: retry or fail?
                if i < self.max_retries:
                    print(f"\n🔄 Retrying step {i}...")
                    retry_result = self._execute_step(i, step, context)
                    context.results[-1] = retry_result
                else:
                    print(f"\n⚠️ Step {i} failed, continuing with remaining steps...")
        
        context.status = "completed"
        context.end_time = datetime.now()
        
        self.execution_history.append(context)
        
        # Print summary
        self._print_execution_summary(context)
        
        return context
    
    def _execute_step(self, step_num: int, step: Dict, context: ExecutionContext) -> ExecutionResult:
        """Execute a single step"""
        tool_name = step.get("tool", "").lower()
        action = step.get("action", "")
        parameters = step.get("parameters", {})
        expected_output = step.get("expected_output", "")
        
        print(f"🔧 Tool: {tool_name}")
        print(f"📋 Parameters: {parameters}")
        print(f"✅ Expected: {expected_output}")
        
        # Step 1: Resolve parameters (substitute shared data)
        resolved_params = self._resolve_parameters(parameters, context)
        
        # Step 2: Call tool
        success, output = self.tool_registry.call_tool(tool_name, **resolved_params)
        
        if success:
            print(f"📤 Output: {str(output)[:100]}...")
            
            # Store output for next steps
            context.set_shared_data(f"step_{step_num}_output", output)
            
            # Verify output meets expectations
            if expected_output:
                verified = self._verify_output(output, expected_output)
                if not verified:
                    print(f"⚠️ Output may not match expectations")
        else:
            print(f"❌ Error: {output}")
        
        return ExecutionResult(step_num, step, success, output, output if not success else "")
    
    def _resolve_parameters(self, parameters: Dict, context: ExecutionContext) -> Dict:
        """Resolve parameter values (substitute variables, etc.)"""
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("$"):
                # Variable reference
                var_name = value[1:]
                resolved[key] = context.get_shared_data(var_name, value)
            else:
                resolved[key] = value
        
        return resolved
    
    def _verify_output(self, output: Any, expected: str) -> bool:
        """Verify output matches expectations (simple heuristic)"""
        output_str = str(output).lower()
        expected_str = expected.lower()
        
        # Simple keywords matching
        keywords = expected_str.split()
        matched = sum(1 for kw in keywords if kw in output_str)
        
        return matched >= len(keywords) * 0.5  # 50% threshold
    
    def _print_execution_summary(self, context: ExecutionContext):
        """Print execution summary"""
        successful = sum(1 for r in context.results if r.success)
        failed = sum(1 for r in context.results if not r.success)
        
        print(f"\n{'='*50}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'='*50}")
        print(f"Goal: {context.goal}")
        print(f"Status: {context.status.upper()}")
        print(f"Steps completed: {context.current_step}/{len(context.steps)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        duration = (context.end_time - context.start_time).total_seconds()
        print(f"⏱️ Duration: {duration:.2f}s")
    
    def execute_step_by_step(self, goal: str, steps: List[Dict]) -> ExecutionContext:
        """
        Execute steps interactively (wait for user confirmation between steps)
        
        Args:
            goal: The overall goal
            steps: List of steps
            
        Returns:
            ExecutionContext
        """
        print(f"\n▶️ INTERACTIVE EXECUTION: {goal}")
        print(f"📋 Total steps: {len(steps)}")
        
        context = ExecutionContext(goal, steps)
        
        for i, step in enumerate(steps, 1):
            print(f"\n{'='*50}")
            print(f"Step {i}/{len(steps)}")
            print(f"Action: {step.get('action')}")
            print(f"Tool: {step.get('tool')}")
            print(f"Params: {step.get('parameters')}")
            print(f"{'='*50}")
            
            # Ask for confirmation
            response = input("\n▶️ Continue? (y/n/skip): ").lower()
            
            if response == "n":
                print("❌ Execution cancelled")
                context.status = "cancelled"
                break
            elif response == "skip":
                print("⊘ Skipping step")
                context.add_result(ExecutionResult(i, step, None, None, "Skipped"))
                continue
            
            # Execute
            result = self._execute_step(i, step, context)
            context.add_result(result)
        
        context.status = "completed"
        context.end_time = datetime.now()
        self.execution_history.append(context)
        
        self._print_execution_summary(context)
        return context
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get execution history"""
        return [e.to_dict() for e in self.execution_history[-limit:]]
    
    def analyze_failures(self) -> Dict:
        """Analyze failure patterns"""
        failures = []
        
        for execution in self.execution_history:
            for result in execution.results:
                if not result.success:
                    failures.append({
                        "goal": execution.goal,
                        "step": result.step.get("action"),
                        "tool": result.step.get("tool"),
                        "error": result.error
                    })
        
        return {
            "total_failures": len(failures),
            "recent_failures": failures[-10:],
            "failed_tools": list(set(f["tool"] for f in failures)),
            "failure_rate": len(failures) / max(1, sum(len(e.results) for e in self.execution_history))
        }
