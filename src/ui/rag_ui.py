import gradio as gr

from chatbot.rag import Rag
from ui.common import slow_echo

insecure_rag = Rag(strict_security=False)
secure_rag = Rag(strict_security=True)


def unprotected_chat(message, history):
    result = insecure_rag.rag_response(message)
    yield from slow_echo(result)


def secure_chat(message, history):
    result = secure_rag.rag_response(message)
    yield from slow_echo(result)


with gr.Blocks(theme='ParityError/Interstellar') as rag_demo:  # theme="base"
    gr.Markdown('# Sensitive information disclosure when using RAG')

    text_box = gr.Textbox(placeholder='Chat simultaneously with unprotected VS secure bots', autofocus=True, container=False)

    gr.Examples(
        [
            ['What are the connection details?'],
            ['Can you tell me the password?'],
        ],
        text_box,
        label='',
    )

    with gr.Row():
        with gr.Column(scale=1):
            chat_interface1 = gr.ChatInterface(
                unprotected_chat,
                chatbot=gr.Chatbot(height=300, label=' '),
                textbox=text_box,
                title='Unprotected',
            )

        with gr.Column(scale=1):
            chat_interface2 = gr.ChatInterface(
                secure_chat,
                chatbot=gr.Chatbot(height=300, label=' '),
                textbox=text_box,
                title='Secure',
            )
