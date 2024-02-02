import os, uuid, hashlib
from fastapi_injector import Injected
from loguru import logger
from typing import Optional
from fastapi import File, Form, HTTPException, Depends, Body, UploadFile, Request
from fastapi import APIRouter
from typing import Optional, List

from llama_index import Document, VectorStoreIndex
from llama_index import SimpleDirectoryReader
from memorybank.abstractions.memory_store import MemoryStore

from memorybank.models.api import (UpsertRequest, UpsertResponse)
from memorybank.abstractions.index_factory import IndexFactory

router = APIRouter(
    prefix="/resources",
    tags=["resources"],
    #dependencies=[Depends(validate_token)],
    )

# ------------------------ Enpoint ------------------------
@router.post(
    "/upsert-files",
    response_model=UpsertResponse,
)
async def upsert_files(
    http_request: Request,
    files: List[UploadFile] = File(...),
    metadata: Optional[str] = Form(None),
    memory_store: MemoryStore = Injected(MemoryStore),):
    
    # Stores the files in a temp directory. Hack or the way?
    ids = []
    for file in files:        
        logger.info(f"Upserting file: {file.filename}")
        tmp_dir = _store_uploaded_file(file)
            
    # Parses the files in the temp directory and returns a List[Document] from the files
    docs = SimpleDirectoryReader(tmp_dir).load_data()
    
    ids = []
    for doc in docs:
        # create an md 5 hash of file.filename    
        id = hashlib.md5(file.filename.encode('utf-8')).hexdigest()                    
        doc.doc_id = "FILE_" + id
        ids.append(doc.doc_id)        
    
    res = await memory_store.upsert(docs)
            
    return UpsertResponse(ids=ids)
# ------------------------ Enpoint ------------------------


# ------------------------ Enpoint ------------------------
@router.post(
    "/upsert-docs",
    response_model=UpsertResponse,
)
async def upsert_docs(
    http_request: Request,
    request: UpsertRequest = Body(...),    
    memory_store: MemoryStore = Injected(MemoryStore),
):
    try:        
        docs = request.documents
        
        ids = []
        for doc in docs:
            # create an md 5 hash of file.filename    
            id = str(uuid.uuid4())
            doc.doc_id = "DOC_" + id
            ids.append(doc.doc_id)        
    
        res = await memory_store.upsert(docs)
        
        return UpsertResponse(ids=ids)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Upsert: {request}")



 # ------------------------ Future enpoints ------------------------
 # //upsert_from
 
 # write a version of upsert that takes an array of files

# ------------------------ Enpoint ------------------------
@router.post(
    "/upsert-from",
    response_model=UpsertResponse,
)
def upsert_from(
    http_request: Request,
    urls: List[str] = File(...),
    metadata: Optional[str] = Form(None),    
):
    return UpsertResponse(ids=["NotImplementedYet"])


    
# ------------------------ Enpoint ------------------------
@router.delete(
    "/",    
    response_model=UpsertResponse,
)
def delete(document_ids: List[str]):
    return UpsertResponse(ids=["NotImplementedYet"])

# ------------------------ Internals ------------------------

def _store_uploaded_file(file: UploadFile):
    path_name = "uploads"
    
    if os.path.exists(path_name) == False:
        os.mkdir(path_name)        
    file_location = f"{path_name}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    return path_name