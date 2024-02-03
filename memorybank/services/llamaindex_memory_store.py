from typing import Dict, List, Optional
from injector import inject
from llama_index import Response
from memorybank.abstractions.memory_store import MemoryStore
from memorybank.models.api import QueryResult
from memorybank.models.models import Document, DocumentMetadataFilter, Query
from memorybank.settings.app_settings import AppSettings
from memorybank.abstractions.index_factory import IndexFactory

class LlamaIndexMemoryStore(MemoryStore):
    @inject
    def __init__(self, app_settings: AppSettings, index_factory: IndexFactory):
        self.app_settings = app_settings
        self.index_factory = index_factory
        pass

    def _get_formatted_sources(self, response: Response, length: int = 100) -> str:
        """Get formatted sources text."""
        texts = []
        for source_node in response.source_nodes:
            #fmt_text_chunk = truncate_text(source_node.node.get_content(), length)
            doc_id = source_node.node.node_id or "None"
            file_name = source_node.node.metadata["file_name"]
            source_text = f"> Source (Doc id: {doc_id}): {file_name}"
            texts.append(source_text)
        return "\n\n".join(texts)

    async def query(self, queries: List[Query]) -> List[QueryResult]:        
        #print(self.app_settings.azure_openai.api_base)
        
        idx = await self.index_factory.get_vector_index()
        
        query_engine = idx.as_query_engine()
        
        responses = []
        for qry in queries:
            response = await query_engine.aquery(qry.text)#, top_k=qry.top_k, filter=qry.filter)
            responses.append(QueryResult(
                query=qry,
                answer=response.response,
                formatted_sources = self._get_formatted_sources(response),
            ))
                
        return responses 
    
    async def upsert(self, documents: List[Document]) -> List[str]:
        """
        Takes in a list of list of document chunks and inserts them into the database.
        Return a list of document ids.
        """
        idx = await self.index_factory.get_vector_index()
        res = idx.refresh_ref_docs(documents=documents)
        
        return res

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        return True
    