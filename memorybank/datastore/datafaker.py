from memorybank.models.api import QueryResult
from memorybank.models.models import Document, DocumentChunk, DocumentChunkMetadata, DocumentChunkWithScore, DocumentMetadataFilter, Query, QueryWithEmbedding
from abc import ABC, abstractmethod
from typing import List

def _fake_results() -> List[QueryResult]:
    res1 = QueryResult(
        query="Who is Alessandro Federici?", 
        results=[
            DocumentChunkWithScore(
                score=1.0, 
                text="Alessandro Federici is the developer who created this project.", 
                metadata=DocumentChunkMetadata(
                    source="chat",
                    source_id="",
                    url = "",
                    created_at="1/1/2023",                    
                    author="",
                    document_id="",
                    )
                )
        ])
            
    res2 = QueryResult(
        query="How old is Alessandro Federici?", 
        results=[
            DocumentChunkWithScore(
                score=1.0, 
                text="Alessandro Federici is 48.", 
                metadata=DocumentChunkMetadata(
                    source="email",
                    source_id="",
                    url = "",
                    created_at="2/2/2022",
                    author="",
                    document_id="",
                    )
                ),
            
            DocumentChunkWithScore(
                score=1.0, 
                text="Alessandro Federici is 47.", 
                metadata=DocumentChunkMetadata(
                    source="chat",
                    source_id="",
                    url = "",
                    created_at="1/3/2024",
                    author="",
                    document_id="",
                    )
                )
        ])
            
    return [res1, res2]