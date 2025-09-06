from .anthropic_provider import AnthropicProvider
from .bedrock_converse_provider import BedrockConverseProvider
from .bedrock_provider import BedrockClaudeProvider
from .groq_provider import GroqProvider
from .openai_provider import OpenAIProvider


class LLMConfig:
    # Model IDs (kept for backward compatibility with RAG)
    GROQ_MODEL_ID = 'llama-3.3-70b-versatile'
    OPENAI_MODEL_ID = 'gpt-4o-mini'
    BEDROCK_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'
    BEDROCK_CONVERSE_MODEL_ID = 'eu.amazon.nova-lite-v1:0'
    ANTHROPIC_MODEL_ID = 'claude-3-haiku-20240307'

    # Security configuration
    LLAMA_SECURITY_FAMILY = True

    # Provider configurations: [ClassName, model_id]
    PROVIDERS = {
        'groq': [GroqProvider, GROQ_MODEL_ID],
        'openai': [OpenAIProvider, OPENAI_MODEL_ID],
        'bedrock': [BedrockClaudeProvider, BEDROCK_MODEL_ID],
        'bedrock_converse': [BedrockConverseProvider, BEDROCK_CONVERSE_MODEL_ID],
        'anthropic': [AnthropicProvider, ANTHROPIC_MODEL_ID],
    }

    def __init__(self, debug=False):
        self.debug = debug
        self.providers = {}
        self.default_unprotected_llm = None
        self.default_secure_llm = None

    def initialize(self):
        self._initialize_providers()
        self._set_defaults()
        return self

    def _initialize_providers(self):
        for name, (provider_class, model_id) in self.PROVIDERS.items():
            self.providers[name] = provider_class(model_id=model_id, debug=self.debug)

    def _set_defaults(self):
        self.default_unprotected_llm = self.providers['bedrock_converse']
        self.default_secure_llm = self.providers['bedrock_converse']

    def get_provider(self, name):
        """Get provider by name. Easier to add new providers."""
        return self.providers.get(name)

    # Backwards compatibility methods
    def get_groq_llm(self):
        return self.providers['groq']

    def get_openai_llm(self):
        return self.providers['openai']

    def get_bedrock_llm(self):
        return self.providers['bedrock']

    def get_anthropic_llm(self):
        return self.providers['anthropic']

    def get_bedrock_converse_llm(self):
        return self.providers['bedrock_converse']

    def get_default_unprotected_llm(self):
        return self.default_unprotected_llm

    def get_default_secure_llm(self):
        return self.default_secure_llm
