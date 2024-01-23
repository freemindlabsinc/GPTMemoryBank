import json
import time
from azure.storage.queue import QueueServiceClient
from models.memory_models import (Message, Resource)
from azure.core.exceptions import ResourceExistsError
import internal.urlUtils as uu
from internal.config import get_configured
from internal.logger import setup_logger

# Read the configuration
AZURE_STORAGE_CONNECTION_STRING = get_configured('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
IMPORT_RESOURCE_QUEUE = get_configured('IMPORT_RESOURCE_QUEUE', is_required=True)

DELETE_QUEUE = False
REMOVE_MESSAGES = False

# Set up logging
logger = setup_logger(__name__)

# Create a QueueServiceClient object that will be used to create a queue client
queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

if DELETE_QUEUE:
    deleted = False
    try:
        queue_service.delete_queue(IMPORT_RESOURCE_QUEUE)        
        deleted = True
    except Exception as e:
        pass   
    
    logger.debug(f"Delete queue {IMPORT_RESOURCE_QUEUE} returned {deleted}.")
    exit(1)    
    
try:            
    # create the queue if it doesn't exist
    logger.debug(f"Creating queue {IMPORT_RESOURCE_QUEUE}...")        
    queue_service.create_queue(IMPORT_RESOURCE_QUEUE)    
    logger.debug(f"Created queue {IMPORT_RESOURCE_QUEUE}.")
    
except ResourceExistsError:
    # Resource exists
    logger.debug(f"Queue {IMPORT_RESOURCE_QUEUE} already exists.")
    pass    

# Functionality
def import_resource(resource: Resource):    
    resource_type = uu.get_service_from_url(resource.address)
    if resource_type == uu.Service.Unsupported:
        # For now we just log a message
        logger.warn(f"Unsupported resource type for {resource.address}")
        return
    elif resource_type == uu.Service.YouTube:
        # Handle YouTube URL
        logger.info(f"YouTube URL: {resource.address}")
    elif resource_type == uu.Service.GoogleDrive:
        # Handle Google Drive URL
        logger.info(f"Google Drive URL: {resource.address}")
    elif resource_type == uu.Service.WebAddress:
        # Handle Web Address
        logger.info(f"Web Address: {resource.address}")
    else:
        # This should never happen unless more services are added to the Service enum
        logger.error(f"Unexpected resource type for {resource.address}")
    
def process_queue():
    queue_client = queue_service.get_queue_client(queue=IMPORT_RESOURCE_QUEUE)
    messages = queue_client.receive_messages(max_messages=10)
    
    count = 0
    for message in messages:   
        try:
            resource_dict = json.loads(message.content)  # Convert the JSON string to a dictionary
            resource = Resource(**resource_dict)  # Create a Resource object from the dictionary
        
            import_resource(resource)        
            count += 1
            if REMOVE_MESSAGES:
                queue_client.delete_message(message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            #queue_client.delete_message(message)
            #raise e
    
    logger.info(f"Processed {count} messages")
    
if __name__ == "__main__":
    process_queue()    