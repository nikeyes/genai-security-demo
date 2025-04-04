from llama_index.core import PromptTemplate, Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock

from config.llm_config import LLMConfig
from prompts import RAG_INPUT_SENSITIVITY_CHECK_SYSTEM_PROMPT

# from llama_index.readers.web import SimpleWebPageReader


class Rag:
    SIMILARITY_CUTOFF_THRESHOLD_PERCENT = 30

    PROMPT_TEMPLATE = (
        'We have provided context information below. \n'
        '---------------------\n'
        '{context_str}'
        '\n---------------------\n'
        'Given this information, please answer the question: {query_str}\n'
    )

    def __init__(self, strict_security: bool = True, score_threshold=SIMILARITY_CUTOFF_THRESHOLD_PERCENT):
        # Initialize LLMConfig
        self.llm_config = LLMConfig(debug=False)
        self.llm_config.initialize()

        # Get model ID from config
        bedrock_model_id = self.llm_config.BEDROCK_MODEL_ID

        llm = Bedrock(
            region_name='eu-central-1',
            model=bedrock_model_id,
            profile_name='data-dev',
        )

        embed_model = BedrockEmbedding(
            region_name='eu-central-1',
            model_name='cohere.embed-multilingual-v3',
            profile_name='data-dev',
        )

        # global settings
        Settings.llm = llm
        Settings.embed_model = embed_model
        self.index_folder = './vector_index/default'

        # load documents
        local_data = SimpleDirectoryReader(input_dir='src/data', required_exts=['.txt']).load_data()
        # web_data = SimpleWebPageReader(html_to_text=True).load_data(
        #     ["https://nikeyes.github.io/Principios-de-un-Open-Space-y-viajar-con-ni%C3%B1os-en-coche/"]
        # )

        if strict_security:
            local_data = self.filter_out_sensitive_data_from(local_data)

        # indexing documents using vector store
        self.vector_index = VectorStoreIndex.from_documents(local_data, show_progress=True)

        self.query_engine = RetrieverQueryEngine(
            retriever=(self.vector_index.as_retriever(similarity_top_k=3)),
            node_postprocessors=[(SimilarityPostprocessor(similarity_cutoff=score_threshold / 100))],
        )
        self.query_engine.update_prompts({'response_synthesizer:text_qa_template': (PromptTemplate(self.PROMPT_TEMPLATE))})

        # Store Vector Index
        # self.vector_index.storage_context.persist(persist_dir=self.index_folder)

    def rag_response(self, query):
        response = self.query_engine.query(query)

        for i, node_with_score in enumerate(response.source_nodes, 1):
            print(f'\nNode {i}:')
            print(f'Score: {node_with_score.score:.4f}')
            print(f'Node ID: {node_with_score.node.id_}')
            print(f'Text Preview: {node_with_score.node.text[:100]}...')
            print('-' * 80)

        return response

    def filter_out_sensitive_data_from(self, local_data):
        # Use the bedrock LLM from config instead of creating a new one
        llm = self.llm_config.get_bedrock_llm()
        filtered = []
        for doc in local_data:
            assessment = llm.invoke(RAG_INPUT_SENSITIVITY_CHECK_SYSTEM_PROMPT, doc.text)
            print(f'{assessment} determined for: {doc}')
            if assessment == 'not_sensitive':
                filtered.append(doc)

        return filtered
