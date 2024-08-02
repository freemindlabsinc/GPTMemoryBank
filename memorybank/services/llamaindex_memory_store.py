from elasticsearch import NotFoundError
from loguru import logger
from typing import Dict, List, Optional
from injector import inject

from llama_index.core import (Response, Settings)
from llama_index.core.readers.file.base import SimpleDirectoryReader
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.retrievers import BaseRetriever

from llama_index.core.retrievers import (VectorIndexRetriever)
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import (RetrieverQueryEngine)
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core.response_synthesizers.type import ResponseMode

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.models.api import QueryResult
from memorybank.models.models import Document, DocumentMetadataFilter, Query
from memorybank.settings.app_settings import AppSettings
from memorybank.abstractions.rag_factory import RAGFactory

class LlamaIndexMemoryStore(MemoryStore):
    @inject
    def __init__(self, app_settings: AppSettings, rag_factory: RAGFactory):
        self.app_settings = app_settings
        self.rag_factory = rag_factory
        pass

    def _get_formatted_sources(self, response: Response, length: int = 100) -> str:
        """Get formatted sources text."""
        texts = []
        if response.source_nodes is None:
            return ""
        
        for source_node in response.source_nodes:
            #fmt_text_chunk = truncate_text(source_node.node.get_content(), length)
            doc_id = source_node.node.node_id or "None"
            file_name = source_node.node.metadata["file_name"]
            source_text = f"> Source (Doc id: {doc_id}): {file_name}"
            texts.append(source_text)
        return "\n\n".join(texts)

    async def query(self, query: Query) -> QueryResult:        
        logger.debug(f"Querying '{query}'.")
        try:                                    
            query_engine = self.rag_factory.get_query_engine(
                top_k=query.top_k,
                vector_store_query_mode=query.query_mode,
                response_mode=query.response_mode                
            )
            response = await query_engine.aquery(query.text)
                        
            logger.debug(f"Query response: {response}")
        
            return QueryResult(
                query=query,
                answer=response.response,
                formatted_sources = self._get_formatted_sources(response),
            )
        except NotFoundError as e:
            return QueryResult(
                query=query,
                answer="It appears you have not yet uploaded any file. Please upload some files so I can help you.",
                formatted_sources = "No data",
            )
        except Exception as e:
            return QueryResult(
                query=query,
                answer=f"Something went wrong. [{e}]",
                formatted_sources = "No data",
            )
    
    async def upload(self, file_names: List[str], chunk_token_size: Optional[int] = None) -> List[str]:        
        logger.debug(f"Uploading files: {file_names}")
        
        uploaded_documents = SimpleDirectoryReader(            
                input_files=file_names,
                filename_as_id=True,
                #file_extractor=
                exclude_hidden=False).load_data(
                    show_progress=True)
                            
        res = await self.upsert(uploaded_documents)
        return res
        
    
    async def upsert(self, documents: List[Document]) -> List[str]:
        """
        Takes in a list of list of document chunks and inserts them into the database.
        Return a list of document ids.
        """        
        logger.debug(f"Upserting {len(documents)} documents...")
        try:
            idx = self.rag_factory.get_vector_index()
            
            # refresh_ref_docs calls insert which then runs the conversion pipeline            
            res = idx.refresh_ref_docs(
                documents=documents,
                update_kwargs={"delete_kwargs": {"delete_from_docstore": True}})
                                    
            # get all ids from documents
            ids = []
            for doc in documents:
                ids.append(doc.doc_id)
            
            logger.debug(f"Upserted {len(ids)} chunks: {ids} from {len(documents)} documents.")
                        
            return ids
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            return []

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        raise NotImplementedError("Delete not implemented yet.")
    
        idx = await self.rag_factory.get_vector_index()
        
        return True
    