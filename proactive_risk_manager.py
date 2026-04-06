"""
Risk Manager - Evaluates task safety and determines execution strategy

Critical component for safe autonomous operation.
Prevents dangerous actions while enabling proactive automation.
"""

from typing import Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class RiskLevel(Enum):
    """Risk classification for tasks."""
    LOW = "low"           # Safe to auto-execute
    MEDIUM = "medium"     # Request confirmation
    HIGH = "high"         # Require approval
    CRITICAL = "critical" # Manual intervention required


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    task_name: str
    risk_level: RiskLevel
    confidence_score: float
    factors: List[str]
    recommendation: str
    estimated_impact: str
    reversible: bool


class RiskManager:
    """
    Manages risk assessment for autonomous tasks.
    
    Ensures JARVIS operates safely while being proactive.
    """
    
    # Task risk classification
    TASK_RISK_MAP = {
        # LOW RISK - Auto-execute
        "low": {
            "open_app": "low",
            "play_music": "low",
            "set_timer": "low",
            "read_note": "low",
            "search_web": "low",
            "show_notification": "low",
            "create_reminder": "low",
            "open_browser": "low",
            "switch_app": "low",
            "take_screenshot": "low",
            "get_info": "low",
            "speak": "low",
            "list_files": "low",
        },
        
        # MEDIUM RISK - Confirm before executing
        "medium": {
            "send_email": "medium",
            "send_message": "medium",
            "create_file": "medium",
            "modify_file": "medium",
            "edit_text": "medium",
            "save_data": "medium",
            "run_script": "medium",
            "install_app": "medium",
            "download_file": "medium",
            "create_backup": "medium",
            "chmod_file": "medium",
            "rename_file": "medium",
            "create_folder": "medium",
        },
        
        # HIGH RISK - Require approval
        "high": {
            "delete_file": "high",
            "delete_folder": "high",
            "move_file": "high",
            "clear_cache": "high",
            "uninstall_app": "high",
            "modify_system_setting": "high",
            "access_sensitive_file": "high",
            "execute_command": "high",
            "modify_config": "high",
            "commit_repository": "high",
        },
        
        # CRITICAL - Manual intervention REQUIRED
        "critical": {
            "format_drive": "critical",
            "delete_system_file": "critical",
            "modify_registry": "critical",
            "system_shutdown": "critical",
            "system_restart": "critical",
            "disable_security": "critical",
            "destructive_operation": "critical",
        }
    }
    
    # Conditions that increase risk
    RISK_ESCALATORS = {
        "user_away": 1,           # +1 level if user away
        "batch_delete": 2,        # +2 levels for batch delete
        "system_file": 2,         # +2 levels for system files
        "irreversible": 1,        # +1 level if irreversible
        "high_latency": 1,        # +1 level with network latency
        "first_time": 1,          # +1 level for unknown task
    }
    
    def __init__(self):
        """Initialize risk manager."""
        self.assessment_history = []
        self.approved_tasks = set()
        self.blocked_tasks = set()
        self.user_risk_tolerance = "medium"  # Can be customized
    
    def assess_task(self, task: Dict[str, Any], 
                   user_context: Dict[str, Any] = None) -> RiskAssessment:
        """
        Assess risk level for a task.
        
        Args:
            task: Task dict with:
              - name: task name
              - action: action to perform
              - target: what to act on
              - parameters: task parameters
            user_context: dict with:
              - user_away: bool
              - time_of_day: int (hour)
              - network_available: bool
              - urgent: bool
              
        Returns:
            RiskAssessment
        """
        user_context = user_context or {}
        
        task_name = task.get('name', 'unknown')
        action = task.get('action', '').lower()
        target = task.get('target', '')
        params = task.get('parameters', {})
        
        # Get base risk
        base_risk = self._get_base_risk(action)
        
        # Calculate risk adjustments
        adjustments = self._calculate_risk_adjustments(
            task, base_risk, user_context
        )
        
        # Determine final risk level
        risk_level = self._determine_final_risk(base_risk, adjustments)
        
        # Generate factors and recommendation
        factors = self._analyze_risk_factors(
            task, base_risk, adjustments, user_context
        )
        estimate_impact = self._estimate_impact(action, target)
        reversible = self._is_reversible(action, target)
        
        # Create recommendation
        recommendation = self._generate_recommendation(
            risk_level, action, reversible, params
        )
        
        # Confidence score based on factors
        confidence = min(0.95, 0.5 + len(factors) * 0.1)
        
        assessment = RiskAssessment(
            task_name=task_name,
            risk_level=risk_level,
            confidence_score=confidence,
            factors=factors,
            recommendation=recommendation,
            estimated_impact=estimate_impact,
            reversible=reversible
        )
        
        # Store assessment
        self.assessment_history.append({
            'timestamp': datetime.now(),
            'assessment': assessment
        })
        
        return assessment
    
    def _get_base_risk(self, action: str) -> RiskLevel:
        """Get base risk level for action."""
        action_lower = action.lower()
        
        # Check against risk maps
        for risk_name, risk_dict in [
            ("critical", self.TASK_RISK_MAP["critical"]),
            ("high", self.TASK_RISK_MAP["high"]),
            ("medium", self.TASK_RISK_MAP["medium"]),
            ("low", self.TASK_RISK_MAP["low"]),
        ]:
            for task_key in risk_dict.keys():
                if task_key in action_lower:
                    return RiskLevel(risk_name)
        
        # Default to medium if unknown
        return RiskLevel.MEDIUM
    
    def _calculate_risk_adjustments(self, task: Dict[str, Any],
                                    base_risk: RiskLevel,
                                    user_context: Dict[str, Any]) -> int:
        """Calculate risk level adjustments in levels."""
        adjustments = 0
        
        # User away increases risk
        if user_context.get('user_away', False):
            adjustments += self.RISK_ESCALATORS["user_away"]
        
        # Batch operations increase risk
        if task.get('batch_size', 0) > 1:
            adjustments += self.RISK_ESCALATORS["batch_delete"]
        
        # System files increase risk
        if self._is_system_file(task.get('target', '')):
            adjustments += self.RISK_ESCALATORS["system_file"]
        
        # Irreversible operations increase risk
        if not self._is_reversible(task.get('action', ''), task.get('target', '')):
            adjustments += self.RISK_ESCALATORS["irreversible"]
        
        # Unknown task increases risk
        executions = task.get('execution_count', 0)
        if executions == 0:
            adjustments += self.RISK_ESCALATORS["first_time"]
        
        return adjustments
    
    def _determine_final_risk(self, base_risk: RiskLevel, 
                             adjustments: int) -> RiskLevel:
        """Determine final risk level after adjustments."""
        risk_order = [
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL
        ]
        
        current_idx = risk_order.index(base_risk)
        final_idx = min(len(risk_order) - 1, current_idx + adjustments)
        
        return risk_order[final_idx]
    
    def _analyze_risk_factors(self, task: Dict[str, Any],
                             base_risk: RiskLevel,
                             adjustments: int,
                             user_context: Dict[str, Any]) -> List[str]:
        """Analyze and list risk factors."""
        factors = []
        
        # Base risk factor
        factors.append(f"Base risk: {base_risk.value}")
        
        # User context factors
        if user_context.get('user_away'):
            factors.append("User is away (increased risk)")
        
        if not user_context.get('network_available', True):
            factors.append("Network unavailable (rollback uncertain)")
        
        if user_context.get('urgent'):
            factors.append("Task marked urgent")
        
        # Task-specific factors
        if task.get('batch_size', 0) > 1:
            factors.append(f"Batch operation ({task['batch_size']} items)")
        
        if self._is_system_file(task.get('target', '')):
            factors.append("Targets system files")
        
        if not self._is_reversible(task.get('action', ''), task.get('target', '')):
            factors.append("Action is irreversible")
        
        if task.get('execution_count', 0) == 0:
            factors.append("First-time execution of this task")
        
        return factors
    
    def _estimate_impact(self, action: str, target: str) -> str:
        """Estimate impact of an action."""
        action_lower = action.lower()
        
        if 'delete' in action_lower:
            return f"Will permanently remove: {target}"
        elif 'modify' in action_lower or 'edit' in action_lower:
            return f"Will change: {target}"
        elif 'send' in action_lower or 'email' in action_lower:
            return f"Will communicate: {target}"
        elif 'shutdown' in action_lower or 'restart' in action_lower:
            return "Will interrupt all active operations"
        elif 'open' in action_lower:
            return f"Will launch: {target}"
        else:
            return f"Will perform: {action} on {target}"
    
    def _is_reversible(self, action: str, target: str) -> bool:
        """Check if action is reversible."""
        action_lower = action.lower()
        
        # Irreversible operations
        irreversible_keywords = ['delete', 'format', 'clear', 'wipe', 'destroy']
        
        for keyword in irreversible_keywords:
            if keyword in action_lower:
                return False
        
        return True
    
    def _is_system_file(self, target: str) -> bool:
        """Check if target is a system file."""
        system_paths = [
            'windows',
            'system32',
            'system',
            'registry',
            'boot',
            'kernel',
            'drivers',
            '/etc/',
            '/sys/',
            '/boot/',
        ]
        
        target_lower = target.lower()
        return any(sys_path in target_lower for sys_path in system_paths)
    
    def _generate_recommendation(self, risk_level: RiskLevel,
                                action: str, reversible: bool,
                                params: Dict) -> str:
        """Generate execution recommendation."""
        
        if risk_level == RiskLevel.LOW:
            return "✅ SAFE: Can auto-execute with high confidence"
        
        elif risk_level == RiskLevel.MEDIUM:
            return "⚠️ MODERATE: Should request user confirmation before executing"
        
        elif risk_level == RiskLevel.HIGH:
            return "🔴 HIGH: Requires explicit user approval before execution"
        
        else:  # CRITICAL
            return "⛔ CRITICAL: Manual intervention required. Do NOT auto-execute"
    
    def should_auto_execute(self, risk_level: RiskLevel, 
                           user_auto_approve: bool = False) -> bool:
        """Determine if task should auto-execute."""
        if risk_level == RiskLevel.LOW:
            return True
        elif risk_level == RiskLevel.MEDIUM and user_auto_approve:
            return True
        else:
            return False
    
    def should_ask_user(self, risk_level: RiskLevel) -> bool:
        """Determine if we should ask user for approval."""
        return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
    
    def get_execution_strategy(self, risk_level: RiskLevel) -> str:
        """Get recommended execution strategy."""
        strategies = {
            RiskLevel.LOW: "auto_execute",
            RiskLevel.MEDIUM: "ask_first",
            RiskLevel.HIGH: "ask_detailed",
            RiskLevel.CRITICAL: "manual_only"
        }
        return strategies.get(risk_level, "ask_first")
    
    def set_user_risk_tolerance(self, tolerance: str):
        """Set user risk tolerance ('low', 'medium', 'high')."""
        if tolerance in ['low', 'medium', 'high']:
            self.user_risk_tolerance = tolerance
    
    def get_risk_report(self) -> Dict[str, Any]:
        """Get risk assessment report."""
        if not self.assessment_history:
            return {'total_assessments': 0}
        
        # Count by risk level
        risk_counts = {level.value: 0 for level in RiskLevel}
        for entry in self.assessment_history:
            risk_level = entry['assessment'].risk_level
            risk_counts[risk_level.value] += 1
        
        # Recent assessments
        recent = [
            {
                'task': entry['assessment'].task_name,
                'risk': entry['assessment'].risk_level.value,
                'time': entry['timestamp']
            }
            for entry in self.assessment_history[-5:]
        ]
        
        return {
            'total_assessments': len(self.assessment_history),
            'risk_distribution': risk_counts,
            'recent_assessments': recent,
            'user_tolerance': self.user_risk_tolerance
        }


