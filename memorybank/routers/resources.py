from injector import Injector
from llama_index import Document, VectorStoreIndex
from loguru import logger
from memorybank.datastore.datastore import DataStore
from memorybank.services.file import get_document_from_file
from typing import Optional
from fastapi import File, Form, HTTPException, Depends, Body, UploadFile, Request
from memorybank.models.api import (UpsertRequest, UpsertResponse)
from memorybank.models.models import (DocumentMetadata, Source)
from fastapi import APIRouter
from typing import Optional, List
from llama_index import SimpleDirectoryReader
import os                
from memorybank.services.indexUtils import IndexFactory
from memorybank.services.fileuploads import store_uploaded_file

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
    try:
        tmp_dir = store_uploaded_file(file)        
        docs = SimpleDirectoryReader(tmp_dir).load_data()
        
        index = await get_vector_index(http_request)    
                             
        res = index.insert(docs[0])
                
        return UpsertResponse(ids=[docs[0].doc_id])
     
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"str({e})")
    
    finally:
        xx = file.filename
        logger.info(f"Upsert_file: {xx}")

async def get_vector_index(http_request: Request) -> VectorStoreIndex:
    injector = http_request.state.injector
    indexFactory = injector.get(IndexFactory)
    index = await indexFactory.get_index() 
    return index

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
        index = get_vector_index(http_request)
        
        ids = await index.insert(request.documents)
        
        return UpsertResponse(ids=ids)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Upsert: {request}")

 # ------------------------ Future enpoints ------------------------
 # //upsert_from