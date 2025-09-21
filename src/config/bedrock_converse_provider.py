import boto3
from botocore.config import Config
from .base_provider import BaseProvider
from .token_usage import TokenUsage
from .tool_system import ToolSpec, ToolResult
from .tool_adapters import BedrockToolAdapter


class BedrockConverseProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False, tools=None):
        # Handle both ToolSpec objects and legacy Bedrock format
        if tools:
            if isinstance(tools[0], ToolSpec):
                tool_specs = tools
            else:
                tool_specs = self._convert_legacy_tools(tools)
        else:
            tool_specs = []
        super().__init__('Bedrock-Claude-Converse', model_id, debug, tool_specs)
        # Configure timeout to prevent hanging
        config = Config(read_timeout=30, connect_timeout=10, retries={'max_attempts': 2})
        self.client = boto3.client(service_name='bedrock-runtime',
                                   region_name='eu-central-1', config=config)

    def _create_tool_adapter(self) -> BedrockToolAdapter:
        """Create Bedrock tool adapter."""
        return BedrockToolAdapter()

    def _convert_legacy_tools(self, legacy_tools):
        """Convert legacy Bedrock tools format to ToolSpec."""
        tool_specs = []
        for tool in legacy_tools:
            tool_spec = tool['toolSpec']
            spec = ToolSpec(
                name=tool_spec['name'],
                description=tool_spec['description'],
                parameters=tool_spec['inputSchema']['json']['properties'],
                required=tool_spec['inputSchema']['json'].get('required', [])
            )
            tool_specs.append(spec)
        return tool_specs

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
            bedrock_tools = self.tool_adapter.convert_tools(self.tools)
            tool_config = {'tools': bedrock_tools}

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

            # Format tool results for Bedrock
            formatted_results = self.tool_adapter.format_tool_results(tool_results)

            # Send tool results back to get final response
            messages.append({'role': 'assistant', 'content': message_content})
            messages.append({'role': 'user', 'content': formatted_results})

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
