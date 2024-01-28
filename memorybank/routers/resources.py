from loguru import logger
from memorybank.services.file import get_document_from_file
from typing import Optional
from fastapi import File, Form, HTTPException, Depends, Body, UploadFile
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
    finally:
        logger.info(f"Upsert_file: {document}")

# ------------------------ Enpoint ------------------------
@router.post(
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
    finally:
        logger.info(f"Upsert: {request}")

 # ------------------------ Future enpoints ------------------------
 # //upsert_from