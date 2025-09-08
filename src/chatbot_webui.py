"""GenAI security demo web interface with tabbed comparisons of different protection levels."""

import gradio as gr

from config.llm_config import LLMConfig
from ui.direct_injection_ui import basic_demo
from ui.prompt_injection_demo_ui import leak_demo
from ui.input_guardrail_ui import input_guardrail_demo
from ui.output_guardrail_ui import output_guardrail_demo
from ui.rag_ui import rag_demo

config = LLMConfig()

if config.LLAMA_SECURITY_FAMILY:
    demos = [basic_demo, rag_demo, leak_demo, input_guardrail_demo, output_guardrail_demo]
    demo_names = ['Direct', 'RAG', 'Prompt Leak', 'Input Guardrails', 'Output Guardrails']
else:
    demos = [basic_demo, rag_demo, leak_demo]
    demo_names = ['Direct', 'RAG', 'Prompt Leak']

demo = gr.TabbedInterface(demos, demo_names)
demo.launch(server_port=7860, share=False)
