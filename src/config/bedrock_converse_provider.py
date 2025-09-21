import boto3
from botocore.config import Config
from .base_provider import BaseProvider
from .token_usage import TokenUsage


class BedrockConverseProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False, tools: list = None):
        super().__init__('Bedrock-Claude-Converse', model_id, debug)
        # Configure timeout to prevent hanging
        config = Config(read_timeout=30, connect_timeout=10, retries={'max_attempts': 2})
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1', config=config)
        self.tools = tools or []

    def invoke(self, system_prompt: str, user_prompt: str, tool_handler=None):
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

        # Configure tool config if tools are available
        tool_config = None
        if self.tools:
            tool_config = {'tools': self.tools}

        self.trace_invocation_info(user_prompt, self.model_id, {'messages': messages, 'system': system_messages, 'tools': tool_config})

        # Prepare converse parameters
        converse_params = {
            'modelId': self.model_id,
            'messages': messages,
            'system': system_messages,
            'inferenceConfig': inference_config,
        }

        if tool_config:
            converse_params['toolConfig'] = tool_config

        # Use Converse API
        response = self.client.converse(**converse_params)

        # Handle tool use if present
        message_content = response['output']['message']['content']

        # Check if the response contains tool use
        tool_use_blocks = [block for block in message_content if block.get('toolUse')]
        if tool_use_blocks and tool_handler:
            # Process tool use
            tool_results = []
            for tool_block in tool_use_blocks:
                tool_use = tool_block['toolUse']
                tool_name = tool_use['name']
                tool_input = tool_use['input']
                tool_use_id = tool_use['toolUseId']

                # Call the tool handler
                tool_result = tool_handler(tool_name, tool_input)

                tool_results.append({'toolResult': {'toolUseId': tool_use_id, 'content': [{'text': str(tool_result)}]}})

            # Send tool results back to get final response
            messages.append({'role': 'assistant', 'content': message_content})
            messages.append({'role': 'user', 'content': tool_results})

            # Make another call with tool results
            converse_params['messages'] = messages
            response = self.client.converse(**converse_params)
            message_content = response['output']['message']['content']

        # Extract text response
        completion_text = ''
        for block in message_content:
            if 'text' in block:
                completion_text += block['text']

        input_tokens = response['usage']['inputTokens']
        output_tokens = response['usage']['outputTokens']
        self.trace_invocation_result_with_tokens(input_tokens, output_tokens, completion_text)

        usage = self._extract_token_usage(response)
        return completion_text, usage

    def _extract_token_usage(self, response):
        return TokenUsage(input_tokens=response['usage']['inputTokens'], output_tokens=response['usage']['outputTokens'])
