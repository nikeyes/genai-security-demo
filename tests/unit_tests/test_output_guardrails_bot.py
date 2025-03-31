import asyncio
import unittest
from unittest.mock import MagicMock

from chatbot.output_guardrail_bot import OutputGuardrailsBot


class TestOutputGuardrailBot(unittest.TestCase):
    def setUp(self):
        # Create a bot instance with a mock LLM
        self.mock_llm = MagicMock()
        self.bot = OutputGuardrailsBot(self.mock_llm)

    def test_scan_no_code_output(self):
        secure_code = """I'm afraid I'm not an expert code developer.
                         I'm Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest."""

        output = asyncio.run(self.bot.scan_llm_output(secure_code))

        self.assertIn('SECURE', output)
        self.assertIn('✅ No security issues detected', output)
        self.assertIn(secure_code, output)

    def test_scan_secure_code_output(self):
        secure_code = 'def add(a, b):\n    return a + b'

        output = asyncio.run(self.bot.scan_llm_output(secure_code))

        self.assertIn('SECURE', output)
        self.assertIn('✅ No security issues detected', output)
        self.assertIn(secure_code, output)

    def test_scan_insecure_code_output(self):
        insecure_code = """
        import hashlib
        def get_md5_hash(input_string):
            md5_hash = hashlib.md5(input_string.encode('utf-8')).hexdigest()
            return md5_hash
        """

        output = asyncio.run(self.bot.scan_llm_output(insecure_code))

        self.assertIn('INSECURE', output)
        self.assertIn('Issues Found', output)
        self.assertIn(insecure_code, output)


if __name__ == '__main__':
    unittest.main()
