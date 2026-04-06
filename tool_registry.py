"""
JARVIS Tool Registry System
Manages all tools available to the agent
"""

from typing import Dict, Any, Callable, Optional, List, Union
from dataclasses import dataclass
import inspect
from datetime import datetime

@dataclass
class ToolSchema:
    """Schema for a tool"""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema
    required: List[str]
    returns: str
    category: str  # web, file, app, task, etc.


class ToolRegistry:
    """Registry of all tools available to the agent"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.schemas: Dict[str, ToolSchema] = {}
        self.call_history: List[Dict] = []
    
    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        required: List[str],
        returns: str,
        category: str = "general"
    ):
        """
        Register a tool
        
        Args:
            name: Tool name
            func: Function to call
            description: What it does
            parameters: Input schema
            required: Required parameters
            returns: Output description
            category: Tool category
        """
        self.tools[name] = {
            "func": func,
            "description": description,
            "parameters": parameters,
            "required": required,
            "returns": returns,
            "category": category,
            "calls": 0,
            "errors": 0
        }
        
        # Store schema
        self.schemas[name] = ToolSchema(
            name=name,
            description=description,
            parameters=parameters,
            required=required,
            returns=returns,
            category=category
        )
        
        print(f"✅ Registered tool: {name}")
    
    def call_tool(self, tool_name: str, **kwargs) -> Union[Any, tuple]:
        """
        Call a tool with parameters
        
        Args:
            tool_name: Name of tool to call
            **kwargs: Tool parameters
            
        Returns:
            (success, result) tuple
        """
        if tool_name not in self.tools:
            return False, f"❌ Tool not found: {tool_name}"
        
        tool = self.tools[tool_name]
        func = tool["func"]
        
        # Validate required parameters
        for req_param in tool["required"]:
            if req_param not in kwargs:
                return False, f"❌ Missing required parameter: {req_param}"
        
        try:
            print(f"🔧 Calling tool: {tool_name}")
            print(f"   Parameters: {kwargs}")
            
            # Call the tool
            result = func(**kwargs)
            
            # Log call
            self.tools[tool_name]["calls"] += 1
            self.call_history.append({
                "tool": tool_name,
                "params": kwargs,
                "success": True,
                "result": str(result)[:200],  # Store first 200 chars
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ Tool succeeded")
            return True, result
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Tool error: {error_msg}")
            
            # Log error
            self.tools[tool_name]["errors"] += 1
            self.call_history.append({
                "tool": tool_name,
                "params": kwargs,
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            
            return False, error_msg
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get information about a tool"""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        schema = self.schemas[tool_name]
        
        return {
            "name": tool_name,
            "description": tool["description"],
            "category": tool["category"],
            "parameters": tool["parameters"],
            "required": tool["required"],
            "returns": tool["returns"],
            "stats": {
                "calls": tool["calls"],
                "errors": tool["errors"],
                "success_rate": (tool["calls"] - tool["errors"]) / max(1, tool["calls"]) if tool["calls"] > 0 else 0
            }
        }
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get all tools in a category"""
        return [name for name, tool in self.tools.items() if tool["category"] == category]
    
    def list_tools(self, categories: Optional[List[str]] = None) -> str:
        """List available tools"""
        result = "🔧 Available Tools:\n\n"
        
        # Group by category
        categories_list = categories or list(set(t["category"] for t in self.tools.values()))
        
        for cat in categories_list:
            tools_in_cat = self.get_tools_by_category(cat)
            if tools_in_cat:
                result += f"{cat.upper()}:\n"
                for tool_name in tools_in_cat:
                    info = self.get_tool_info(tool_name)
                    result += f"  • {tool_name}: {info['description']}\n"
                result += "\n"
        
        return result
    
    def get_call_history(self, limit: int = 10) -> List[Dict]:
        """Get recent tool calls"""
        return self.call_history[-limit:]
    
    def get_tool_stats(self) -> Dict:
        """Get statistics about tool usage"""
        stats = {
            "total_tools": len(self.tools),
            "total_calls": sum(t["calls"] for t in self.tools.values()),
            "total_errors": sum(t["errors"] for t in self.tools.values()),
            "tools_by_category": {},
            "most_used": [],
            "most_errors": []
        }
        
        # Category breakdown
        for cat in set(t["category"] for t in self.tools.values()):
            tools_in_cat = self.get_tools_by_category(cat)
            calls = sum(self.tools[t]["calls"] for t in tools_in_cat)
            stats["tools_by_category"][cat] = {"count": len(tools_in_cat), "calls": calls}
        
        # Most used tools
        sorted_tools = sorted(
            self.tools.items(),
            key=lambda x: x[1]["calls"],
            reverse=True
        )
        stats["most_used"] = [
            {"name": name, "calls": tool["calls"]}
            for name, tool in sorted_tools[:5]
        ]
        
        # Most errors
        sorted_errors = sorted(
            self.tools.items(),
            key=lambda x: x[1]["errors"],
            reverse=True
        )
        stats["most_errors"] = [
            {"name": name, "errors": tool["errors"]}
            for name, tool in sorted_errors[:5]
            if tool["errors"] > 0
        ]
        
        return stats
    
    def clear_history(self):
        """Clear call history"""
        self.call_history = []
        print("✅ History cleared")
    
    def reset_statistics(self):
        """Reset all tool statistics"""
        for tool in self.tools.values():
            tool["calls"] = 0
            tool["errors"] = 0
        self.call_history = []
        print("✅ Statistics reset")
    
    def suggest_tool(self, task_description: str) -> Optional[str]:
        """Suggest a tool for a task (simple heuristic)"""
        from brain import JarvisBrain
        
        task_desc_lower = task_description.lower()
        
        # Simple heuristic-based suggestions
        if any(x in task_desc_lower for x in ["search", "find", "look", "research"]):
            return "search_web"
        elif any(x in task_desc_lower for x in ["write", "save", "create", "note"]):
            return "write_file"
        elif any(x in task_desc_lower for x in ["read", "open", "view", "load"]):
            return "read_file"
        elif any(x in task_desc_lower for x in ["summarize", "condense", "brief"]):
            return "summarize_text"
        elif any(x in task_desc_lower for x in ["open", "launch", "start", "run"]):
            return "open_app"
        
        # Default: use AI for suggestion
        try:
            brain = JarvisBrain()
            prompt = f"""Given this task, which tool would be best?

Task: {task_description}

Available tools: {', '.join(self.tools.keys())}

Respond with ONLY the tool name, no explanation."""
            
            suggestion = brain.query(prompt)
            tool_name = suggestion.strip().lower()
            
            if tool_name in self.tools:
                return tool_name
        except:
            pass
        
        return None
