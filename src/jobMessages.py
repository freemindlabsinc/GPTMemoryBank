from models.memory_models import (Message)
from internal.config import get_configured
from internal.logger import setup_logger
from internal.queue_utils import setup_queue, process_queue

# Get the Azure storage connection string and the save message queue from environment variables
AZURE_STORAGE_CONNECTION_STRING = get_configured('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
SAVE_MESSAGE_QUEUE = get_configured('SAVE_MESSAGE_QUEUE', is_required=True)

DELETE_QUEUE = False
REMOVE_MESSAGES = False

# Set up logging
logger = setup_logger(__name__)

# Functionality
def save_message(resource_dict):    
    message = Message(**resource_dict)    
    # For now we just print a message
    print(f"Saving message '{message.text}' in collection {message.collection}")
    
if __name__ == "__main__":
    queue_service = setup_queue(AZURE_STORAGE_CONNECTION_STRING, SAVE_MESSAGE_QUEUE, DELETE_QUEUE)
    process_queue(queue_service, SAVE_MESSAGE_QUEUE, save_message, logger, REMOVE_MESSAGES)