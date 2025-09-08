import asyncio

from config.security_config import SecurityConfig
from config.token_usage import format_token_usage


class SystemPromptGuardrailBot:
    """Chatbot with parallel guardrail checks for instruction changes and prompt leakage."""

    INSTRUCTION_CHANGE_GUARDRAIL_TRIGGERED_MESSAGE = 'INSTRUCTION_CHANGE_GUARDRAIL TRIGGERED'

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = SecurityConfig.get_secure_system_prompt()

    async def chat(self, user_prompt: str):
        return self.llm.invoke(self.system_prompt, user_prompt)

    async def detect_instruction_change_attempt(self, user_prompt):
        response, _ = self.llm.invoke(SecurityConfig.INSTRUCTION_CHANGE_GUARDRAIL_PROMPT, user_prompt)
        return response

    async def execute_chat_with_guardrail(self, user_prompt):
        guardrail_task = asyncio.create_task(self.detect_instruction_change_attempt(user_prompt))
        chat_task = asyncio.create_task(self.chat(user_prompt))

        while True:
            completed_tasks, _ = await asyncio.wait([guardrail_task, chat_task], return_when=asyncio.FIRST_COMPLETED)

            if guardrail_task in completed_tasks:
                if self._should_block_request(guardrail_task.result()):
                    chat_task.cancel()
                    return SecurityConfig.get_blocked_message('instruction_change')

                if chat_task in completed_tasks:
                    return await self._process_chat_response(chat_task.result())
            else:
                await asyncio.sleep(0.1)

    def _should_block_request(self, guardrail_result):
        return guardrail_result == 'not_allowed'

    async def _process_chat_response(self, chat_result):
        chat_response, chat_usage = chat_result
        response_after_canary_check = self.check_system_prompt_leak(chat_response)

        if self._is_blocked_response(response_after_canary_check):
            return response_after_canary_check

        return f'{response_after_canary_check}\n\n{format_token_usage(chat_usage)}'

    def _is_blocked_response(self, response):
        return response.startswith("Sorry I won't do that.")

    def check_system_prompt_leak(self, chat_response):
        if SecurityConfig.CANARY_WORD in chat_response:
            return SecurityConfig.get_blocked_message('canary')
        return chat_response

    async def execute_chat_with_sandwich(self, user_prompt):
        response, usage = await self.chat(user_prompt + SecurityConfig.get_sandwich_bottom())
        return f'{response}\n\n{format_token_usage(usage)}'
