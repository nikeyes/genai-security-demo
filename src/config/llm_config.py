from config.bedrock_provider import BedrockClaudeProvider
from config.groq_provider import GroqProvider
from config.openai_provider import OpenAIProvider
from config.anthropic_provider import AnthropicProvider

GROQ_MODEL_ID = 'llama-3.3-70b-versatile'
OPENAI_MODEL_ID = 'gpt-4o-mini'
BEDROCK_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'
ANTHROPIC_MODEL_ID = 'claude-3-haiku-20240307'

GROQ_LLM = GroqProvider(model_id=GROQ_MODEL_ID, debug=False)
OPENAI_LLM = OpenAIProvider(model_id=OPENAI_MODEL_ID, debug=False)
BEDROCK_LLM = BedrockClaudeProvider(model_id=BEDROCK_MODEL_ID, debug=False)
ANTHROPIC_LLM = AnthropicProvider(model_id=ANTHROPIC_MODEL_ID, debug=False)


DEFAULT_UNPROTECTED_LLM = BEDROCK_LLM
DEFAULT_SECURE_LLM = BEDROCK_LLM

# You can disable this part of the demo, if you don't have huggingface account
# or you can't to accept the terms of service for Llama Prompt Guard
# You can see README.md for more information:
#   1.1 This project uses Llama PromptGuard and Purple-Llama CodeShield
LLAMA_SECURITY_FAMILY = True
