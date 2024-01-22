import time
import os
from azure.storage.queue import QueueServiceClient
from models.memory_models import (Message, Resource)

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
IMPORT_RESOURCE_QUEUE = os.getenv('IMPORT_RESOURCE_QUEUE')

queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def import_resource(url: str):
    # This is where you'd put the code to execute the message.
    # For now, we'll just print it.
    print(f"Importing from {url}")
    
def check_for_messages():
    queue_client = queue_service.get_queue_client(queue=IMPORT_RESOURCE_QUEUE)
    messages = queue_client.receive_messages(max_messages=10)
    
    for message in messages:
        import_resource(message.content)
        queue_client.delete_message(message)
    
if __name__ == "__main__":
    check_for_messages()    