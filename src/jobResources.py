import time
import os
import json
from azure.storage.queue import QueueServiceClient
from ..models.memory_models import (Message, Resource)
from azure.core.exceptions import ResourceExistsError

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
IMPORT_RESOURCE_QUEUE = os.getenv('IMPORT_RESOURCE_QUEUE')

queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
try:
    # create the queue if it doesn't exist
    queue_service.create_queue(IMPORT_RESOURCE_QUEUE)
except ResourceExistsError:
    # Resource exists
    pass    

def import_resource(resource: Resource):
    # For now we just print a message
    print(f"Importing {resource.address} in collection {resource.collection}")
    
def process_queue():
    queue_client = queue_service.get_queue_client(queue=IMPORT_RESOURCE_QUEUE)
    messages = queue_client.receive_messages(max_messages=10)
    
    for message in messages:        
        resource_dict = json.loads(message.content)  # Convert the JSON string to a dictionary
        resource = Resource(**resource_dict)  # Create a Resource object from the dictionary
        
        import_resource(resource)
        
        queue_client.delete_message(message)
    
if __name__ == "__main__":
    process_queue()    