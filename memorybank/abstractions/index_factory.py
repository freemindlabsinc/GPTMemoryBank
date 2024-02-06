from llama_index import VectorStoreIndex
from abc import ABC, abstractmethod

class IndexFactory(ABC):
    @abstractmethod
    async def get_vector_index(self) -> VectorStoreIndex:
        raise NotImplementedError
    

