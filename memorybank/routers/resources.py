import os, uuid, hashlib
import tempfile
from pathlib import Path
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
        docs = _convert_uploaded_files_to_chunks(files)                    
        
        res = await memory_store.upsert(docs)
        
        ids = []
        for doc in docs:
            id = doc.id_                
            
        return UpsertResponse(ids=ids)  
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:
        logger.info(f"upsert_files:")

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
        #ids = [generate_id(doc=doc, prefix="DOC_", generator=lambda: str(uuid.uuid4())) for doc in docs]
        
        ids = [doc.metadata["file_name"] for doc in docs]
        
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
    #doc.id_ = doc.metadata["file_name"]    
    #hash = hashlib.md5(doc.text.encode('utf-8')).hexdigest()
    #doc.doc_id = prefix + tmp
    #doc.metadata["doc_hash"] = hash
    
    return doc.id_

def store_bytes_as_temp_file(byte_data):
    # Create a temporary file and write the byte data to it
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(byte_data)
    
    # Return the name of the temporary file
    return temp_file.name
    
def store_uploaded_files(files: List[UploadFile]) -> List[str]:
    file_names = []
    for file in files:
        file_location = store_bytes_as_temp_file(file.file.read())
        file_names.append(file_location)
        
        logger.info(f"Generated temporary file: {file.filename} at {file_location}")
        
    return file_names

def _convert_uploaded_files_to_chunks(files: List[UploadFile]) -> List[Document]:    
    # Stores the files in a temp directory. Hack or the way?
    try:        
        file_names = store_uploaded_files(files)
            
        # Parses the files in the temp directory and returns a List[Document] from the files
        chunks = SimpleDirectoryReader(
            input_files=file_names,
            filename_as_id=True,
            exclude_hidden=False).load_data(
                show_progress=True,
                num_workers=1,)
    
        return chunks
    
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
    finally:        
        # delete temporary files
        for file in file_names:
            os.remove(file)    