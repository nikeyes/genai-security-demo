import json
import boto3
from .base_provider import BaseProvider
from .token_usage import TokenUsage
from .tool_adapters import NoOpToolAdapter


class BedrockClaudeProvider(BaseProvider):
    def __init__(self, model_id: str, debug: bool = False):
        super().__init__('Bedrock-Claude', model_id, debug)
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1')

    def _create_tool_adapter(self) -> NoOpToolAdapter:
        """Create NoOp tool adapter since this Bedrock provider doesn't support tools."""
        return NoOpToolAdapter()

    def invoke(self, system_prompt: str, user_prompt: str, tool_handler=None):
        if self.is_empty(user_prompt):
            return ' '

        body = json.dumps(
            {
                'system': system_prompt,
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': self.DEFAULT_MAX_TOKENS,
                'temperature': self.DEFAULT_TEMPERATURE,
                'top_p': self.DEFAULT_TOP_P,
                'messages': [
                    {
                        'role': 'user',
                        'content': [{'type': 'text', 'text': user_prompt}],
                    }
                ],
                'stop_sequences': self.STOP_SEQUENCES,
            }
        )

        self.trace_invocation_info(user_prompt, self.model_id, body)

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
        )

        completion = json.loads(response.get('body').read())

        output_list = completion.get('content', [])
        completion_text = output_list[0]['text']

        input_tokens = completion['usage']['input_tokens']
        output_tokens = completion['usage']['output_tokens']
        self.trace_invocation_result_with_tokens(input_tokens, output_tokens, completion_text)

        usage = self._extract_token_usage(completion)
        return completion_text, usage

    def _add_tool_conversation(self, messages, response, formatted_results):
        """No-op implementation since this provider doesn't support tools."""
        pass

    def _make_tool_followup_call(self, params):
        """No-op implementation since this provider doesn't support tools."""
        return None

    def _extract_token_usage(self, completion):
        return TokenUsage(input_tokens=completion['usage']['input_tokens'], output_tokens=completion['usage']['output_tokens'])
