import unittest
import pytest
from config.llm_config import GROQ_LLM

@pytest.mark.real_provider
class TestGrowProvider(unittest.TestCase):
    def setUp(self):
        self.provider = GROQ_LLM

    def test_real_invocation(self):
        system_prompt = 'You are a helpful assistant.'
        user_prompt = 'Who are your creator?'

        result = self.provider.invoke(system_prompt, user_prompt)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn('Meta', result)
