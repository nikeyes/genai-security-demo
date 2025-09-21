from groq import Groq
from .base_provider import BaseProvider
from .token_usage import TokenUsage
from .tool_system import ToolResult
from .tool_adapters import GroqToolAdapter


class GroqProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False, tools=None):
        super().__init__('Llama-Groq', model_id, debug, tools)
        self.client = Groq()

    def _create_tool_adapter(self) -> GroqToolAdapter:
        """Create Groq tool adapter."""
        return GroqToolAdapter()

    def invoke(self, system_prompt: str, user_prompt: str, tool_handler=None):
        """Invoke Groq model with system and user prompts."""
        if self.is_empty(user_prompt):
            return ' '

        self.logger.debug('GroqProvider invoke...')

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]

        self.trace_invocation_info(user_prompt, self.model_id, messages)

        # Prepare parameters
        params = {
            'model': self.model_id,
            'messages': messages,
            'max_completion_tokens': self.DEFAULT_MAX_TOKENS,
            'temperature': self.DEFAULT_TEMPERATURE,
            'top_p': self.DEFAULT_TOP_P,
            'stop': self.STOP_SEQUENCES,
        }

        # Add tools if available
        if self.tools:
            groq_tools = self.tool_adapter.convert_tools(self.tools)
            params['tools'] = groq_tools

        response = self.client.chat.completions.create(**params)

        # Handle tool calls if present
        tool_calls = self.tool_adapter.extract_tool_calls(response)
        if tool_calls and tool_handler:
            # Process tool calls
            tool_results = []
            for tool_call in tool_calls:
                try:
                    result_content = tool_handler.execute_tool(
                        tool_call['tool_name'], tool_call['tool_input']
                    )
                    tool_result = ToolResult(
                        tool_use_id=tool_call['tool_use_id'],
                        content=str(result_content),
                        success=True
                    )
                except Exception as e:
                    tool_result = ToolResult(
                        tool_use_id=tool_call['tool_use_id'],
                        content=f"Error: {str(e)}",
                        success=False,
                        error=str(e)
                    )
                tool_results.append(tool_result)

            # Add assistant message and tool results
            messages.append(response.choices[0].message.model_dump())
            tool_messages = self.tool_adapter.format_tool_results(tool_results)
            messages.extend(tool_messages)

            # Make another call with tool results
            params['messages'] = messages
            response = self.client.chat.completions.create(**params)

        completion_text = response.choices[0].message.content
        self.trace_invocation_result_basic(completion_text)

        usage = self._extract_token_usage(response)
        return completion_text, usage

    def _extract_token_usage(self, response):
        return TokenUsage(input_tokens=response.usage.prompt_tokens, output_tokens=response.usage.completion_tokens)
