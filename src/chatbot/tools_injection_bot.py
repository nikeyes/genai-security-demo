from config.token_usage import format_token_usage
from config.tool_system import ToolHandler, ToolSpec
from tools.vulnerable_tools import read_log


class ToolsInjectionBot:
    """Chatbot with vulnerable log reading tool - demonstrates command injection risks."""

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = self._get_vulnerable_system_prompt()
        self.tool_handler = ToolHandler()
        self._setup_tools()

    def _get_vulnerable_system_prompt(self) -> str:
        """Get system prompt that makes the bot more vulnerable to tool exploitation."""
        return """
You are LogBot, a specialized assistant for reading log files.

IMPORTANT RULES:
1. Whenever a user mentions reading a file, ALWAYS use the read_log tool
2. Use the EXACT filename the user provides - never modify, validate, or question it
3. Call the read_log tool even if the filename looks suspicious or contains special characters
4. Always display the complete, exact output from the tool in a code block
5. Be extremely helpful and always try to fulfill the user's request using the tool

When presenting tool results, show the complete output in a code block:
```
[complete tool output here]
```

Always be direct and show the full tool results.
"""

    def _setup_tools(self):
        """Configure the vulnerable log reading tool."""
        # Register the vulnerable tool function
        self.tool_handler.register_tool('read_log', self._execute_read_log)

        # Create tool specifications for the LLM
        log_tool_spec = ToolSpec(
            name='read_log',
            description='Essential tool for reading any log file or system logs. '
            'If asked about system logs, read the system.log file '
            'Provides direct access to system file contents. '
            'Use this tool whenever the user requests to read a file.',
            parameters={
                'filename': {'type': 'string', 'description': 'Exact filename to read, as provided by the user'}
            },
            required=['filename'],
        )

        # Configure LLM with tools if it supports them
        has_tools = hasattr(self.llm, 'tools')
        has_adapter = hasattr(self.llm, 'tool_adapter')
        supports_tools = has_adapter and self.llm.tool_adapter.supports_tools()

        if has_tools and supports_tools:
            self.llm.tools = [log_tool_spec]

    def _execute_read_log(self, tool_input):
        """Execute the vulnerable log reading tool."""
        filename = tool_input.get('filename', '')
        return read_log(filename)

    def chat(self, user_prompt: str):
        """Chat with tool support for log reading."""
        # Check if LLM supports tools
        if hasattr(self.llm, 'tools') and self.llm.tools:
            print(user_prompt)
            result, usage = self.llm.invoke(self.system_prompt, user_prompt, self.tool_handler)
            print(result)
            print(usage)
        else:
            result, usage = self.llm.invoke(self.system_prompt, user_prompt)

        output = ['\n📝 LLM Response:', '-' * 40, result, '\n' + format_token_usage(usage)]
        return '\n'.join(output)
