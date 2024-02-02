from typing import List
from fastapi_injector import Injected
from loguru import logger
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from datetime import datetime

from llama_index import Response, VectorStoreIndex
from llama_index.schema import NodeWithScore

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.models.api import (QueryResponse, QueryRequest, QueryResult)
from memorybank.models.models import (DocumentChunk, DocumentChunkMetadata, Source)
from memorybank.abstractions.index_factory import IndexFactory

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    #dependencies=[Depends(validate_token)],
    )

def _get_document_chunks(nodes: List[NodeWithScore]) -> List[DocumentChunk]:
    nowstr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    chunks = []
    for node in nodes:                        
        chunk =  DocumentChunk(
                            text=node.get_text(),
                            score=node.get_score(),                                                
                            metadata=DocumentChunkMetadata(
                                author="",
                                document_id=node.node.ref_doc_id or "unspecified",
                                source=Source.file,
                                source_id=node.node_id or "unspecified",
                                url=node.metadata.get("file_name", "unspecified"),
                                created_at=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                start_char_idx=node.node.start_char_idx or -1,
                                end_char_idx=node.node.end_char_idx or -1,
                            )
                )
        chunks.append(chunk)
        
    return chunks

# ------------------------ Enpoint ------------------------
@router.post(
    "/query",
    response_model=QueryResponse,
    # NOTE: We are describing the shape of the API endpoint input due to a current limitation in parsing arrays of objects from OpenAPI schemas. This will not be necessary in the future.
    description="Accepts search query objects array each with query and optional filter. Break down complex questions into sub-questions. Refine results by criteria, e.g. time / source, don't do this often. Split queries if ResponseTooLargeError occurs.",
)
async def query(
    http_request: Request,
    request: QueryRequest = Body(...),    
    memory_store: MemoryStore = Injected(MemoryStore)
):
    try:        
        results = await memory_store.query(request.queries)
                  
        response = QueryResponse(results=results)
        
        return response
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Query: {request.queries}")
        
# ------------------------ Enpoint ------------------------
@router.post(
    "/retrieve",
    response_model=QueryResponse,
    # NOTE: We are describing the shape of the API endpoint input due to a current limitation in parsing arrays of objects from OpenAPI schemas. This will not be necessary in the future.
    description="Accepts search query objects array each with query and optional filter. Break down complex questions into sub-questions. Refine results by criteria, e.g. time / source, don't do this often. Split queries if ResponseTooLargeError occurs.",
)
async def retrieve(
    http_request: Request,
    request: QueryRequest = Body(...),   
    memory_store: MemoryStore = Injected(MemoryStore) 
):
    try: 
        raise NotImplementedError("Not implemented yet")        
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Summarize: {request.queries}") 


@router.post(
    "/summarize",
    response_model=QueryResponse,
    # NOTE: We are describing the shape of the API endpoint input due to a current limitation in parsing arrays of objects from OpenAPI schemas. This will not be necessary in the future.
    description="Accepts search query objects array each with query and optional filter. Break down complex questions into sub-questions. Refine results by criteria, e.g. time / source, don't do this often. Split queries if ResponseTooLargeError occurs.",       
)
async def summarize(
    http_request: Request,
    request: QueryRequest = Body(...),    
):
    try: 
        raise NotImplementedError("Not implemented yet")        
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Summarize: {request.queries}") 
    
# ------------------------ Future enpoints ------------------------
 # /summarize
 # /chat

