import os
from fastapi import APIRouter, Query
from azure.storage.queue import QueueServiceClient
from typing import Optional, List
from models.memory_models import (Message, Resource)
from models.endpoint_models import (RememberRequest, RememberJob, QuestionResponse)
from pydantic import BaseModel, Field
from typing import List
import json

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
IMPORT_RESOURCE_QUEUE = os.getenv('IMPORT_RESOURCE_QUEUE')
SAVE_MESSAGE_QUEUE = os.getenv('SAVE_MESSAGE_QUEUE')

queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# Endpoints

@router.post("/remember", response_model=List[RememberJob], summary="Stores a memory in the memory bank", operation_id="storeMemory")
async def remember(request: RememberRequest) -> List[RememberJob]:
    responses = []
    for message in request.messages:        
        queue_client = queue_service.get_queue_client(SAVE_MESSAGE_QUEUE)        
        resp = queue_client.send_message(message.model_dump_json() )  # Send the JSON message
        
        responses.append(
            RememberJob(
                status="queued", 
                job_id=resp.id, 
                collection=message.collection, 
                status_message="Message queued for processing."))         
        
        print(f"Sent message {message.text} to queue {queue_client.queue_name} with id {resp.id}")
        
    for res in request.resources:        
        queue_client = queue_service.get_queue_client(IMPORT_RESOURCE_QUEUE)                
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
    collections: Optional[List[str]] = Query(..., description="The collections to query")) -> List[QuestionResponse]:
    # Implementation of LLamaIndex query goes here
    # For now, return a placeholder response
    return [
        QuestionResponse(answer=f"The answer to '{question}' is '42'.", collections=collections, confidence=0.1, links=["https://en.wikipedia.org/wiki/42_(number)", "https://en.wikipedia.org/wiki/hitchhikers_guide_to_the_galaxy"]),
        QuestionResponse(answer=f"The other answer is '{question}' is 'maybe'.", collections=collections, confidence=0.2, links=["https://en.wikipedia.org/wiki/Maybe", "https://cdn1.vectorstock.com/i/1000x1000/56/45/maybe-stamp-vector-16595645.jpg"]),
        ]