import pytest
from src.config.bedrock_converse_provider import BedrockConverseProvider
from src.config.openai_provider import OpenAIProvider
from src.config.anthropic_provider import AnthropicProvider
from src.config.groq_provider import GroqProvider
from src.config.bedrock_provider import BedrockClaudeProvider


@pytest.mark.real_provider
class TestTokenUsageTracking:
    def test_bedrock_converse_returns_token_usage(self):
        provider = BedrockConverseProvider('anthropic.claude-3-haiku-20240307-v1:0')

        response, usage = provider.invoke('You are helpful', 'What is 2+2?')

        assert usage is not None
        assert usage.input_tokens > 0
        assert usage.output_tokens > 0
        assert usage.provider_name == 'Bedrock-Claude-Converse'

    def test_bedrock_legacy_returns_token_usage(self):
        provider = BedrockClaudeProvider('anthropic.claude-3-haiku-20240307-v1:0')

        response, usage = provider.invoke('You are helpful', 'What is 2+2?')

        assert usage is not None
        assert usage.input_tokens > 0
        assert usage.output_tokens > 0
        assert usage.provider_name == 'Bedrock-Claude'

    def test_openai_returns_token_usage(self):
        provider = OpenAIProvider('gpt-4o-mini')

        response, usage = provider.invoke('You are helpful', 'What is 2+2?')

        assert usage is not None
        assert usage.input_tokens > 0
        assert usage.output_tokens > 0
        assert usage.provider_name == 'GPT4o-OpenAI'

    def test_anthropic_returns_token_usage(self):
        provider = AnthropicProvider('claude-3-haiku-20240307')

        response, usage = provider.invoke('You are helpful', 'What is 2+2?')

        assert usage is not None
        assert usage.input_tokens > 0
        assert usage.output_tokens > 0
        assert usage.provider_name == 'Anthropic-Claude'

    def test_groq_returns_token_usage(self):
        provider = GroqProvider('llama-3.1-8b-instant')

        response, usage = provider.invoke('You are helpful', 'What is 2+2?')

        assert usage is not None
        assert usage.input_tokens > 0
        assert usage.output_tokens > 0
        assert usage.provider_name == 'Llama-Groq'
