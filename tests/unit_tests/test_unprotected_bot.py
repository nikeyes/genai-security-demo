import unittest
from unittest.mock import Mock

from chatbot.unprotected_bot import UnprotectedBot
from config.token_usage import TokenUsage
from config.security_config import SecurityConfig


class TestUnprotectedBot(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.bot = UnprotectedBot(self.mock_llm)

    def test_unprotected_bot_has_expected_system_prompt(self):
        self.assertEqual(self.bot.system_prompt, SecurityConfig.get_unprotected_system_prompt())

    def test_chat_calls_llm_with_correct_parameters(self):
        mock_usage = TokenUsage(15, 25)
        self.mock_llm.invoke.return_value = ('Hello there!', mock_usage)
        user_input = 'Hi, how are you?'

        result = self.bot.chat(user_input)

        self.mock_llm.invoke.assert_called_once_with(SecurityConfig.get_unprotected_system_prompt(), user_input)
        self.assertIn('Hello there!', result)
        self.assertIn('📝 LLM Response:', result)
        self.assertIn('Tokens:', result)

    def test_chat_includes_token_usage_in_output(self):
        mock_usage = TokenUsage(10, 20)
        self.mock_llm.invoke.return_value = ('Test response', mock_usage)

        result = self.bot.chat('Test input')

        self.assertIn('Tokens: 10 + 20 = 30', result)

    def test_chat_formats_response_correctly(self):
        mock_usage = TokenUsage(5, 10)
        expected_response = 'This is a test response'
        self.mock_llm.invoke.return_value = (expected_response, mock_usage)

        result = self.bot.chat('Test')

        lines = result.split('\n')
        self.assertIn('📝 LLM Response:', lines)
        self.assertIn(expected_response, lines)
        self.assertTrue(any('Tokens:' in line for line in lines))


if __name__ == '__main__':
    unittest.main()