# Example usage
if __name__ == "__main__":
    print("🛡️ Risk Manager Test\n")
    
    manager = RiskManager()
    
    # Test 1: Low risk task
    print("📝 Test 1: Open App (Low Risk)")
    task1 = {
        'name': 'open_vscode',
        'action': 'open_app',
        'target': 'vs_code',
        'parameters': {}
    }
    assessment1 = manager.assess_task(task1)
    print(f"  Risk: {assessment1.risk_level.value}")
    print(f"  Recommendation: {assessment1.recommendation}")
    print(f"  Auto-execute: {manager.should_auto_execute(assessment1.risk_level)}")
    
    # Test 2: Medium risk task
    print("\n📝 Test 2: Delete File (High Risk)")
    task2 = {
        'name': 'delete_log',
        'action': 'delete_file',
        'target': 'documents/temp.log',
        'parameters': {},
        'batch_size': 1
    }
    assessment2 = manager.assess_task(task2)
    print(f"  Risk: {assessment2.risk_level.value}")
    print(f"  Factors: {', '.join(assessment2.factors)}")
    print(f"  Recommendation: {assessment2.recommendation}")
    print(f"  Reversible: {assessment2.reversible}")
    
    # Test 3: High risk + user away
    print("\n📝 Test 3: Delete with User Away (Critical)")
    task3 = {
        'name': 'batch_delete',
        'action': 'delete_file',
        'target': 'documents',
        'parameters': {},
        'batch_size': 10
    }
    assessment3 = manager.assess_task(
        task3,
        user_context={'user_away': True}
    )
    print(f"  Risk: {assessment3.risk_level.value}")
    print(f"  Strategy: {manager.get_execution_strategy(assessment3.risk_level)}")
    print(f"  Recommendation: {assessment3.recommendation}")
    
    # Show report
    print("\n📊 Risk Report:")
    report = manager.get_risk_report()
    for key, value in report.items():
        if key != 'recent_assessments':
            print(f"  {key}: {value}")
