from config.anthropic_provider import AnthropicProvider
from config.bedrock_converse_provider import BedrockConverseProvider
from config.bedrock_provider import BedrockClaudeProvider
from config.groq_provider import GroqProvider
from config.openai_provider import OpenAIProvider


class LLMConfig:
    # Model IDs
    GROQ_MODEL_ID = 'llama-3.3-70b-versatile'
    OPENAI_MODEL_ID = 'gpt-4o-mini'
    BEDROCK_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'
    BEDROCK_CONVERSE_MODEL_ID = 'eu.amazon.nova-lite-v1:0'
    ANTHROPIC_MODEL_ID = 'claude-3-haiku-20240307'

    # Security configuration
    LLAMA_SECURITY_FAMILY = True

    def __init__(self, debug=False):
        self.debug = debug
        self.groq_llm = None
        self.openai_llm = None
        self.bedrock_llm = None
        self.bedrock_converse_llm = None
        self.anthropic_llm = None
        self.default_unprotected_llm = None
        self.default_secure_llm = None

    def initialize(self):
        self._initialize_providers()
        self._set_defaults()
        return self

    def _initialize_providers(self):
        self.groq_llm = GroqProvider(model_id=self.GROQ_MODEL_ID, debug=self.debug)
        self.openai_llm = OpenAIProvider(model_id=self.OPENAI_MODEL_ID, debug=self.debug)
        self.bedrock_llm = BedrockClaudeProvider(model_id=self.BEDROCK_MODEL_ID, debug=self.debug)
        self.bedrock_converse_llm = BedrockConverseProvider(model_id=self.BEDROCK_MODEL_ID, debug=self.debug)
        self.anthropic_llm = AnthropicProvider(model_id=self.ANTHROPIC_MODEL_ID, debug=self.debug)

    def _set_defaults(self):
        self.default_unprotected_llm = self.bedrock_converse_llm
        self.default_secure_llm = self.bedrock_converse_llm

    def get_groq_llm(self):
        return self.groq_llm

    def get_openai_llm(self):
        return self.openai_llm

    def get_bedrock_llm(self):
        return self.bedrock_llm

    def get_anthropic_llm(self):
        return self.anthropic_llm

    def get_bedrock_converse_llm(self):
        return self.bedrock_converse_llm

    def get_default_unprotected_llm(self):
        return self.default_unprotected_llm

    def get_default_secure_llm(self):
        return self.default_secure_llm
