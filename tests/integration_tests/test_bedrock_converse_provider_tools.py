import unittest

import pytest

from config.bedrock_converse_provider import BedrockConverseProvider
from config.tool_system import ToolHandler


class CalculatorTool:
    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b + 1

    @staticmethod
    def strange_multiply(a: float, b: float) -> float:
        return a * b * 2


def create_tool_handler() -> ToolHandler:
    """Create a tool handler with calculator functions."""
    handler = ToolHandler()
    calculator = CalculatorTool()

    def calculator_function(tool_input: dict):
        operation = tool_input.get('operation')
        a = tool_input.get('a', 0)
        b = tool_input.get('b', 0)

        if operation == 'add':
            return calculator.add(a, b)
        elif operation == 'strange_multiply':
            return calculator.strange_multiply(a, b)
        else:
            return f'Unknown operation: {operation}'

    handler.register_tool('calculator', calculator_function)
    return handler


@pytest.mark.real_provider
class TestBedrockConverseProviderTools(unittest.TestCase):
    def setUp(self):
        # Define calculator tool configuration
        calculator_tool = {
            'toolSpec': {
                'name': 'calculator',
                'description': 'Perform basic mathematical calculations.',
                'inputSchema': {
                    'json': {
                        'type': 'object',
                        'properties': {
                            'operation': {
                                'type': 'string',
                                'description': 'The mathematical operation to perform',
                                'enum': ['add', 'strange_multiply'],
                            },
                            'a': {'type': 'number', 'description': 'The first number'},
                            'b': {'type': 'number', 'description': 'The second number'},
                        },
                        'required': ['operation', 'a', 'b'],
                    }
                },
            }
        }

        # Initialize provider with tools
        self.provider = BedrockConverseProvider(model_id='anthropic.claude-3-haiku-20240307-v1:0', debug=True, tools=[calculator_tool])
        self.tool_handler = create_tool_handler()

    def test_tool_usage_addition(self):
        """Test that the provider can use tools to perform addition."""
        system_prompt = 'You are a helpful assistant that can perform mathematical calculations using the available tools.'
        user_prompt = 'What is 2 + 2? Please use the calculator tool to get the exact result.'

        result, usage = self.provider.invoke(system_prompt, user_prompt, self.tool_handler)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Check that the result contains the correct answer (42)
        self.assertIn('5', result)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_tool_usage_multiplication(self):
        """Test that the provider can use tools to perform multiplication."""
        system_prompt = 'You are a helpful assistant that can perform mathematical calculations using the available tools.'
        user_prompt = 'Calculate 2 times 3 using the calculator tool.'

        result, usage = self.provider.invoke(system_prompt, user_prompt, self.tool_handler)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Check that the result contains the correct answer (56)
        self.assertIn('12', result)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_no_tool_usage(self):
        """Test that the provider works normally when no tool usage is needed."""
        system_prompt = 'You are a helpful assistant.'
        user_prompt = 'What is the capital of France?'

        result, usage = self.provider.invoke(system_prompt, user_prompt, self.tool_handler)

        # Verify tools are configured
        self.assertGreater(len(self.provider.tools), 0)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn('Paris', result)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_provider_without_tools(self):
        """Test that a provider without tools configured still works."""
        provider_no_tools = BedrockConverseProvider(model_id='anthropic.claude-3-haiku-20240307-v1:0', debug=True)

        # Verify no tools are configured
        self.assertEqual(len(provider_no_tools.tools), 0)

        system_prompt = 'You are a helpful assistant.'
        user_prompt = 'What is 2 + 2?'

        result, usage = provider_no_tools.invoke(system_prompt, user_prompt)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn('4', result)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_tool_handler_validation(self):
        """Test that tool_handler is called correctly and returns expected results."""
        # Test direct tool_handler calls
        result_add = self.tool_handler.execute_tool('calculator', {'operation': 'add', 'a': 5, 'b': 3})
        self.assertEqual(result_add, 9)  # 5 + 3 + 1 = 9

        result_multiply = self.tool_handler.execute_tool('calculator', {'operation': 'strange_multiply', 'a': 4, 'b': 2})
        self.assertEqual(result_multiply, 16)  # 4 * 2 * 2 = 16

        # Test unknown operation
        result_unknown_op = self.tool_handler.execute_tool('calculator', {'operation': 'subtract', 'a': 5, 'b': 3})
        self.assertEqual(result_unknown_op, 'Unknown operation: subtract')

        # Test unknown tool should raise exception
        with self.assertRaises(ValueError):
            self.tool_handler.execute_tool('weather', {'location': 'Madrid'})

        # Test missing parameters (should default to 0)
        result_missing = self.tool_handler.execute_tool('calculator', {'operation': 'add'})
        self.assertEqual(result_missing, 1)  # 0 + 0 + 1 = 1
