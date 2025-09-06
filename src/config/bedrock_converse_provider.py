import boto3
from botocore.config import Config
from .base_provider import BaseProvider
from .token_usage import TokenUsage


class BedrockConverseProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False):
        super().__init__('Bedrock-Claude-Converse', model_id, debug)
        # Configure timeout to prevent hanging
        config = Config(
            read_timeout=30,
            connect_timeout=10,
            retries={'max_attempts': 2}
        )
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1', config=config)

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
            'maxTokens': self.DEFAULT_MAX_TOKENS,
            'temperature': self.DEFAULT_TEMPERATURE,
            'topP': self.DEFAULT_TOP_P,
            'stopSequences': [seq.replace('\\', '') for seq in self.STOP_SEQUENCES],
        }

        self.trace_invocation_info(user_prompt, self.model_id, {'messages': messages, 'system': system_messages})

        # Use Converse API
        response = self.client.converse(
            modelId=self.model_id,
            messages=messages,
            system=system_messages,
            inferenceConfig=inference_config,
        )

        completion_text = response['output']['message']['content'][0]['text']

        input_tokens = response['usage']['inputTokens']
        output_tokens = response['usage']['outputTokens']
        self.trace_invocation_result_with_tokens(input_tokens, output_tokens, completion_text)

        usage = self._extract_token_usage(response)
        return completion_text, usage

    def _extract_token_usage(self, response):
        return TokenUsage(
            input_tokens=response['usage']['inputTokens'], output_tokens=response['usage']['outputTokens'], provider_name=self.name
        )
