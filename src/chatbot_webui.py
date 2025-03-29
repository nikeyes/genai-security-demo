import gradio as gr

from ui.basic_ui import basic_demo
from ui.basic_ui_prompt_leak import leak_demo
from ui.rag_ui import rag_demo
from ui.input_guardrail_ui import input_guardrail_demo
from ui.output_guardrail_ui import output_guardrail_demo
from config.llm_config import LLAMA_SECURITY_FAMILY

if LLAMA_SECURITY_FAMILY:
    print('Llama Security Family: ENABLED')
    demos = [basic_demo, rag_demo, leak_demo, input_guardrail_demo, output_guardrail_demo]
    demo_names = ['Direct', 'RAG', 'Prompt Leak', 'Input Guardrails', 'Output Guardrails']

else:
    print('Llama Security Family: DISABLED')
    demos = [basic_demo, rag_demo, leak_demo]
    demo_names = ['Direct', 'RAG', 'Prompt Leak']


demo = gr.TabbedInterface(demos, demo_names)

demo.launch()
