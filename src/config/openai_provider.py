from openai import OpenAI
from .base_provider import BaseProvider
from .token_usage import TokenUsage


class OpenAIProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False):
        super().__init__('GPT4o-OpenAI', model_id, debug)
        self.client = OpenAI()

    def invoke(self, system_prompt: str, user_prompt: str):
        """Invoke OpenAI model with system and user prompts."""
        if self.is_empty(user_prompt):
            return ' '

        self.logger.debug('OpenAIProvider invoke...')

        messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]

        self.trace_invocation_info(user_prompt, self.model_id, messages)

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            max_tokens=self.DEFAULT_MAX_TOKENS,
            temperature=self.DEFAULT_TEMPERATURE,
            top_p=self.DEFAULT_TOP_P,
            stop=self.STOP_SEQUENCES,
        )

        completion_text = response.choices[0].message.content
        self.trace_invocation_result_basic(completion_text, response.usage)

        usage = self._extract_token_usage(response)
        return completion_text, usage

    def _extract_token_usage(self, response):
        return TokenUsage(input_tokens=response.usage.prompt_tokens, output_tokens=response.usage.completion_tokens)
