"""
Orchestrator Bridge - Connect Integrations to JARVIS Orchestrator

Features:
- Tool discovery across all integrations
- Integration with JARVIS Planner/Executor
- Unified tool registry
- Async integration execution
- Statistics and monitoring
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .base import ToolDefinition, BaseIntegration, IntegrationError, EventBus
from .auth_manager import AuthManager
from .workflow import WorkflowEngine


@dataclass
class ToolExecution:
    """Record of a tool execution."""
    tool_name: str
    integration_name: str
    parameters: Dict[str, Any]
    result: Any = None
    error: str = None
    duration_ms: float = 0.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class IntegrationRegistry:
    """
    Registry for all integrations.
    
    Provides tool discovery and unified execution interface.
    """
    
    def __init__(self, event_bus: EventBus = None):
        """
        Initialize registry.
        
        Args:
            event_bus: Shared EventBus instance
        """
        self.integrations = {}
        self.event_bus = event_bus or EventBus()
        self.execution_log = []
    
    def register_integration(self, integration: BaseIntegration) -> None:
        """
        Register an integration.
        
        Args:
            integration: Integration instance
        """
        self.integrations[integration.name] = integration
        print(f"✅ Registered integration: {integration.name}")
    
    def get_integration(self, name: str) -> Optional[BaseIntegration]:
        """Get integration by name."""
        return self.integrations.get(name)
    
    def discover_tools(self) -> Dict[str, List[ToolDefinition]]:
        """
        Discover all available tools.
        
        Returns:
            Dict mapping integration names to tools
        """
        tools = {}
        for name, integration in self.integrations.items():
            tools[name] = integration.get_tools()
        return tools
    
    def list_all_tools(self) -> List[Dict[str, Any]]:
        """
        List all tools across integrations.
        
        Returns:
            List of tool definitions with integration context
        """
        all_tools = []
        for integration_name, integration in self.integrations.items():
            for tool in integration.get_tools():
                tool_info = {
                    "id": f"{integration_name}.{tool.name}",
                    "integration": integration_name,
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                    "returns": tool.returns,
                    "category": tool.category
                }
                all_tools.append(tool_info)
        
        return all_tools
    
    async def execute_tool(self, integration_name: str, tool_name: str,
                          **kwargs) -> Any:
        """
        Execute a tool.
        
        Args:
            integration_name: Integration name
            tool_name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        import time
        
        integration = self.get_integration(integration_name)
        if not integration:
            raise IntegrationError(f"Integration not found: {integration_name}")
        
        start = time.time()
        try:
            result = await integration._execute_tool(tool_name, **kwargs)
            duration = (time.time() - start) * 1000
            
            execution = ToolExecution(
                tool_name=tool_name,
                integration_name=integration_name,
                parameters=kwargs,
                result=result,
                duration_ms=duration
            )
            
            self.execution_log.append(execution)
            
            print(f"✅ {integration_name}.{tool_name} → {type(result).__name__} ({duration:.1f}ms)")
            
            return result
        
        except Exception as e:
            duration = (time.time() - start) * 1000
            
            execution = ToolExecution(
                tool_name=tool_name,
                integration_name=integration_name,
                parameters=kwargs,
                error=str(e),
                duration_ms=duration
            )
            
            self.execution_log.append(execution)
            
            print(f"❌ {integration_name}.{tool_name} failed: {e}")
            
            raise IntegrationError(f"{integration_name}.{tool_name} failed: {e}")
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tool by full ID (integration.tool).
        
        Args:
            tool_id: Tool ID
            
        Returns:
            Tool definition dict
        """
        for tool in self.list_all_tools():
            if tool["id"] == tool_id:
                return tool
        
        return None
    
    def get_execution_history(self, limit: int = 100) -> List[ToolExecution]:
        """Get execution history."""
        return self.execution_log[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_executions = len(self.execution_log)
        successful = sum(1 for e in self.execution_log if e.error is None)
        failed = sum(1 for e in self.execution_log if e.error is not None)
        
        avg_duration = 0.0
        if self.execution_log:
            avg_duration = sum(e.duration_ms for e in self.execution_log) / len(self.execution_log)
        
        return {
            "total_integrations": len(self.integrations),
            "total_tools": len(self.list_all_tools()),
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "avg_execution_time_ms": avg_duration
        }


class PlannerToolInterface:
    """
    Interface between IntegrationRegistry and JARVIS Planner.
    
    Exposes tools for the planner to discover and select.
    """
    
    def __init__(self, registry: IntegrationRegistry):
        """
        Initialize planner interface.
        
        Args:
            registry: IntegrationRegistry instance
        """
        self.registry = registry
    
    def get_available_tools_for_planner(self) -> List[Dict[str, Any]]:
        """
        Get tools formatted for JARVIS Planner.
        
        Returns:
            List of tool specs
        """
        return self.registry.list_all_tools()
    
    def find_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Find tool by name (searches across integrations).
        
        Args:
            tool_name: Tool name (can include integration prefix)
            
        Returns:
            Tool definition
        """
        if "." in tool_name:
            return self.registry.get_tool_by_id(tool_name)
        
        # Search for tool name across all integrations
        for tool in self.registry.list_all_tools():
            if tool["name"] == tool_name:
                return tool
        
        return None
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get tools by category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tools
        """
        all_tools = self.registry.list_all_tools()
        return [t for t in all_tools if t.get("category") == category]


class ExecutorExecutionInterface:
    """
    Interface between IntegrationRegistry and JARVIS Executor.
    
    Handles tool execution with error handling and result tracking.
    """
    
    def __init__(self, registry: IntegrationRegistry):
        """
        Initialize executor interface.
        
        Args:
            registry: IntegrationRegistry instance
        """
        self.registry = registry
    
    async def execute(self, tool_id: str, **parameters) -> Any:
        """
        Execute a tool.
        
        Args:
            tool_id: Tool ID (integration.tool)
            **parameters: Tool parameters
            
        Returns:
            Tool result
        """
        if "." not in tool_id:
            raise IntegrationError(f"Invalid tool ID: {tool_id}. Expected format: integration.tool")
        
        integration_name, tool_name = tool_id.split(".", 1)
        
        return await self.registry.execute_tool(
            integration_name,
            tool_name,
            **parameters
        )


class OrchestratorBridge:
    """
    Main bridge between JARVIS orchestrator and integrations.
    
    Coordinates tool discovery, planning, and execution.
    """
    
    def __init__(self, workflow_engine: WorkflowEngine = None,
                 auth_manager: AuthManager = None):
        """
        Initialize orchestrator bridge.
        
        Args:
            workflow_engine: WorkflowEngine instance
            auth_manager: AuthManager instance
        """
        self.event_bus = EventBus()
        self.registry = IntegrationRegistry(event_bus=self.event_bus)
        self.planner_interface = PlannerToolInterface(self.registry)
        self.executor_interface = ExecutorExecutionInterface(self.registry)
        
        self.workflow_engine = workflow_engine
        self.auth_manager = auth_manager
    
    def register_all_integrations(self, integrations: List[BaseIntegration]) -> None:
        """
        Register multiple integrations.
        
        Args:
            integrations: List of integration instances
        """
        for integration in integrations:
            self.registry.register_integration(integration)
    
    async def tool_discovery(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover all available tools (for Planner).
        
        Returns:
            Nested dict of tools by integration
        """
        discovered = {}
        for name, integration in self.registry.integrations.items():
            tools = []
            for tool in integration.get_tools():
                tools.append({
                    "id": f"{name}.{tool.name}",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                    "returns": tool.returns
                })
            discovered[name] = tools
        
        return discovered
    
    async def plan_with_tools(self, objective: str) -> List[Dict[str, Any]]:
        """
        Get available tools for planning.
        
        This would integrate with JARVIS Planner to generate action plans.
        
        Args:
            objective: High-level objective
            
        Returns:
            List of recommended tools
        """
        print(f"📋 Planning for objective: {objective}\n")
        
        available_tools = self.planner_interface.get_available_tools_for_planner()
        
        print(f"✅ Found {len(available_tools)} available tools:")
        for tool in available_tools[:5]:
            print(f"   • {tool['id']}: {tool['description']}")
        
        if len(available_tools) > 5:
            print(f"   ... and {len(available_tools) - 5} more")
        
        return available_tools
    
    async def execute_plan(self, actions: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute a plan (multiple actions).
        
        Args:
            actions: List of actions with tool_id and parameters
            
        Returns:
            List of results
        """
        results = []
        
        for i, action in enumerate(actions, 1):
            tool_id = action.get("tool_id")
            parameters = action.get("parameters", {})
            
            print(f"\n[{i}/{len(actions)}] Executing: {tool_id}")
            
            try:
                result = await self.executor_interface.execute(tool_id, **parameters)
                results.append({
                    "action": tool_id,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "action": tool_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get bridge diagnostics."""
        return {
            "registry_stats": self.registry.get_stats(),
            "total_tools_available": len(self.planner_interface.get_available_tools_for_planner()),
            "execution_history_size": len(self.registry.execution_log),
            "event_history_size": len(self.event_bus.history)
        }


# Example usage and setup
if __name__ == "__main__":
    import asyncio
    
    async def test_orchestrator_bridge():
        print("🧪 Orchestrator Bridge Test\n")
        
        # Create bridge
        bridge = OrchestratorBridge()
        
        # In real setup, would register all integrations:
        # from . import email, calendar, github, slack, notion, iot
        # bridge.register_all_integrations([
        #     email.EmailIntegration(),
        #     calendar.CalendarIntegration(),
        #     github.GitHubIntegration(),
        #     slack.SlackIntegration(),
        #     notion.NotionIntegration(),
        #     iot.IoTIntegration(),
        # ])
        
        print("🔍 Tool Discovery:\n")
        tools = await bridge.tool_discovery()
        print(f"✅ Would discover tools from: {list(tools.keys())}")
        
        print(f"\n📊 Diagnostics:")
        diag = bridge.get_diagnostics()
        for key, value in diag.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for k, v in value.items():
                    print(f"     {k}: {v}")
            else:
                print(f"   {key}: {value}")
    
    asyncio.run(test_orchestrator_bridge())
