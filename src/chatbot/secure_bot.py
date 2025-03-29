import asyncio

from prompts import SECURE_SYSTEM_PROMPT, INSTRUCTION_CHANGE_GUARDRAIL_SYSTEM_PROMPT, SANDWICH_BOTTOM


class SecureBot:
    INSTRUCTION_CHANGE_GUARDRAIL_TRIGGERED_MESSAGE = 'INSTRUCTION_CHANGE_GUARDRAIL TRIGGERED'

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = SECURE_SYSTEM_PROMPT

    async def chat(self, user_prompt: str):
        return self.llm.invoke(self.system_prompt, user_prompt)

    async def instruction_change_guardrail(self, user_prompt):
        print('Checking instruction_change guardrail')

        return self.llm.invoke(INSTRUCTION_CHANGE_GUARDRAIL_SYSTEM_PROMPT, user_prompt)

    async def execute_chat_with_guardrail(self, user_prompt):
        instruction_change_guardrail_task = asyncio.create_task(self.instruction_change_guardrail(user_prompt))
        chat_task = asyncio.create_task(self.chat(user_prompt))

        while True:
            done, _ = await asyncio.wait([instruction_change_guardrail_task, chat_task], return_when=asyncio.FIRST_COMPLETED)
            if instruction_change_guardrail_task in done:
                guardrail_response = instruction_change_guardrail_task.result()
                if guardrail_response == 'not_allowed':
                    chat_task.cancel()
                    print(self.INSTRUCTION_CHANGE_GUARDRAIL_TRIGGERED_MESSAGE)
                    return "Sorry I won't do that. [GUARDRAIL]"
                elif chat_task in done:
                    chat_response = chat_task.result()
                    return self.check_system_prompt_leak(chat_response)
            else:
                await asyncio.sleep(0.1)

    def check_system_prompt_leak(self, chat_response):
        if 'lightblueeagle' in chat_response:
            print('canary word found in response')
            return "Sorry I won't do that. [CANARY]"

        return chat_response

    async def execute_chat_with_sandwich(self, user_prompt):
        return await self.chat(user_prompt + SANDWICH_BOTTOM)
