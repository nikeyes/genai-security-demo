import boto3
from botocore.config import Config

from .base_provider import BaseProvider
from .token_usage import TokenUsage
from .tool_adapters import BedrockToolAdapter
from .tool_system import ToolResult, ToolSpec


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
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1', config=config)

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
                required=tool_spec['inputSchema']['json'].get('required', []),
            )
            tool_specs.append(spec)
        return tool_specs

    def invoke(self, system_prompt: str, user_prompt: str, tool_handler=None, messages=None):
        if self.is_empty(user_prompt) and not messages:
            return ' '

        # Prepare messages for Converse API
        if messages is None:
            messages = [
                {
                    'role': 'user',
                    'content': [{'text': user_prompt}],
                }
            ]
        else:
            # When messages are provided, check if we need to add the current user_prompt
            if user_prompt and not self.is_empty(user_prompt):
                messages.append({'role': 'user', 'content': [{'text': user_prompt}]})

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
        tool_config = None
        if self.tools:
            bedrock_tools = self.tool_adapter.convert_tools(self.tools)
            tool_config = {'tools': bedrock_tools}
        elif has_tool_results or has_pending_tools:
            # Even if no tools are configured, we need tool_config if conversation has tool use/results
            # We'll try to infer the tool definitions from the conversation
            inferred_tools = self._infer_tools_from_conversation(messages)
            if inferred_tools:
                tool_config = {'tools': inferred_tools}
                if self.debug:
                    print(f'[DEBUG] Inferred tools from conversation: {tool_config}')

        self.trace_invocation_info(user_prompt, self.model_id, {'messages': messages, 'system': system_messages, 'tools': tool_config})

        if self.debug:
            print(f'[DEBUG] Conversation analysis: has_tool_results={has_tool_results}, has_pending_tools={has_pending_tools}')

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
        if self.debug:
            print(f'[DEBUG] Sending converse_params: {converse_params}')

        response = self.client.converse(**converse_params)

        if self.debug:
            print(f'[DEBUG] Initial response: {response}')

        # Handle tool use if present
        message_content = response['output']['message']['content']
        if self.debug:
            print(f'[DEBUG] Initial message_content: {message_content}')
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
            converse_params['messages'] = messages

            if self.debug:
                print(f'[DEBUG] Sending follow-up converse_params: {converse_params}')

            response = self.client.converse(**converse_params)

            if self.debug:
                print(f'[DEBUG] Follow-up response: {response}')

            message_content = response['output']['message']['content']
            if self.debug:
                print(f'[DEBUG] Follow-up message_content: {message_content}')

        # Extract text response
        completion_text = ''
        if self.debug:
            print(f'[DEBUG] Processing message_content blocks: {message_content}')

        for block in message_content:
            if self.debug:
                print(f'[DEBUG] Processing block: {block}')
            if 'text' in block:
                completion_text += block['text']
                if self.debug:
                    print(f"[DEBUG] Added text: '{block['text']}'")

        # If we got empty completion_text and the conversation has tool results,
        # it might mean the model considers the conversation complete
        if not completion_text.strip() and has_tool_results:
            if self.debug:
                print('[DEBUG] Empty response with tool results - model may consider conversation complete')
            # Try adding a prompt to encourage the model to respond
            follow_up_messages = messages.copy()
            follow_up_messages.append({'role': 'user', 'content': [{'text': 'Please provide a response based on the tool results above.'}]})

            follow_up_params = converse_params.copy()
            follow_up_params['messages'] = follow_up_messages

            if self.debug:
                print(f'[DEBUG] Sending follow-up request: {follow_up_params}')

            follow_up_response = self.client.converse(**follow_up_params)

            if self.debug:
                print(f'[DEBUG] Follow-up response: {follow_up_response}')

            follow_up_content = follow_up_response['output']['message']['content']
            if self.debug:
                print(f'[DEBUG] Follow-up message_content: {follow_up_content}')

            # Extract text from follow-up response
            for block in follow_up_content:
                if 'text' in block:
                    completion_text += block['text']
                    if self.debug:
                        print(f"[DEBUG] Added follow-up text: '{block['text']}'")

            # Update response for token counting
            response = follow_up_response

        if self.debug:
            print(f"[DEBUG] Final completion_text: '{completion_text}'")

        input_tokens = response['usage']['inputTokens']
        output_tokens = response['usage']['outputTokens']
        self.trace_invocation_result_with_tokens(input_tokens, output_tokens, completion_text)

        usage = self._extract_token_usage(response)
        return completion_text, usage

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

    def _infer_tools_from_conversation(self, messages):
        """Infer tool definitions from conversation toolUse blocks."""
        tools = []
        seen_tools = set()

        for message in messages:
            if message.get('role') == 'assistant':
                content = message.get('content', [])
                for block in content:
                    if 'toolUse' in block:
                        tool_use = block['toolUse']
                        tool_name = tool_use.get('name')

                        if tool_name and tool_name not in seen_tools:
                            # Create a basic tool definition
                            tool_input = tool_use.get('input', {})
                            properties = {}
                            required = []

                            # Infer properties from the input
                            for key, value in tool_input.items():
                                if isinstance(value, str):
                                    properties[key] = {'type': 'string'}
                                elif isinstance(value, (int, float)):
                                    properties[key] = {'type': 'number'}
                                elif isinstance(value, bool):
                                    properties[key] = {'type': 'boolean'}
                                else:
                                    properties[key] = {'type': 'string'}
                                required.append(key)

                            tool_spec = {
                                'toolSpec': {
                                    'name': tool_name,
                                    'description': f'Tool {tool_name} inferred from conversation',
                                    'inputSchema': {'json': {'type': 'object', 'properties': properties, 'required': required}},
                                }
                            }
                            tools.append(tool_spec)
                            seen_tools.add(tool_name)

        return tools

    def _extract_token_usage(self, response):
        return TokenUsage(input_tokens=response['usage']['inputTokens'], output_tokens=response['usage']['outputTokens'])
