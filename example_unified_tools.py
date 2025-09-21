#!/usr/bin/env python3
"""
Example demonstrating unified tool system across different providers.
This shows how the same tools can be used with Bedrock, OpenAI, and Groq providers.
"""

from src.config.tool_system import ToolSpec, ToolHandler
from src.config.bedrock_converse_provider import BedrockConverseProvider
from src.config.openai_provider import OpenAIProvider
from src.config.groq_provider import GroqProvider


def create_calculator_tools():
    """Create standard calculator tools that work across all providers."""
    calculator_tool = ToolSpec(
        name='calculator',
        description='Perform basic mathematical calculations like addition and multiplication.',
        parameters={
            'operation': {'type': 'string', 'description': 'The mathematical operation to perform', 'enum': ['add', 'multiply']},
            'a': {'type': 'number', 'description': 'The first number'},
            'b': {'type': 'number', 'description': 'The second number'},
        },
        required=['operation', 'a', 'b'],
    )
    return [calculator_tool]


def create_tool_handler():
    """Create a tool handler with calculator functions."""
    handler = ToolHandler()

    def calculator_function(tool_input: dict):
        operation = tool_input.get('operation')
        a = tool_input.get('a', 0)
        b = tool_input.get('b', 0)

        if operation == 'add':
            return a + b
        elif operation == 'multiply':
            return a * b
        else:
            return f'Unknown operation: {operation}'

    handler.register_tool('calculator', calculator_function)
    return handler


def demonstrate_provider(provider_class, model_id, provider_name):
    """Demonstrate tool usage with a specific provider."""
    print(f'\n=== {provider_name} Provider ===')

    try:
        # Create tools and handler
        tools = create_calculator_tools()
        # Note: tool_handler would be used for actual invocations
        # tool_handler = create_tool_handler()

        # Initialize provider with tools
        provider = provider_class(model_id=model_id, debug=True, tools=tools)

        # Test basic functionality
        print(f'Provider supports tools: {provider.supports_tools()}')
        print(f'Provider has tools: {provider.has_tools()}')
        print(f'Number of tools: {len(provider.tools)}')

        # Show tool conversion
        if provider.tool_adapter and provider.tools:
            converted_tools = provider.tool_adapter.convert_tools(provider.tools)
            print(f'Tools converted to {provider_name} format:')
            # Handle different formats
            if 'toolSpec' in converted_tools[0]:
                tool_name = converted_tools[0]['toolSpec']['name']
            elif 'function' in converted_tools[0]:
                tool_name = converted_tools[0]['function']['name']
            else:
                tool_name = 'N/A'
            print(f'  Tool name: {tool_name}')

        print(f'{provider_name} provider configured successfully!')

    except Exception as e:
        print(f'Error with {provider_name}: {e}')


def main():
    """Main demonstration function."""
    print('Unified Tool System Demonstration')
    print('=' * 40)

    # Note: These won't actually work without proper API keys and network access
    # but they demonstrate the unified interface

    demonstrate_provider(BedrockConverseProvider, 'anthropic.claude-3-haiku-20240307-v1:0', 'Bedrock')

    demonstrate_provider(OpenAIProvider, 'gpt-4o-mini', 'OpenAI')

    demonstrate_provider(GroqProvider, 'llama-3.1-70b-versatile', 'Groq')

    print('\n' + '=' * 40)
    print('All providers use the same ToolSpec and ToolHandler!')
    print("Tools are automatically converted to each provider's format.")


if __name__ == '__main__':
    main()
