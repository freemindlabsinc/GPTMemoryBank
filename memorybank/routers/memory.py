from typing import List
from loguru import logger
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from datetime import datetime

from llama_index import Response, VectorStoreIndex
from llama_index.schema import NodeWithScore

from memorybank.datastore.datastore import DataStore
from memorybank.models.api import (QueryResponse, QueryRequest, QueryResult)
from memorybank.models.models import (DocumentChunkWithScore, DocumentChunkMetadata, Source)
from memorybank.services.index_factory import IndexFactory

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    #dependencies=[Depends(validate_token)],
    )

# -- to centralize ---
async def _get_vector_index(http_request: Request) -> VectorStoreIndex:
    injector = http_request.state.injector
    indexFactory = injector.get(IndexFactory)
    
    index = await indexFactory.get_index() 
    
    return index

def _get_document_chunks(nodes: List[NodeWithScore]) -> List[DocumentChunkWithScore]:
    nowstr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    chunks = []
    for node in nodes:                        
        chunk =  DocumentChunkWithScore(
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
):
    try:        
        index = await _get_vector_index(http_request) 
        query_engine = index.as_query_engine()
        
        results = []
        for query in request.queries:                        
            qry_response = query_engine.query(query.text)
                        
            doc_chunks = _get_document_chunks(qry_response.source_nodes)
            
            result = QueryResult(                
                query = query.text,
                answer = qry_response.response,
                formatted_sources = qry_response.get_formatted_sources(),
                links = doc_chunks)
            
            results.append(result)
        
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
):
    try:        
        index = await _get_vector_index(http_request) 
        
        results = []
        for query in request.queries:                                    
            retriever = index.as_retriever(
                similarity_top_k=query.top_k,
                
            )        
            nodes_with_score = retriever.retrieve(query.text)
                        
            doc_chunks = _get_document_chunks(nodes_with_score)
            
            result = QueryResult(                
                query = query.text,
                #answer = "See references below",
                #formatted_sources = "none",
                links = doc_chunks)
            
            results.append(result)
        
        response = QueryResponse(results=results)
        return response
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Retrieve: {request.queries}")        


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
        #index = await _get_vector_index(http_request) 
        #
        #results = []
        #for query in request.queries:                                    
        #    retriever = index.as_retriever(
        #        similarity_top_k=query.top_k,
        #        
        #    )        
        #    nodes_with_score = retriever.retrieve(query.text)
        #                
        #    doc_chunks = _get_document_chunks(nodes_with_score)
        #    
        #    result = QueryResult(                
        #        query = query.text,
        #        #answer = "See references below",
        #        #formatted_sources = "none",
        #        links = doc_chunks)
        #    
        #    results.append(result)
        #
        #response = QueryResponse(results=results)
        #return response
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Summarize: {request.queries}") 
    
    
    
    
    
    
    
# ------------------------ Future enpoints ------------------------
 # /summarize
 # /chat

