import unittest

import pytest

from config.tool_system import ToolHandler, ToolSpec


class UserInfoTool:
    @staticmethod
    def get_user_info(user_id: str) -> str:
        """Get simulated user information based on user ID."""
        import hashlib

        # Fixed data arrays for consistent results
        names = ['Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank']
        departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']

        # Generate consistent "random" data based on user_id hash
        user_hash = int(hashlib.md5(str(user_id).encode()).hexdigest()[:8], 16)

        name = names[user_hash % len(names)]
        department = departments[user_hash % len(departments)]
        score = 60 + (user_hash % 40)  # Score between 60-100

        return f'User {user_id}: {name}, {department} dept, Score: {score}/100'


def create_tool_handler() -> ToolHandler:
    """Create a tool handler with user info functions."""
    handler = ToolHandler()
    user_tool = UserInfoTool()

    def user_info_function(tool_input: dict):
        action = tool_input.get('action')
        user_id = tool_input.get('user_id', '0')

        if action == 'get_info':
            return user_tool.get_user_info(user_id)
        else:
            return f'Unknown action: {action}'

    handler.register_tool('user_info', user_info_function)
    return handler


@pytest.mark.real_provider
class TestGroqProviderTools(unittest.TestCase):
    def setUp(self):
        from config.groq_provider import GroqProvider

        # Define user info tool configuration
        user_info_tool = ToolSpec(
            name='user_info',
            description='Get user information from the company database (simulated data).',
            parameters={
                'action': {
                    'type': 'string',
                    'description': 'The action to perform',
                    'enum': ['get_info'],
                },
                'user_id': {'type': 'string', 'description': 'The user ID to look up'},
            },
            required=['action', 'user_id'],
        )

        # Initialize provider with tools
        self.provider = GroqProvider(model_id='llama-3.3-70b-versatile', debug=True, tools=[user_info_tool])
        self.tool_handler = create_tool_handler()

    def test_tool_usage_user_info(self):
        """Test that the provider can use tools to get user information."""
        system_prompt = 'You are a helpful assistant that can look up user information using the available tools.'
        user_prompt = 'Please get information for user ID "123" using the user info tool.'

        result, usage = self.provider.invoke(system_prompt, user_prompt, self.tool_handler)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Check that the result contains user info (user 123 will always give same result)
        self.assertIn('123', result)  # Should contain user ID
        self.assertIn('Carol', result)  # Should contain the name
        self.assertIn('Finance', result)  # Should contain the department
        self.assertIn('94', result)  # Should contain the score
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_tool_usage_different_user(self):
        """Test that the provider can use tools with different user IDs."""
        system_prompt = 'You are a helpful assistant that can look up user information using the available tools.'
        user_prompt = 'Please get information for user ID "456" using the user info tool.'

        result, usage = self.provider.invoke(system_prompt, user_prompt, self.tool_handler)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Check that the result contains different user info (user 456 gives different result than 123)
        self.assertIn('456', result)  # Should contain user ID
        self.assertIn('Bob', result)  # Should contain the name (different from Carol)
        self.assertIn('HR', result)  # Should contain the department (different from Finance)
        self.assertIn('73', result)  # Should contain the score (different from 94)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_no_tool_usage(self):
        """Test that the provider works normally when no tool usage is needed."""
        system_prompt = 'You are a helpful assistant.'
        user_prompt = 'What is the capital of France?'

        result, usage = self.provider.invoke(system_prompt, user_prompt, self.tool_handler)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn('Paris', result)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_provider_without_tools(self):
        """Test that a provider without tools configured still works."""
        system_prompt = 'You are a helpful assistant.'
        user_prompt = 'What is 2 + 2?'

        result, usage = self.provider.invoke(system_prompt, user_prompt)

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn('4', result)
        self.assertIsNotNone(usage)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_tool_handler_validation(self):
        """Test that tool_handler is called correctly and returns expected results."""
        # Test direct tool_handler calls
        result_user_123 = self.tool_handler.execute_tool('user_info', {'action': 'get_info', 'user_id': '123'})
        # User 123 will always give consistent result based on hash
        self.assertIn('User 123:', result_user_123)
        self.assertIn('dept', result_user_123)
        self.assertIn('Score:', result_user_123)

        result_user_456 = self.tool_handler.execute_tool('user_info', {'action': 'get_info', 'user_id': '456'})
        # User 456 should give different result than 123
        self.assertIn('User 456:', result_user_456)
        self.assertNotEqual(result_user_123, result_user_456)

        # Test unknown action
        result_unknown_action = self.tool_handler.execute_tool('user_info', {'action': 'delete', 'user_id': '123'})
        self.assertEqual(result_unknown_action, 'Unknown action: delete')

        # Test unknown tool should raise exception
        with self.assertRaises(ValueError):
            self.tool_handler.execute_tool('weather', {'location': 'Madrid'})

        # Test missing parameters (should default to '0')
        result_missing = self.tool_handler.execute_tool('user_info', {'action': 'get_info'})
        self.assertIn('User 0:', result_missing)
