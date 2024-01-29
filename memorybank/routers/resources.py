import hashlib
import shutil
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


async def get_vector_index(http_request: Request) -> VectorStoreIndex:
    injector = http_request.state.injector
    indexFactory = injector.get(IndexFactory)
    
    index = await indexFactory.get_index() 
    
    return index

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
        # FIXME: This is a hack to get the file converted in a llamaindex Document
        tmp_dir = store_uploaded_file(file)        
        docs = SimpleDirectoryReader(tmp_dir).load_data()
        # create an md 5 hash of file.filename
        for doc in docs:
            hash = hashlib.md5(file.filename.encode('utf-8')).hexdigest()                    
            #doc.id = "DOC_" + hashlib.md5(file.filename.encode('utf-8')).hexdigest()
            doc.doc_id = "DOC_" + hash
            #doc.id_ = "DOC_" + hash
        
        # Gets the veftor index (more in the future)
        index = await get_vector_index(http_request)                                 
        
        # Upserts the documents
        res = index.refresh_ref_docs(docs)
                
        return UpsertResponse(ids=[docs[0].doc_id])
     
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"str({e})")
    
    finally:  
        # removes the temporary directory and the file
        shutil.rmtree(tmp_dir) 
        logger.info(f"Upsert_file: {file.filename}")

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
        index = await get_vector_index(http_request)
        
        ids = []
        for doc in request.documents:
            hash = hashlib.md5(doc.id.encode('utf-8')).hexdigest()        
            newDoc = Document(
                doc_id = "DOC_" + hash,
                text = doc.text,
            )
            
            res = index.refresh_ref_docs([newDoc])            
        
        return UpsertResponse(ids=ids)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Upsert: {request}")

 # ------------------------ Future enpoints ------------------------
 # //upsert_from