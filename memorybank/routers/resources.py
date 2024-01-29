from llama_index import Document
from loguru import logger
from memorybank.datastore.datastore import DataStore
from memorybank.services.file import get_document_from_file
from typing import Optional
from fastapi import File, Form, HTTPException, Depends, Body, UploadFile, Request
from memorybank.models.api import (UpsertRequest, UpsertResponse)
from memorybank.models.models import (DocumentMetadata, Source)
from fastapi import APIRouter
from typing import Optional, List

router = APIRouter(
    prefix="/resources",
    tags=["resources"],
    #dependencies=[Depends(validate_token)],
    )

# ------------------------ Enpoint ------------------------
@router.post(
    "/upsert-file",
    response_model=UpsertResponse,
)
async def upsert_file(
    http_request: Request,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),    
):
    
    doc = Document(file= file, metadata=metadata)
    
    from memorybank.services.elasticsearch_utils import get_index
    index = await get_index()
            
        
    try:
        metadata_obj = (
            DocumentMetadata.parse_raw(metadata) # NOTE look into the depecated parse_raw        
            if metadata
            else DocumentMetadata(source=Source.file)
        )
    except Exception as e:
        metadata_obj = DocumentMetadata(source=Source.file)
    
    document = await get_document_from_file(file, metadata_obj)

    try:
        datastore = http_request.state.injector.get(DataStore)
        
        ids = await datastore.upsert([document])
        
        return UpsertResponse(ids=ids)       
     
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"str({e})")
    
    finally:
        logger.info(f"Upsert_file: {document}")

# ------------------------ Enpoint ------------------------
@router.post(
    "/upsert",
    response_model=UpsertResponse,
)
async def upsert(
    http_request: Request,
    request: UpsertRequest = Body(...),
):
    try:
        datastore = http_request.state.injector.get(DataStore)
        ids = await datastore.upsert(request.documents)
        
        return UpsertResponse(ids=ids)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Upsert: {request}")

 # ------------------------ Future enpoints ------------------------
 # //upsert_from