import time
import json
import os
from azure.storage.queue import QueueServiceClient
from ..models.memory_models import (Message, Resource)
from azure.core.exceptions import ResourceExistsError

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
SAVE_MESSAGE_QUEUE = os.getenv('SAVE_MESSAGE_QUEUE')

queue_service = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
try:
    # create the queue if it doesn't exist
    queue_service.create_queue(SAVE_MESSAGE_QUEUE)
except ResourceExistsError:
    # Resource exists
    pass    

def save_message(message: Message):    
    # For now we just print a message
    print(f"Saving message '{message.text}' in collection {message.collection}")
    
def process_queue():
    queue_client = queue_service.get_queue_client(queue=SAVE_MESSAGE_QUEUE)
    messages = queue_client.receive_messages(max_messages=10)
    
    for message in messages:
        user_message_dict = json.loads(message.content)
        user_message = Message(**user_message_dict)
        
        save_message(user_message)
        
        queue_client.delete_message(message)
    
if __name__ == "__main__":
    process_queue()    