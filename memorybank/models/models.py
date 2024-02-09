from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# should me moved elsewhere
from llama_index.vector_stores.types import VectorStoreQueryMode
from llama_index.response_synthesizers.type import ResponseMode        

class Source(str, Enum):
    email = "email"
    file = "file"
    chat = "chat"

class DocumentMetadata(BaseModel):
    source: Optional[Source] = None
    source_id: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None

class DocumentChunkMetadata(DocumentMetadata):
    document_id: Optional[str] = None
    start_char_idx: Optional[int] = None
    end_char_idx: Optional[int] = None

class DocumentChunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: DocumentChunkMetadata
    score: float

class Document(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[DocumentMetadata] = None

class DocumentMetadataFilter(BaseModel):
    document_id: Optional[str] = None
    source: Optional[Source] = None
    source_id: Optional[str] = None
    author: Optional[str] = None
    start_date: Optional[str] = None  # any date string format
    end_date: Optional[str] = None  # any date string format

class Query(BaseModel):
    text: str
    filter: Optional[DocumentMetadataFilter] = None
    top_k: Optional[int] = 3,
    response_mode: Optional[ResponseMode] = ResponseMode.COMPACT_ACCUMULATE,
    query_mode: Optional[VectorStoreQueryMode]  = VectorStoreQueryMode.DEFAULT,

class QueryResult(BaseModel):
    query: Query
    answer: Optional[str] = None
    formatted_sources: Optional[str] = None
    links: Optional[List[DocumentChunk]] = None