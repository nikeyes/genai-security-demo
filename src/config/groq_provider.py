from groq import Groq
from .logger_config import setup_logger
from .token_usage import TokenUsage


class GroqProvider:
    def __init__(self, model_id: str, debug: bool = False):
        self.name = 'Llama-Groq'
        self.client = Groq()
        self.model_id = model_id
        self.logger = setup_logger(__name__, debug)
        self.logger.debug('GroqWrapper initialized')

    @staticmethod
    def is_empty(s):
        return s.strip() == ''

    def invoke(self, system_prompt: str, user_prompt: str):
        """Invoke Groq model with system and user prompts."""
        if self.is_empty(user_prompt):
            return ' '

        print('GroqWrapper invoke...')

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]

        self.trace_invocation_info(user_prompt, self.model_id, messages)

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            max_completion_tokens=1024,
            temperature=0.5,
            top_p=1,
            stop=['\n\nHuman:', '\n\nAssistant', '</function_calls>'],
        )

        self.trace_invocation_result(response)

        completion_text = response.choices[0].message.content
        usage = self._extract_token_usage(response)

        return completion_text, usage

    def trace_invocation_info(self, user_prompt, model_id, messages):
        """Log debug information before the API call."""
        self.logger.debug('Invocation details:')
        self.logger.debug('model_id: %s', model_id)
        self.logger.debug('user prompt: %s', user_prompt)
        self.logger.debug('messages: %s', messages)

    def trace_invocation_result(self, response):
        """Log debug information after receiving the API response."""
        self.logger.debug('Response details:')
        self.logger.debug('- Completion text: %s', response.choices[0].message.content)
        self.logger.debug('Invocation completed.')

    def _extract_token_usage(self, response):
        return TokenUsage(
            input_tokens=response.usage.prompt_tokens, output_tokens=response.usage.completion_tokens, provider_name=self.name
        )
