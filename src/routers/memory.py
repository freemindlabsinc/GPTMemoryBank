import os
from fastapi import APIRouter, Query
from azure.storage.queue import QueueServiceClient
from typing import Optional, List
from models.memory_models import (Message, Resource)
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
IMPORT_RESOURCE_QUEUE = os.getenv('IMPORT_RESOURCE_QUEUE')
SAVE_MESSAGE_QUEUE = os.getenv('SAVE_MESSAGE_QUEUE')

queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# Model
class RememberRequest(BaseModel):
    """
    Stores messages and resources in the memory bank.
    """
    messages: List[Message] = Field(..., description="The list of messages to be stored.")
    urls: List[Resource] = Field(..., description="The list of resources to be stored.")

class RememberResponse(BaseModel):
    """
    The response to a remember request.
    """
    status: str = Field(..., description="The status of the operation. Will be 'queued' if the operation was successful.")
    job_id: str = Field(..., description="The id of the job.")
    collection: str = Field(..., description="The collection where the message or URL was stored.")

# Endpoints

@router.post("/remember", response_model=List[RememberResponse], summary="Stores a memory in the memory bank", operation_id="storeMemory")
async def remember(request: RememberRequest):
    responses = []
    for message in request.messages:
        queue_name = SAVE_MESSAGE_QUEUE
        queue_client = queue_service.get_queue_client(queue_name)
        resp = queue_client.send_message(message.text)
        responses.append({"status": "queued", "job_id": resp.id, "collection": message.collection})
        print(f"Sent message {message.text} to queue {queue_name} with id {resp.id}")
        
    for url in request.urls:
        queue_name = IMPORT_RESOURCE_QUEUE
        queue_client = queue_service.get_queue_client(queue_name)
        resp = queue_client.send_message(url.address)
        responses.append({"status": "queued", "job_id": resp.id, "collection": url.collection})
        print(f"Sent url {url.address} to queue {queue_name} with id {resp.id}")

    return responses

@router.get("/ask", summary="Queries the memory bank", operation_id="queryMemory")
async def ask(question: str = Query(..., description="The question to ask"), collections: Optional[List[str]] = Query(None, description="The collections to query")):
    # Implementation of LLamaIndex query goes here
    # For now, return a placeholder response
    return {"answer": "This is a placeholder answer"}