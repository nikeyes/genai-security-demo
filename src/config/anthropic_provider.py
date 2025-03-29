import anthropic
from .logger_config import setup_logger


class AnthropicProvider:
    def __init__(self, model_id: str, debug: bool = False):
        self.name = 'Anthropic-Claude'
        self.client = anthropic.Anthropic()
        self.model_id = model_id
        self.logger = setup_logger(__name__, debug)
        self.logger.debug('OpenAIWrapper initialized')

    @staticmethod
    def is_empty(s):
        return s.strip() == ''

    def invoke(self, system_prompt: str, user_prompt: str):
        """Invoke OpenAI model with system and user prompts."""
        if self.is_empty(user_prompt):
            return ' '

        print('AnthropicProvider invoke...')

        messages = [{'role': 'user', 'content': user_prompt}]

        self.trace_invocation_info(user_prompt, self.model_id, messages)

        response = self.client.messages.create(model=self.model_id, system=system_prompt, messages=messages, max_tokens=1000)

        self.trace_invocation_result(response)

        completion_text = response.content[0].text

        return completion_text

    def trace_invocation_info(self, user_prompt, model_id, messages):
        """Log debug information before the API call."""
        self.logger.debug('Invocation details:')
        self.logger.debug('model_id: %s', model_id)
        self.logger.debug('user prompt: %s', user_prompt)
        self.logger.debug('messages: %s', messages)

    def trace_invocation_result(self, response):
        """Log debug information after receiving the API response."""
        self.logger.debug('Response details:')
        self.logger.debug('- Completion text: %s', response.content[0].text)
        self.logger.debug('- Usage: %s', response.usage)
        self.logger.debug('Invocation completed.')
