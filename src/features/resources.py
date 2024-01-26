from services.file import get_document_from_file
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Depends, Body, UploadFile
from models.api import (QueryResponse, QueryRequest, QueryResult, UpsertRequest, UpsertResponse)
from  models.models import (DocumentChunkWithScore, DocumentChunkMetadata, DocumentMetadata, Source)

resources_app = FastAPI(
    title="Resources API",
    description="An API to store resources in a memory bank.",
    version="0.0.1",
    servers=[{"url": "https://your-app-url.com"}],
    #dependencies=[Depends(validate_token)],
    )

# ------------------------ Enpoint ------------------------
@resources_app.post(
    "/upsert-file",
    response_model=UpsertResponse,
)
async def upsert_file(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
):
    try:
        metadata_obj = (
            DocumentMetadata.parse_raw(metadata)
            if metadata
            else DocumentMetadata(source=Source.file)
        )
    except:
        metadata_obj = DocumentMetadata(source=Source.file)

    document = await get_document_from_file(file, metadata_obj)

    try:
        #ids = await datastore.upsert([document])
        ids = ["0001", "0002"]
        return UpsertResponse(ids=ids)
        pass
    except Exception as e:
        #logger.error(e)
        raise HTTPException(status_code=500, detail=f"str({e})")

# ------------------------ Enpoint ------------------------
@resources_app.post(
    "/upsert",
    response_model=UpsertResponse,
)
async def upsert(
    request: UpsertRequest = Body(...),
):
    try:
        #ids = await datastore.upsert(request.documents)
        ids = ["0001", "0002"]        
        return UpsertResponse(ids=ids)
    except Exception as e:
        #logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")

