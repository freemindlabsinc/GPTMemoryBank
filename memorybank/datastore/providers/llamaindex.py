from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from injector import inject
from memorybank.datastore.datastore import DataStore
from memorybank.models.api import QueryResult
from memorybank.models.models import Document, DocumentChunk, DocumentChunkMetadata, DocumentChunkWithScore, DocumentMetadataFilter, Query, QueryWithEmbedding
from memorybank.settings.app_settings import AppSettings

class LlamaIndexDataStore(DataStore):
    @inject
    def __init__(self, app_settings: AppSettings):
        super().__init__(app_settings)        
        pass

    async def _upsert(self, chunks: Dict[str, List[DocumentChunk]]) -> List[str]:
        """
        Takes in a list of list of document chunks and inserts them into the database.
        Return a list of document ids.
        """

        return []

    async def _query(self, queries: List[QueryWithEmbedding]) -> List[QueryResult]:        
        print(self.app_settings.azure_openai.api_base)
        
        from memorybank.datastore.datafaker import _fake_results
        return _fake_results() 

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        return True
    