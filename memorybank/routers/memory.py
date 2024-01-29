from llama_index import VectorStoreIndex
from loguru import logger
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from memorybank.datastore.datastore import DataStore
from memorybank.models.api import (QueryResponse, QueryRequest, QueryResult)
from memorybank.models.models import (DocumentChunkWithScore, DocumentChunkMetadata)
from memorybank.services.indexUtils import IndexFactory

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    #dependencies=[Depends(validate_token)],
    )

# -- to centralize ---
async def get_vector_index(http_request: Request) -> VectorStoreIndex:
    injector = http_request.state.injector
    indexFactory = injector.get(IndexFactory)
    
    index = await indexFactory.get_index() 
    
    return index

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
):
    try:        
        index = await get_vector_index(http_request) 
        query_engine = index.as_query_engine()
        
        results = []
        for qry in request.queries:                        
            response = query_engine.query(qry.query)
            
            srcs = []
            for x in response.source_nodes:
                y =  DocumentChunkWithScore(
                        text=response.response,
                        score=1,                                                
                        metadata=DocumentChunkMetadata()
                )
                srcs.append(y)
            
            result = QueryResult(
                query=qry.query,
                results = srcs)
            
            results.append(result)
        
        response = QueryResponse(results=results)
        return response
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Query: {request.queries}")
 
 # ------------------------ Future enpoints ------------------------
 # /summarize
 # /chat
 
 