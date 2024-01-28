import collections
from loguru import logger
from fastapi import APIRouter, HTTPException, Query, Body
from azure.storage.queue import QueueServiceClient
from models.api import QueryRequest, QueryResponse
from models.endpoint_models import QuestionResponse
from services.config import get_option
from services import elasticsearch_utils as esutils

# Retrieve environment variables for Azure Storage and Queue names
AZURE_STORAGE_CONNECTION_STRING = get_option('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
IMPORT_RESOURCE_QUEUE = get_option('IMPORT_RESOURCE_QUEUE', is_required=True)
SAVE_MESSAGE_QUEUE = get_option('SAVE_MESSAGE_QUEUE', is_required=True)

# Create a new router for the memory related endpoints
router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    #responses={404: {"description": "Not found"}},
)

# Create a QueueServiceClient object that will be used to send messages to the queue
queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# ------------------------ Enpoint ------------------------
@router.post("/query", response_model=QueryResponse,)
async def query_main(
    request: QueryRequest = Body(...),
):
    try:
        results = []

        index = await esutils.get_index()
    
    
    
        query_engine = index.as_query_engine()
        resp = query_engine.query("question")    
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

        #results = await datastore.query(
        #    request.queries,
        #)
        return QueryResponse(results=results)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Service Error")



