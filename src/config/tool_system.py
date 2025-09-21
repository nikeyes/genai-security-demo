from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass


@dataclass
class ToolSpec:
    """Standard tool specification that works across all providers."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = None

    def __post_init__(self):
        if self.required is None:
            self.required = []


@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool_use_id: str
    content: str
    success: bool = True
    error: Optional[str] = None


class ToolHandler:
    """Standard tool handler that manages tool execution."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, handler: Callable):
        """Register a tool handler function."""
        self._tools[name] = handler

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool by name with given input."""
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        return self._tools[tool_name](tool_input)

    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools


class ToolAdapter(ABC):
    """Abstract base class for provider-specific tool adapters."""

    @abstractmethod
    def convert_tools(self, tools: List[ToolSpec]) -> List[Dict[str, Any]]:
        """Convert standard ToolSpec to provider-specific format."""
        pass

    @abstractmethod
    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from provider response."""
        pass

    @abstractmethod
    def format_tool_results(self, results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format tool results for provider."""
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if this provider supports tools."""
        pass