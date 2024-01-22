import os
from typing import Optional, List
from models.memory_models import (Message, Resource)
from pydantic import BaseModel, Field

class RememberRequest(BaseModel):
    """
    Stores messages and resources in the memory bank.
    """
    messages: List[Message] = Field(..., description="The list of messages to be stored.")
    resources: List[Resource] = Field(..., description="The list of resources to be stored.")

class RememberJob(BaseModel):
    """
    The job created to process the storing of a message or resource.
    """
    status: str = Field(..., description="The status of the operation. Will be 'queued' if the operation was successful.")
    job_id: str = Field(..., description="The id of the job.")
    collection: str = Field(..., description="The collection where the message or resource will to be stored.")
    status_message: str = Field(..., description="A status message.")    

class QuestionResponse(BaseModel):
    """
    The response to a question asked over the information stored in the memory bank.
    """
    answer: str = Field(..., description="The answer to the question.")
    confidence: float = Field(..., description="The confidence of the answer.")
    collections: Optional[List[str]] = Field(None, description="The collections that were queried.")    
    links: Optional[List[str]] = Field(None, description="The list of resources that grounded this response.")    
