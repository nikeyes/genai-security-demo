from prompts import UNPROTECTED_SYSTEM_PROMPT
from config.token_usage import format_token_usage


class UnprotectedBot:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = UNPROTECTED_SYSTEM_PROMPT

    def chat(self, user_prompt: str):
        result, usage = self.llm.invoke(self.system_prompt, user_prompt)

        output = []
        output.append('\n📝 LLM Response:')
        output.append('-' * 40)
        output.append(f'{result}')
        output.append('\n' + format_token_usage(usage))
        formatted_output = '\n'.join(output)
        print(formatted_output)  # For debugging
        return formatted_output
