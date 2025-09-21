"""Unit tests for BedrockConverseProvider structure and tool configuration."""

import unittest
from unittest.mock import Mock, patch
from src.config.bedrock_converse_provider import BedrockConverseProvider


class TestBedrockConverseProviderStructure(unittest.TestCase):
    """Test BedrockConverseProvider initialization and tool configuration."""

    def test_initialization_without_tools(self):
        """Test provider initialization without tools."""
        with patch('boto3.client'):
            provider = BedrockConverseProvider('test-model')
            self.assertEqual(len(provider.tools), 0)
            self.assertEqual(provider.model_id, 'test-model')

    def test_initialization_with_tools(self):
        """Test provider initialization with tools."""
        tools = [
            {
                'toolSpec': {
                    'name': 'test_tool',
                    'description': 'A test tool',
                    'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}},
                }
            }
        ]

        with patch('boto3.client'):
            provider = BedrockConverseProvider('test-model', tools=tools)
            self.assertEqual(len(provider.tools), 1)
            self.assertEqual(provider.tools[0].name, 'test_tool')

    def test_initialization_with_empty_tools_list(self):
        """Test provider initialization with empty tools list."""
        with patch('boto3.client'):
            provider = BedrockConverseProvider('test-model', tools=[])
            self.assertEqual(len(provider.tools), 0)

    def test_tool_config_structure(self):
        """Test that tool configuration follows AWS Bedrock format."""
        calculator_tool = {
            'toolSpec': {
                'name': 'calculator',
                'description': 'Perform basic mathematical calculations',
                'inputSchema': {
                    'json': {
                        'type': 'object',
                        'properties': {
                            'operation': {'type': 'string', 'enum': ['add', 'multiply']},
                            'a': {'type': 'number'},
                            'b': {'type': 'number'},
                        },
                        'required': ['operation', 'a', 'b'],
                    }
                },
            }
        }

        with patch('boto3.client'):
            provider = BedrockConverseProvider('test-model', tools=[calculator_tool])

            # Verify tool structure (now ToolSpec objects)
            tool_spec = provider.tools[0]
            self.assertEqual(tool_spec.name, 'calculator')
            self.assertEqual(tool_spec.description, 'Perform basic mathematical calculations')
            self.assertIn('operation', tool_spec.parameters)
            self.assertIn('a', tool_spec.parameters)
            self.assertIn('b', tool_spec.parameters)
            self.assertEqual(tool_spec.required, ['operation', 'a', 'b'])

    @patch('boto3.client')
    def test_invoke_method_signature(self, mock_boto3):
        """Test that invoke method accepts tool_handler parameter."""
        provider = BedrockConverseProvider('test-model')

        # Mock the client response to avoid actual AWS calls
        mock_client = Mock()
        mock_response = {'output': {'message': {'content': [{'text': 'test response'}]}}, 'usage': {'inputTokens': 10, 'outputTokens': 20}}
        mock_client.converse.return_value = mock_response
        provider.client = mock_client

        # Test that method accepts tool_handler parameter
        try:
            provider.invoke('system', 'user', tool_handler=None)
            success = True
        except TypeError:
            success = False

        self.assertTrue(success, 'invoke method should accept tool_handler parameter')
