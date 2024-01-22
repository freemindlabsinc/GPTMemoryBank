from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},    
)

fake_memory = [ ]

class StoreRequest(BaseModel):
    memory: str
    topic: str = None
    
class StoreResponse(BaseModel):    
    response: str
    
class QueryRequest(BaseModel):
    query: str
    topic: str = None    
    
class QueryResponse(BaseModel):
    response: str

@router.post("/save", summary="Saves a memory in the memory bank", operation_id="saveMemory")
async def save_memory(store_request: StoreRequest):
    """
    Saves a memory in the memory bank
    """
    fake_memory.append(store_request.memory)
    return store_request;

@router.get("/read", summary="Retrieves memories from the memory bank", operation_id="readMemory")
async def get_memories(
    query: str = Query(description="The query")) -> str:
    """
    Retrieves memories from the memory bank
    """
    return "fake_memory";

