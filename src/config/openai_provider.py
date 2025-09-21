from openai import OpenAI
from .base_provider import BaseProvider
from .token_usage import TokenUsage
from .tool_system import ToolResult
from .tool_adapters import OpenAICompatibleToolAdapter


class OpenAIProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False, tools=None):
        super().__init__('GPT4o-OpenAI', model_id, debug, tools)
        self.client = OpenAI()

    def _create_tool_adapter(self) -> OpenAICompatibleToolAdapter:
        """Create OpenAI-compatible tool adapter."""
        return OpenAICompatibleToolAdapter()

    def invoke(self, system_prompt: str, user_prompt: str, tool_handler=None):
        """Invoke OpenAI model with system and user prompts."""
        if self.is_empty(user_prompt):
            return ' '

        self.logger.debug('OpenAIProvider invoke...')

        messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]

        self.trace_invocation_info(user_prompt, self.model_id, messages)

        # Prepare parameters
        params = {
            'model': self.model_id,
            'messages': messages,
            'max_tokens': self.DEFAULT_MAX_TOKENS,
            'temperature': self.DEFAULT_TEMPERATURE,
            'top_p': self.DEFAULT_TOP_P,
            'stop': self.STOP_SEQUENCES,
        }

        # Add tools if available
        if self.tools:
            openai_tools = self.tool_adapter.convert_tools(self.tools)
            params['tools'] = openai_tools

        response = self.client.chat.completions.create(**params)

        # Handle tool calls if present
        response = self._execute_tools(response, tool_handler, messages, params)

        completion_text = response.choices[0].message.content
        self.trace_invocation_result_basic(completion_text, response.usage)

        usage = self._extract_token_usage(response)
        return completion_text, usage

    def _add_tool_conversation(self, messages, response, formatted_results):
        """Add tool conversation to messages (OpenAI format)."""
        messages.append(response.choices[0].message.model_dump())
        messages.extend(formatted_results)

    def _make_tool_followup_call(self, params):
        """Make follow-up call with tool results (OpenAI format)."""
        return self.client.chat.completions.create(**params)

    def _extract_token_usage(self, response):
        return TokenUsage(input_tokens=response.usage.prompt_tokens, output_tokens=response.usage.completion_tokens)
