import json
import boto3
from .logger_config import setup_logger


class BedrockClaudeProvider:
    def __init__(self, model_id: str, debug: bool = False):
        self.name = 'Bedrock-Claude'
        self.client = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1')
        self.model_id = model_id
        self.logger = setup_logger(__name__, debug)
        self.logger.debug('ClaudeWrapper initialized')

    @staticmethod
    def is_empty(s):
        return s.strip() == ''

    def invoke(self, system_prompt: str, user_prompt: str):
        if self.is_empty(user_prompt):
            return ' '

        body = json.dumps(
            {
                'system': system_prompt,
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1024,
                'messages': [
                    {
                        'role': 'user',
                        'content': [{'type': 'text', 'text': user_prompt}],
                    }
                ],
                'stop_sequences': ['\n\nHuman:', '\n\nAssistant', '</function_calls>'],
            }
        )

        self.trace_invocation_info(user_prompt, self.model_id, body)

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
        )

        completion = json.loads(response.get('body').read())

        output_list = completion.get('content', [])

        self.trace_invocation_result(completion, output_list)

        completion_text = output_list[0]['text']

        return completion_text

    def trace_invocation_info(self, user_prompt, model_id, body):
        self.logger.debug('Invocation details:')
        self.logger.debug('model_id: %s', model_id)
        self.logger.debug('user prompt: %s', user_prompt)
        self.logger.debug('body: %s', body)

    def trace_invocation_result(self, completion, output_list):
        input_tokens = completion['usage']['input_tokens']
        output_tokens = completion['usage']['output_tokens']
        self.logger.debug('Response details:')
        self.logger.debug('- Input tokens: %s', input_tokens)
        self.logger.debug('- Output tokens: %s', output_tokens)

        for output in output_list:
            self.logger.debug(output['text'])
        self.logger.debug('Invocation completed.')
