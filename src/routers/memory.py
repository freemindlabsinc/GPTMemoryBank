import os
from fastapi import APIRouter, Query
from azure.storage.queue import QueueServiceClient
from typing import Optional, List
from models.memory_models import (Message, Resource)
from models.endpoint_models import (RememberRequest, RememberJob, QuestionResponse)
from pydantic import BaseModel, Field
from typing import List
import json

# Retrieve environment variables for Azure Storage and Queue names
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
IMPORT_RESOURCE_QUEUE = os.getenv('IMPORT_RESOURCE_QUEUE')
SAVE_MESSAGE_QUEUE = os.getenv('SAVE_MESSAGE_QUEUE')

# Create a new router for the memory related endpoints
router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

# Create a QueueServiceClient object that will be used to send messages to the queue
queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# Endpoints

# This endpoint accepts a POST request with a RememberRequest object
# It sends each message and resource in the request to a separate Azure Queue for processing
# It returns a list of RememberJob objects, each representing the status of a message or resource that was sent to the queue
@router.post("/remember", response_model=List[RememberJob], summary="Stores a memory in the memory bank", operation_id="storeMemory")
async def remember(request: RememberRequest) -> List[RememberJob]:
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

@router.get("/ask", summary="Queries the memory bank", operation_id="queryMemory")
async def ask(
    question: str = Query(..., description="The question to ask"), 
    collections: Optional[str] = Query(None, description="The collections to query (comma separated).")) -> List[QuestionResponse]:
    # Implementation of LLamaIndex query goes here
    # For now, return a placeholder response
    colls = collections.split(",") if collections else ['*'] 
    return [
        QuestionResponse(answer=f"The answer to '{question}' is '42'.", collections=colls, confidence=0.9, links=["https://en.wikipedia.org/wiki/42_(number)", "https://en.wikipedia.org/wiki/hitchhikers_guide_to_the_galaxy"]),
        QuestionResponse(answer=f"The other answer is '{question}' is 'maybe 1420'.", collections=colls, confidence=0.8, links=["https://en.wikipedia.org/wiki/Maybe", "https://cdn1.vectorstock.com/i/1000x1000/56/45/maybe-stamp-vector-16595645.jpg"]),
        ]    