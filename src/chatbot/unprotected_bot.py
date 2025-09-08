from config.security_config import SecurityConfig
from config.token_usage import format_token_usage


class UnprotectedBot:
    """Chatbot with no security measures - vulnerable by design for comparison."""

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = SecurityConfig.get_unprotected_system_prompt()

    def chat(self, user_prompt: str):
        result, usage = self.llm.invoke(self.system_prompt, user_prompt)

        output = ['\n📝 LLM Response:', '-' * 40, result, '\n' + format_token_usage(usage)]
        return '\n'.join(output)
