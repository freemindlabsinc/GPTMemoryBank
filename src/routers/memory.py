import os
from fastapi import APIRouter, Query, status
from azure.storage.queue import QueueServiceClient
from typing import Optional, List
from models.memory_models import (Message, Resource)
from models.endpoint_models import (RememberRequest, RememberJob, QuestionResponse)
from pydantic import BaseModel, Field
from typing import List
from services.config import get_configured
from services.logger import setup_logger
from services import elasticsearch_utils as esutils
from llama_index.vector_stores import ElasticsearchStore
from llama_index import ServiceContext
from llama_index.llms import OpenAI
from llama_index.embeddings import HuggingFaceEmbedding    
from llama_index import VectorStoreIndex
from llama_index.storage.storage_context import StorageContext
from llama_index import SimpleDirectoryReader

# Retrieve environment variables for Azure Storage and Queue names
AZURE_STORAGE_CONNECTION_STRING = get_configured('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
IMPORT_RESOURCE_QUEUE = get_configured('IMPORT_RESOURCE_QUEUE', is_required=True)
SAVE_MESSAGE_QUEUE = get_configured('SAVE_MESSAGE_QUEUE', is_required=True)

# Create a new router for the memory related endpoints
router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    #responses={404: {"description": "Not found"}},
)

# Create a QueueServiceClient object that will be used to send messages to the queue
queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# -------------------- remember --------------------
@router.post("/remember", 
             response_model=List[RememberJob], 
             status_code=status.HTTP_200_OK,
             summary="Stores a memory in the memory bank", 
             response_description="The list of jobs created to process the storing of the messages and resources",
             operation_id="storeMemory")
async def remember(request: RememberRequest) -> List[RememberJob]:
    """
    Memorize messages and resources in the memory bank XXX
    
    
    """
    responses = []
    
    # Send each message to the queue
    queue_client = queue_service.get_queue_client(SAVE_MESSAGE_QUEUE)                
    for message in request.messages:        
        resp = queue_client.send_message(message.model_dump_json() )  # Send the JSON message
        
        responses.append(
            RememberJob(
                status="queued", 
                job_id=resp.id, 
                collection=message.collection, 
                status_message="Message queued for processing."))         
        
        print(f"Sent message {message.text} to queue {queue_client.queue_name} with id {resp.id}")
        
    # Send each resource to the queue
    queue_client = queue_service.get_queue_client(IMPORT_RESOURCE_QUEUE)                
    for res in request.resources:                
        resp = queue_client.send_message(res.model_dump_json())  # Send the JSON URL
        
        responses.append(
            RememberJob(
                status="queued", 
                job_id=resp.id, 
                collection=res.collection, 
                status_message="Resource queued for processing."))
        
        print(f"Sent url {res.address} to queue {queue_client.queue_name} with id {resp.id}")

    return responses

# -------------------- ask --------------------
@router.get("/ask", 
            summary="Queries the memory bank", 
            operation_id="queryMemory")
async def ask(
    question: str = Query(..., description="The question to ask"), 
    collections: Optional[str] = Query(None, description="The collections to query (comma separated).")) -> QuestionResponse:
    # Implementation of LLamaIndex query goes here
    index = await esutils.get_index()
       
    query_engine = index.as_query_engine()
    resp = query_engine.query(question)    

    list = []    
    for source_node in resp.source_nodes:        
        list.append(source_node.text)
        
    # create a QuestionResponse object with the source nodes data
    colls = collections.split(",") if collections else ['*'] 
    qr = QuestionResponse(
        answer=resp.response, 
        collections=colls, 
        confidence=0.9, 
        links=list)    
    
    return qr  