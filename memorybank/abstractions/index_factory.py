from llama_index.core.llms import LLM
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.callbacks import CallbackManager

from abc import ABC, abstractmethod

class IndexFactory(ABC):
    @abstractmethod
    async def get_vector_index(self) -> VectorStoreIndex:
        raise NotImplementedError
    
    def get_llm(self) -> LLM:
        raise NotImplementedError
    
    def get_embed_model(self) -> BaseEmbedding:
        raise NotImplementedError
    
    def get_callback_manager(self) -> CallbackManager:
        raise NotImplementedError