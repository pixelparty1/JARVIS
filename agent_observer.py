"""
JARVIS Agent Observer Module
Observes execution results and determines if replanning is needed
"""

from typing import Dict, List, Any, Tuple, Optional
from agent_executor import ExecutionContext, ExecutionResult
from brain import JarvisBrain
import json

class ObserverResult:
    """Result of observation"""
    
    def __init__(self, step_num: int, success: bool, insight: str, recommendation: str):
        self.step_num = step_num
        self.success = success
        self.insight = insight
        self.recommendation = recommendation  # "continue", "retry", "replan", "fail"


class Observer:
    """Observes execution and provides feedback"""
    
    def __init__(self):
        self.brain = JarvisBrain()
        self.observations = []
    
    def observe(self, context: ExecutionContext) -> List[ObserverResult]:
        """
        Observe execution results
        
        Args:
            context: ExecutionContext with results
            
        Returns:
            List of observations
        """
        print(f"\n🔍 Observing execution results...")
        
        observations = []
        
        for result in context.results:
            obs = self._analyze_result(result, context)
            observations.append(obs)
            self.observations.append(obs)
        
        return observations
    
    def _analyze_result(self, result: ExecutionResult, context: ExecutionContext) -> ObserverResult:
        """Analyze a single execution result"""
        step_num = result.step_num
        
        if result.success:
            return ObserverResult(
                step_num=step_num,
                success=True,
                insight="Step executed successfully",
                recommendation="continue"
            )
        else:
            # Analyze failure
            insight = self._analyze_failure(result)
            recommendation = self._recommend_action(result, context)
            
            return ObserverResult(
                step_num=step_num,
                success=False,
                insight=insight,
                recommendation=recommendation
            )
    
    def _analyze_failure(self, result: ExecutionResult) -> str:
        """Analyze why a step might have failed"""
        error = result.error or "Unknown error"
        tool = result.step.get("tool", "")
        
        # Simple analysis
        if "not found" in error.lower():
            return f"Tool or resource not found: {tool}"
        elif "timeout" in error.lower():
            return "Operation timed out"
        elif "permission" in error.lower():
            return "Permission denied"
        elif "invalid" in error.lower():
            return "Invalid parameters or input"
        else:
            return f"Execution failed: {error[:100]}"
    
    def _recommend_action(self, result: ExecutionResult, context: ExecutionContext) -> str:
        """Recommend what to do after failure"""
        step_num = result.step_num
        tool = result.step.get("tool", "")
        
        # Count previous attempts
        previous_attempts = sum(
            1 for r in context.results[:step_num-1]
            if r.step.get("tool") == tool
        )
        
        if previous_attempts >= 2:
            return "replan"  # Already retried, need new plan
        else:
            return "retry"  # Can retry
    
    def should_replan(self, observations: List[ObserverResult]) -> bool:
        """Determine if replanning is needed"""
        for obs in observations:
            if obs.recommendation == "replan":
                return True
        return False
    
    def get_failure_info(self, observations: List[ObserverResult]) -> str:
        """Get summary of failures for replanning"""
        failures = [obs for obs in observations if not obs.success]
        
        summary = "Failures encountered:\n"
        for failure in failures:
            summary += f"  • Step {failure.step_num}: {failure.insight}\n"
        
        return summary
    
    def verify_goal_achievement(self, goal: str, context: ExecutionContext) -> Tuple[bool, str]:
        """
        Verify if the goal was actually achieved
        Uses AI to make judgment
        
        Args:
            goal: The original goal
            context: Execution context
            
        Returns:
            (achieved, explanation) tuple
        """
        print(f"\n✓ Verifying goal achievement...")
        
        # Build verification prompt
        steps_summary = "\n".join([
            f"Step {r.step_num}: {r.step.get('action')} - {'✓' if r.success else '✗'}"
            for r in context.results
        ])
        
        verification_prompt = f"""Did we successfully achieve this goal?

GOAL: {goal}

EXECUTION RESULTS:
{steps_summary}

OUTPUT: {str(context.shared_data.get('final_output', ''))[:500]}

Respond with:
1. YES or NO
2. Why (1-2 sentences)

Format: YES/NO: Explanation"""
        
        try:
            response = self.brain.query(verification_prompt)
            
            achieved = response.strip().startswith("YES")
            explanation = response.split(":", 1)[1].strip() if ":" in response else response
            
            return achieved, explanation
        except:
            # Heuristic: if all steps succeeded, goal achieved
            all_success = all(r.success for r in context.results)
            return all_success, "Judgment based on step success"
    
    def get_feedback(self, observations: List[ObserverResult]) -> str:
        """Get human-readable feedback"""
        successful = sum(1 for o in observations if o.success)
        total = len(observations)
        
        feedback = f"📊 Observation Results:\n"
        feedback += f"Success rate: {successful}/{total} ({100*successful//total}%)\n\n"
        
        feedback += "Details:\n"
        for obs in observations:
            status = "✅" if obs.success else "❌"
            feedback += f"  {status} Step {obs.step_num}: {obs.insight}\n"
            feedback += f"     → Recommendation: {obs.recommendation}\n"
        
        return feedback
    
    def summarize_observations(self) -> Dict:
        """Get summary of all observations"""
        successful = sum(1 for o in self.observations if o.success)
        failed = sum(1 for o in self.observations if not o.success)
        
        recommendations = {}
        for obs in self.observations:
            rec = obs.recommendation
            recommendations[rec] = recommendations.get(rec, 0) + 1
        
        return {
            "total_observations": len(self.observations),
            "successful_steps": successful,
            "failed_steps": failed,
            "success_rate": successful / max(1, len(self.observations)),
            "recommendations": recommendations,
            "most_common_issues": self._get_common_issues()
        }
    
    def _get_common_issues(self) -> List[str]:
        """Get most common failure patterns"""
        failed_obs = [o for o in self.observations if not o.success]
        
        issues = {}
        for obs in failed_obs:
            insight = obs.insight
            issues[insight] = issues.get(insight, 0) + 1
        
        # Sort by frequency
        sorted_issues = sorted(issues.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5]]
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for improvement"""
        summary = self.summarize_observations()
        recommendations = []
        
        if summary["success_rate"] < 0.5:
            recommendations.append("Low success rate. Consider improving tool implementations or parameters.")
        
        if summary["recommendations"].get("replan", 0) > 2:
            recommendations.append("Multiple replan recommendations. May need to revise planning logic.")
        
        if summary["recommendations"].get("retry", 0) > 3:
            recommendations.append("Many retries needed. Tools may be unstable.")
        
        common_issues = summary["most_common_issues"]
        if common_issues:
            recommendations.append(f"Most common issue: {common_issues[0]}")
        
        return recommendations if recommendations else ["System operating normally"]
