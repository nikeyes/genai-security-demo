import anthropic
from .base_provider import BaseProvider
from .token_usage import TokenUsage


class AnthropicProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False):
        super().__init__('Anthropic-Claude', model_id, debug)
        self.client = anthropic.Anthropic()

    def invoke(self, system_prompt: str, user_prompt: str):
        """Invoke Anthropic model with system and user prompts."""
        if self.is_empty(user_prompt):
            return ' '

        self.logger.debug('AnthropicProvider invoke...')

        messages = [{'role': 'user', 'content': user_prompt}]

        self.trace_invocation_info(user_prompt, self.model_id, messages)

        response = self.client.messages.create(
            model=self.model_id, 
            system=system_prompt, 
            messages=messages, 
            max_tokens=self.DEFAULT_MAX_TOKENS,
            temperature=self.DEFAULT_TEMPERATURE,
            top_p=self.DEFAULT_TOP_P,
            stop_sequences=self.STOP_SEQUENCES
        )

        completion_text = response.content[0].text
        self.trace_invocation_result_basic(completion_text, response.usage)
        
        usage = self._extract_token_usage(response)
        return completion_text, usage

    def _extract_token_usage(self, response):
        return TokenUsage(input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens, provider_name=self.name)
