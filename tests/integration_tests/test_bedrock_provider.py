import unittest

import pytest

from config.llm_config import LLMConfig


@pytest.mark.real_provider
class TestBedrockClaudeProvider(unittest.TestCase):
    def setUp(self):
        llm_config = LLMConfig(debug=False)
        llm_config.initialize()

        self.provider = llm_config.get_bedrock_llm()

    def test_real_invocation(self):
        system_prompt = 'You are a helpful assistant.'
        user_prompt = 'Who are your creator?'

        result = self.provider.invoke(system_prompt, user_prompt)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn('Anthropic', result)
