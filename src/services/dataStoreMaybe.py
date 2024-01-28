from loguru import logger
from models.api import QueryResponse, QueryRequest, QueryResult
from models.models import DocumentChunkMetadata, DocumentChunkWithScore

async def get_datastore():
    return None

async def query(query: str, top_k: int = 3):
    res1 = QueryResult(
        query="Who is Alessandro Federici?", 
        results=[
            DocumentChunkWithScore(
                score=1.0, 
                text="Alessandro Federici is the developer who created this project.", 
                metadata=DocumentChunkMetadata(
                    source="",
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
                    source="",
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
                    source="",
                    source_id="",
                    url = "",
                    created_at="1/3/2024",
                    author="",
                    document_id="",
                    )
                )
        ])
             
    return QueryResponse(results=[res1, res2])
    