from llama_index.core.llms import LLM
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.retrievers import BaseRetriever

from abc import ABC, abstractmethod

class RAGFactory(ABC):       
    @abstractmethod
    def get_vector_index(self) -> VectorStoreIndex:                
        raise NotImplementedError
    
    @abstractmethod
    def get_chat_engine(self) -> BaseChatEngine:
        raise NotImplementedError
        
    @abstractmethod
    def get_retriever(self,
                      top_k: float, 
                      vector_store_query_mode: VectorStoreQueryMode) -> BaseRetriever:
        raise NotImplementedError
    
    @abstractmethod
    def get_query_engine(self,
                         top_k: float, 
                         vector_store_query_mode: VectorStoreQueryMode,
                         response_mode: ResponseMode) -> BaseQueryEngine:
        raise NotImplementedError
