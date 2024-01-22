from pydantic import BaseModel, Field
from typing import (Optional, List)

class Message(BaseModel):
    """
    A message to be stored in the memory bank.
    """
    text: str = Field(..., description="The message to be stored.")
    collection: Optional[str] = Field('default', description="The collection where the message will be stored.")

class Resource(BaseModel):
    """
    A resource to be imported and stored in the memory bank.
    """
    address: str = Field(..., description="The URL to access the resource.")
    collection: Optional[str] = Field('default', description="The collection where the resource will be stored.")
