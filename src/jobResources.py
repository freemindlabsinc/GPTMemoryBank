from models.memory_models import (Resource)
from internal import url_utils
from internal.config import get_configured
from internal.logger import setup_logger
from internal.queue_utils import setup_queue, process_queue

# Read the configuration
AZURE_STORAGE_CONNECTION_STRING = get_configured('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
IMPORT_RESOURCE_QUEUE = get_configured('IMPORT_RESOURCE_QUEUE', is_required=True)

DELETE_QUEUE = False
REMOVE_MESSAGES = False

# Set up logging
logger = setup_logger(__name__)

# Functionality
def import_resource(resource_dict):    
    resource = Resource(**resource_dict)
    
    resource_type = url_utils.get_service_from_url(resource.address)
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
    
if __name__ == "__main__":
    queue_service = setup_queue(AZURE_STORAGE_CONNECTION_STRING, IMPORT_RESOURCE_QUEUE, DELETE_QUEUE)
    process_queue(queue_service, IMPORT_RESOURCE_QUEUE, import_resource, logger, REMOVE_MESSAGES)