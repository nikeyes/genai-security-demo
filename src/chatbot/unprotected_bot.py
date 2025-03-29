from prompts import UNPROTECTED_SYSTEM_PROMPT


class UnprotectedBot:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = UNPROTECTED_SYSTEM_PROMPT

    def chat(self, user_prompt: str):
        result = self.llm.invoke(self.system_prompt, user_prompt)
        
        output = []
        output.append("\n📝 LLM Response:")
        output.append("-" * 40)
        output.append(f"{result}")
        formatted_output = "\n".join(output)
        print(formatted_output)  # For debugging
        return formatted_output
