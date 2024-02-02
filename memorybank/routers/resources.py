import os, uuid, hashlib
import shutil
from fastapi_injector import Injected
from loguru import logger
from typing import Optional
from fastapi import File, Form, HTTPException, Depends, Body, UploadFile, Request
from fastapi import APIRouter
from typing import Optional, List

from llama_index import Document
from llama_index import SimpleDirectoryReader

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.models.api import (UpsertRequest, UpsertResponse)

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
    
    try:
        docs = _convert_uploaded_files_to_documents(files)
            
        ids = [generate_id(
            doc=doc, 
            prefix="DOC_", 
            # generates the id by MD5ing the actual text
            generator = lambda: hashlib.md5(doc.text.encode('utf-8')).hexdigest()) for doc in docs]
        
        res = await memory_store.upsert(docs)            
        successful_ids = [id for id, success in zip(ids, res) if success]
            
        return UpsertResponse(ids=successful_ids)  
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"upsert_files: {files.count}")

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
        
        # Generates the ids for the documents using a GUID
        ids = [generate_id(doc=doc, prefix="DOC_", generator=lambda: str(uuid.uuid4())) for doc in docs]
        
        res = await memory_store.upsert(docs)
        
        successful_ids = [id for id, success in zip(ids, res) if success]
        return UpsertResponse(ids=successful_ids)
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"Upsert: {request}")
 
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
    # Downloads from YouTube, Google Drive, etc.
    raise HTTPException(status_code=500, detail="NotImplementedYet")
    
# ------------------------ Enpoint ------------------------
@router.delete(
    "/",    
    response_model=UpsertResponse,
)
def delete(document_ids: List[str]):
    # Deletes the documents from the memory store
    raise HTTPException(status_code=500, detail="NotImplementedYet")

# ------------------------ Internals ------------------------
def generate_id(doc : Document, prefix: str, generator: str):
    tmp = generator()
    doc.doc_id = prefix + tmp
    
    return doc.doc_id

def _store_uploaded_file(path_name: str, file: UploadFile):
    logger.info(f"Upserting file: {file.filename}")
        
    if os.path.exists(path_name) == False:
        os.mkdir(path_name)        
        
    file_location = f"{path_name}/{file.filename}"
    
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    return file_location

def _convert_uploaded_files_to_documents(files: List[UploadFile]) -> List[Document]:    
    # Stores the files in a temp directory. Hack or the way?
    path_name = "/uploads"
    try:
        for file in files:        
            _store_uploaded_file(path_name, file)
            
        # Parses the files in the temp directory and returns a List[Document] from the files
        docs = SimpleDirectoryReader(path_name).load_data()
    
        return docs
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:        
        if (os.path.exists(path_name)):
            shutil.rmtree(path_name)
    
    