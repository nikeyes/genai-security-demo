from abc import ABC, abstractmethod
from .logger_config import setup_logger


class BaseProvider(ABC):
    """Base class for all LLM providers. Eliminates code duplication."""
    
    # Common constants
    STOP_SEQUENCES = ['\n\nHuman:', '\n\nAssistant', '</function_calls>']
    DEFAULT_MAX_TOKENS = 1024
    DEFAULT_TEMPERATURE = 0.5
    DEFAULT_TOP_P = 1.0

    def __init__(self, name: str, model_id: str, debug: bool = False):
        self.name = name
        self.model_id = model_id
        self.logger = setup_logger(__name__, debug)
        self.logger.debug(f'{self.__class__.__name__} initialized')

    @staticmethod
    def is_empty(s):
        """Check if string is empty or whitespace only."""
        return s.strip() == ''

    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str):
        """Invoke the provider with system and user prompts."""
        pass

    def trace_invocation_info(self, user_prompt, model_id, messages_or_body):
        """Log debug information before the API call."""
        self.logger.debug('Invocation details:')
        self.logger.debug('model_id: %s', model_id)
        self.logger.debug('user prompt: %s', user_prompt)
        self.logger.debug('messages/body: %s', messages_or_body)

    def trace_invocation_result_basic(self, response_text, usage_info=None):
        """Log basic invocation result."""
        self.logger.debug('Response details:')
        self.logger.debug('- Completion text: %s', response_text)
        if usage_info:
            self.logger.debug('- Usage: %s', usage_info)
        self.logger.debug('Invocation completed.')

    def trace_invocation_result_with_tokens(self, input_tokens, output_tokens, response_text):
        """Log invocation result with token details."""
        self.logger.debug('Response details:')
        self.logger.debug('- Input tokens: %s', input_tokens)
        self.logger.debug('- Output tokens: %s', output_tokens)  
        self.logger.debug('- Completion text: %s', response_text)
        self.logger.debug('Invocation completed.')

    @abstractmethod
    def _extract_token_usage(self, response):
        """Extract token usage from the provider response."""
        pass