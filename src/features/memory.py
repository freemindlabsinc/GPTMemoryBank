from fastapi import FastAPI, File, Form, HTTPException, Depends, Body, UploadFile
from models.api import (QueryResponse, QueryRequest, QueryResult)
from  models.models import (DocumentChunkWithScore, DocumentChunkMetadata)

memory_app = FastAPI(
    title="Query API",
    description="A retrieval API for querying and filtering documents based on natural language queries and metadata.",
    version="0.0.1",
    servers=[{"url": "https://your-app-url.com"}],
    #dependencies=[Depends(validate_token)],
    )

# ------------------------ Enpoint ------------------------
@memory_app.post(
    "/query",
    response_model=QueryResponse,
    # NOTE: We are describing the shape of the API endpoint input due to a current limitation in parsing arrays of objects from OpenAPI schemas. This will not be necessary in the future.
    description="Accepts search query objects array each with query and optional filter. Break down complex questions into sub-questions. Refine results by criteria, e.g. time / source, don't do this often. Split queries if ResponseTooLargeError occurs.",
)
async def query(
    request: QueryRequest = Body(...),
):
    try:        
        #results = await datastore.query(
        #    request.queries,
        #)
        res1 = QueryResult(
            query="test", 
            results=[DocumentChunkWithScore(score=0.0, text="test", metadata=DocumentChunkMetadata())])
                
        return QueryResponse(results=[res1])
    except Exception as e:
        #logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
 