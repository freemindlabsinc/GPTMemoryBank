from memorybank.models.api import QueryResult
from memorybank.models.models import Document, DocumentMetadataFilter, Query, QueryResult
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from injector import inject

class MemoryStore(ABC):
    @abstractmethod
    async def query(self, queries: List[Query]) -> List[QueryResult]:
        """
        Takes in a list of queries and filters and returns a list of query results with matching document chunks and scores.
        """
        
        raise NotImplementedError
    
    @abstractmethod
    async def upsert(self, 
                     documents: List[Document], 
                     chunk_token_size: Optional[int] = None) -> List[str]:
        """
        Takes in a list of documents and inserts them into the database.
        First deletes all the existing vectors with the document id (if necessary, depends on the vector db), then inserts the new ones.
        Return a list of document ids.
        """
        raise NotImplementedError
        
    @abstractmethod
    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        """
        Removes vectors by ids, filter, or everything in the datastore.
        Multiple parameters can be used at once.
        Returns whether the operation was successful.
        """
        raise NotImplementedError