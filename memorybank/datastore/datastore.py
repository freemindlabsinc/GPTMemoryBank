import asyncio
from memorybank.models.api import QueryResult
from memorybank.models.models import Document, DocumentChunk, DocumentChunkMetadata, DocumentChunkWithScore, DocumentMetadataFilter, Query, QueryWithEmbedding
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from injector import Injector, inject
from memorybank.settings.app_settings import AppSettings

class DataStore(ABC):
    @inject
    def __init__(self, app_settings: AppSettings):
        self.app_settings = app_settings
        
    async def query(self, queries: List[Query]) -> List[QueryResult]:
        """
        Takes in a list of queries and filters and returns a list of query results with matching document chunks and scores.
        """
        value = self.app_settings
        # get a list of of just the queries from the Query list
        query_texts = [query.text for query in queries]
        
        # TODO needs ab abstraction for embeddings
        query_embeddings = [] #get_embeddings(query_texts)
        query_embeddings.append([0.1, 0.2, 0.3])
        # hydrate the queries with embeddings
        queries_with_embeddings = [
            QueryWithEmbedding(**query.dict(), embedding=embedding)
            for query, embedding in zip(queries, query_embeddings)
        ]
        return await self._query(queries_with_embeddings)
    
    async def upsert(self, 
                     documents: List[Document], 
                     chunk_token_size: Optional[int] = None) -> List[str]:
        """
        Takes in a list of documents and inserts them into the database.
        First deletes all the existing vectors with the document id (if necessary, depends on the vector db), then inserts the new ones.
        Return a list of document ids.
        """
        # Delete any existing vectors for documents with the input document ids
        await asyncio.gather(
            *[
                self.delete(
                    filter=DocumentMetadataFilter(
                        document_id=document.id,
                    ),
                    delete_all=False,
                )
                for document in documents
                if document.id
            ]
        )

        # FIXME this is to be fixed        
        # chunks = get_document_chunks(documents, chunk_token_size)

        return await self._upsert(chunks)
        return []            
    
    @abstractmethod
    async def _upsert(self, chunks: Dict[str, List[DocumentChunk]]) -> List[str]:
        """
        Takes in a list of list of document chunks and inserts them into the database.
        Return a list of document ids.
        """

        raise NotImplementedError

    @abstractmethod
    async def _query(self, queries: List[QueryWithEmbedding]) -> List[QueryResult]:
        """
        Takes in a list of queries with embeddings and filters and returns a list of query results with matching document chunks and scores.
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