import boto3
from botocore.config import Config

from .base_provider import BaseProvider
from .token_usage import TokenUsage
from .tool_adapters import BedrockToolAdapter
from .tool_system import ToolResult


class BedrockConverseProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False, tools=None):
        tool_specs = tools or []
        super().__init__('Bedrock-Claude-Converse', model_id, debug, tool_specs)
        # Configure timeout to prevent hanging
        config = Config(read_timeout=30, connect_timeout=10, retries={'max_attempts': 2})
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1', config=config)

    def _create_tool_adapter(self) -> BedrockToolAdapter:
        """Create Bedrock tool adapter."""
        return BedrockToolAdapter()

    def invoke(self, system_prompt: str, user_prompt: str, tool_handler=None, messages=None):
        if self.is_empty(user_prompt) and not messages:
            return ' '

        messages = self._prepare_messages(user_prompt, messages)
        params = self._build_converse_params(system_prompt, messages)

        response = self.client.converse(**params)
        response = self._handle_tool_execution(response, tool_handler, messages, params)

        completion_text = self._extract_completion_text(response)
        usage = self._extract_token_usage(response)

        input_tokens = response['usage']['inputTokens']
        output_tokens = response['usage']['outputTokens']
        self.trace_invocation_result_with_tokens(input_tokens, output_tokens, completion_text)

        return completion_text, usage

    def _prepare_messages(self, user_prompt: str, messages: list) -> list:
        """Prepare messages for Converse API."""
        if messages is None:
            return [
                {
                    'role': 'user',
                    'content': [{'text': user_prompt}],
                }
            ]
        else:
            # When messages are provided, check if we need to add the current user_prompt
            if user_prompt and not self.is_empty(user_prompt):
                messages.append({'role': 'user', 'content': [{'text': user_prompt}]})
            return messages

    def _build_converse_params(self, system_prompt: str, messages: list) -> dict:
        """Build parameters for the Converse API call."""
        # System message configuration
        system_messages = []
        if system_prompt:
            system_messages = [{'text': system_prompt}]

        # Check if the conversation already has tool results that need processing
        has_tool_results = self._has_tool_results_in_conversation(messages)
        has_pending_tools = self._has_pending_tool_calls(messages)

        # Configure inference parameters
        inference_config = {
            'maxTokens': self.DEFAULT_MAX_TOKENS,
            'temperature': self.DEFAULT_TEMPERATURE,
            'topP': self.DEFAULT_TOP_P,
            'stopSequences': [seq.replace('\\', '') for seq in self.STOP_SEQUENCES],
        }

        # Configure tool config if tools are available OR if conversation has tool use/results
        tool_config = self._configure_tool_config(has_tool_results, has_pending_tools, messages)

        self.trace_invocation_info(None, self.model_id, {'messages': messages, 'system': system_messages, 'tools': tool_config})

        self.logger.debug('Conversation analysis: has_tool_results=%s, has_pending_tools=%s', has_tool_results, has_pending_tools)

        # Prepare converse parameters
        converse_params = {
            'modelId': self.model_id,
            'messages': messages,
            'system': system_messages,
            'inferenceConfig': inference_config,
        }

        if tool_config:
            converse_params['toolConfig'] = tool_config

        self.logger.debug('Sending converse_params: %s', converse_params)

        return converse_params

    def _configure_tool_config(self, has_tool_results: bool, has_pending_tools: bool, messages: list) -> dict:
        """Configure tool configuration for the API call."""
        tool_config = None
        if self.tools:
            bedrock_tools = self.tool_adapter.convert_tools(self.tools)
            tool_config = {'tools': bedrock_tools}
        elif has_tool_results or has_pending_tools:
            # If conversation has tool use/results but no tools configured, log warning
            self.logger.warning('Conversation contains tool usage but no tools configured')
        return tool_config

    def _handle_tool_execution(self, response, tool_handler, messages: list, params: dict):
        """Handle tool execution if tool calls are present in the response."""
        self.logger.debug('Initial response: %s', response)

        message_content = response['output']['message']['content']
        self.logger.debug('Initial message_content: %s', message_content)

        tool_calls = self.tool_adapter.extract_tool_calls(response)

        if tool_calls and tool_handler:
            # Process tool calls
            tool_results = []
            for tool_call in tool_calls:
                try:
                    result_content = tool_handler.execute_tool(tool_call['tool_name'], tool_call['tool_input'])
                    tool_result = ToolResult(tool_use_id=tool_call['tool_use_id'], content=str(result_content), success=True)
                except Exception as e:
                    tool_result = ToolResult(tool_use_id=tool_call['tool_use_id'], content=f'Error: {str(e)}', success=False, error=str(e))
                tool_results.append(tool_result)

            # Format tool results for Bedrock
            formatted_results = self.tool_adapter.format_tool_results(tool_results)

            # Send tool results back to get final response
            messages.append({'role': 'assistant', 'content': message_content})
            messages.append({'role': 'user', 'content': formatted_results})

            # Make another call with tool results
            params['messages'] = messages

            self.logger.debug('Sending follow-up converse_params: %s', params)

            response = self.client.converse(**params)

            self.logger.debug('Follow-up response: %s', response)

        return response

    def _extract_completion_text(self, response) -> str:
        """Extract text completion from the response."""
        message_content = response['output']['message']['content']
        self.logger.debug('Follow-up message_content: %s', message_content)

        # Extract text response
        completion_text = ''
        self.logger.debug('Processing message_content blocks: %s', message_content)

        for block in message_content:
            self.logger.debug('Processing block: %s', block)
            if 'text' in block:
                completion_text += block['text']
                self.logger.debug("Added text: '%s'", block['text'])

        # Handle empty responses with tool results
        completion_text = self._handle_empty_response_with_tools(completion_text, response)

        self.logger.debug("Final completion_text: '%s'", completion_text)

        return completion_text

    def _handle_empty_response_with_tools(self, completion_text: str, response) -> str:
        """Handle case where we get empty response but have tool results."""
        # This method would handle the empty response logic, but for now
        # we'll simplify and remove this complex fallback behavior
        # as it adds significant complexity without clear benefit
        return completion_text

    def _has_tool_results_in_conversation(self, messages):
        """Check if the conversation already contains tool results."""
        for message in messages:
            if message.get('role') == 'user':
                content = message.get('content', [])
                for block in content:
                    if 'toolResult' in block:
                        return True
        return False

    def _has_pending_tool_calls(self, messages):
        """Check if the conversation has tool calls that haven't been resolved."""
        last_assistant_message = None
        for message in reversed(messages):
            if message.get('role') == 'assistant':
                last_assistant_message = message
                break

        if not last_assistant_message:
            return False

        content = last_assistant_message.get('content', [])
        for block in content:
            if 'toolUse' in block:
                return True
        return False

    def _add_tool_conversation(self, messages, response, formatted_results):
        """Add tool conversation to messages (Bedrock-specific format)."""
        message_content = response['output']['message']['content']
        messages.append({'role': 'assistant', 'content': message_content})
        messages.append({'role': 'user', 'content': formatted_results})

    def _make_tool_followup_call(self, params):
        """Make follow-up call with tool results (Bedrock-specific)."""
        return self.client.converse(**params)

    def _extract_token_usage(self, response) -> TokenUsage:
        """Extract token usage from response."""
        return TokenUsage(input_tokens=response['usage']['inputTokens'], output_tokens=response['usage']['outputTokens'])
