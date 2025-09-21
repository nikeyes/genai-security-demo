import json
from typing import Dict, List, Any
from .tool_system import ToolAdapter, ToolSpec, ToolResult


class BedrockToolAdapter(ToolAdapter):
    """Tool adapter for AWS Bedrock Converse API."""

    def convert_tools(self, tools: List[ToolSpec]) -> List[Dict[str, Any]]:
        """Convert ToolSpec to Bedrock toolSpec format."""
        bedrock_tools = []
        for tool in tools:
            bedrock_tool = {
                'toolSpec': {
                    'name': tool.name,
                    'description': tool.description,
                    'inputSchema': {'json': {'type': 'object', 'properties': tool.parameters, 'required': tool.required}},
                }
            }
            bedrock_tools.append(bedrock_tool)
        return bedrock_tools

    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from Bedrock response."""
        message_content = response['output']['message']['content']
        tool_calls = []

        for block in message_content:
            if block.get('toolUse'):
                tool_use = block['toolUse']
                tool_calls.append({'tool_use_id': tool_use['toolUseId'], 'tool_name': tool_use['name'], 'tool_input': tool_use['input']})

        return tool_calls

    def format_tool_results(self, results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format tool results for Bedrock."""
        formatted_results = []
        for result in results:
            formatted_results.append({'toolResult': {'toolUseId': result.tool_use_id, 'content': [{'text': result.content}]}})
        return formatted_results

    def supports_tools(self) -> bool:
        return True


class OpenAIToolAdapter(ToolAdapter):
    """Tool adapter for OpenAI function calling."""

    def convert_tools(self, tools: List[ToolSpec]) -> List[Dict[str, Any]]:
        """Convert ToolSpec to OpenAI function format."""
        openai_tools = []
        for tool in tools:
            openai_tool = {
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': {'type': 'object', 'properties': tool.parameters, 'required': tool.required},
                },
            }
            openai_tools.append(openai_tool)
        return openai_tools

    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from OpenAI response."""
        tool_calls = []
        message = response.choices[0].message

        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(
                    {
                        'tool_use_id': tool_call.id,
                        'tool_name': tool_call.function.name,
                        'tool_input': json.loads(tool_call.function.arguments),
                    }
                )

        return tool_calls

    def format_tool_results(self, results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format tool results for OpenAI."""
        messages = []
        for result in results:
            messages.append({'tool_call_id': result.tool_use_id, 'role': 'tool', 'content': result.content})
        return messages

    def supports_tools(self) -> bool:
        return True


class GroqToolAdapter(ToolAdapter):
    """Tool adapter for Groq function calling."""

    def convert_tools(self, tools: List[ToolSpec]) -> List[Dict[str, Any]]:
        """Convert ToolSpec to Groq function format."""
        groq_tools = []
        for tool in tools:
            groq_tool = {
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': {'type': 'object', 'properties': tool.parameters, 'required': tool.required},
                },
            }
            groq_tools.append(groq_tool)
        return groq_tools

    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from Groq response."""
        tool_calls = []
        message = response.choices[0].message

        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(
                    {
                        'tool_use_id': tool_call.id,
                        'tool_name': tool_call.function.name,
                        'tool_input': json.loads(tool_call.function.arguments),
                    }
                )

        return tool_calls

    def format_tool_results(self, results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format tool results for Groq."""
        messages = []
        for result in results:
            messages.append({'tool_call_id': result.tool_use_id, 'role': 'tool', 'content': result.content})
        return messages

    def supports_tools(self) -> bool:
        return True


class NoOpToolAdapter(ToolAdapter):
    """Tool adapter for providers that don't support tools."""

    def convert_tools(self, tools: List[ToolSpec]) -> List[Dict[str, Any]]:
        """Return empty list since this provider doesn't support tools."""
        return []

    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Return empty list since this provider doesn't support tools."""
        return []

    def format_tool_results(self, results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Return empty list since this provider doesn't support tools."""
        return []

    def supports_tools(self) -> bool:
        """This adapter doesn't support tools."""
        return False
