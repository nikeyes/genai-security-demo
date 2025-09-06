import boto3

from .logger_config import setup_logger
from .token_usage import TokenUsage


class BedrockConverseProvider:
    def __init__(self, model_id: str, debug: bool = False):
        self.name = 'Bedrock-Claude-Converse'
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1')
        self.model_id = model_id
        self.logger = setup_logger(__name__, debug)
        self.logger.debug('BedrockConverseProvider initialized')

    @staticmethod
    def is_empty(s):
        return s.strip() == ''

    def invoke(self, system_prompt: str, user_prompt: str):
        if self.is_empty(user_prompt):
            return ' '

        # Prepare messages for Converse API
        messages = [
            {
                'role': 'user',
                'content': [{'text': user_prompt}],
            }
        ]

        # System message configuration
        system_messages = []
        if system_prompt:
            system_messages = [{'text': system_prompt}]

        # Configure inference parameters
        inference_config = {
            'maxTokens': 1024,
            'temperature': 0.7,
            'topP': 0.9,
            'stopSequences': ['\\n\\nHuman:', '\\n\\nAssistant', '</function_calls>'],
        }

        self.trace_invocation_info(user_prompt, self.model_id, messages, system_messages)

        # Use Converse API
        response = self.client.converse(
            modelId=self.model_id,
            messages=messages,
            system=system_messages,
            inferenceConfig=inference_config,
        )

        self.trace_invocation_result(response)

        completion_text = response['output']['message']['content'][0]['text']
        usage = self._extract_token_usage(response)

        return completion_text, usage

    def trace_invocation_info(self, user_prompt, model_id, messages, system_messages):
        self.logger.debug('Invocation details:')
        self.logger.debug('model_id: %s', model_id)
        self.logger.debug('user prompt: %s', user_prompt)
        self.logger.debug('messages: %s', messages)
        self.logger.debug('system_messages: %s', system_messages)

    def trace_invocation_result(self, response):
        input_tokens = response['usage']['inputTokens']
        output_tokens = response['usage']['outputTokens']
        self.logger.debug('Response details:')
        self.logger.debug('- Input tokens: %s', input_tokens)
        self.logger.debug('- Output tokens: %s', output_tokens)
        self.logger.debug('- Completion text: %s', response['output']['message']['content'][0]['text'])
        self.logger.debug('Invocation completed.')

    def _extract_token_usage(self, response):
        return TokenUsage(
            input_tokens=response['usage']['inputTokens'], output_tokens=response['usage']['outputTokens'], provider_name=self.name
        )
