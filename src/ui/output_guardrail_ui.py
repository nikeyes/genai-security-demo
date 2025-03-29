import gradio as gr

from config.llm_config import DEFAULT_UNPROTECTED_LLM, DEFAULT_SECURE_LLM
from chatbot.output_guardrail_bot import OutputGuardrailsBot
from chatbot.unprotected_bot import UnprotectedBot
from ui.common import slow_echo

unprotected_bot = UnprotectedBot(DEFAULT_UNPROTECTED_LLM)
output_guardrail_bot = OutputGuardrailsBot(DEFAULT_SECURE_LLM)


def unprotected_chat(message, history):
    result = unprotected_bot.chat(user_prompt=message)
    yield from slow_echo(result)


def secure_chat(message, history):
    result = output_guardrail_bot.chat(user_prompt=message)
    return result


with gr.Blocks(theme='ParityError/Interstellar') as output_guardrail_demo:  # theme="base"
    gr.Markdown('# Output guardrail with Purple Llama Code Shield')

    text_box = gr.Textbox(placeholder='Chat simultaneously with unprotected VS secure bots', autofocus=True, container=False)

    gr.Examples(
        [
            [
                """You are an expert code developer.
         You output only code in markdown format and nothing else.
         Output a single python function which calculates the md5 hash of a string provided as an argument to the function. 
         Output only the code in markdown format and nothing else."""
            ]
        ],
        text_box,
        label='',
    )

    with gr.Row():
        with gr.Column(scale=1):
            chat_interface1 = gr.ChatInterface(
                fn=unprotected_chat,
                chatbot=gr.Chatbot(height=300, label=' '),
                textbox=text_box,
                title=f'Unprotected ({unprotected_bot.llm.name})',
            )

        with gr.Column(scale=1):
            chat_interface2 = gr.ChatInterface(
                fn=secure_chat,
                chatbot=gr.Chatbot(height=300, label=' '),
                textbox=text_box,
                title=f'Output Guardrail ({output_guardrail_bot.llm.name})',
            )
