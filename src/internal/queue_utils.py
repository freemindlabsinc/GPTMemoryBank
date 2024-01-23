import json
from azure.storage.queue import QueueServiceClient
from azure.core.exceptions import ResourceExistsError

def setup_queue(connection_string, queue_name, delete_queue=False):
    # Create a QueueServiceClient object that will be used to create a queue client
    queue_service = QueueServiceClient.from_connection_string(connection_string)

    if delete_queue:
        try:
            queue_service.delete_queue(queue_name)
            print(f"Deleted queue {queue_name}.")
        except Exception as e:
            print(f"Failed to delete queue {queue_name}. Error: {e}")

    try:
        # create the queue if it doesn't exist
        queue_service.create_queue(queue_name)
        print(f"Created queue {queue_name}.")
    except ResourceExistsError:
        # Resource exists
        print(f"Queue {queue_name} already exists.")

    return queue_service

def process_queue(queue_service, queue_name, import_resource, logger, remove_messages=False):
    queue_client = queue_service.get_queue_client(queue=queue_name)
    messages = queue_client.receive_messages(max_messages=10)
    
    count = 0
    for message in messages:   
        try:
            resource_dict = json.loads(message.content)  # Convert the JSON string to a dictionary
            resource = import_resource(resource_dict)  # Create a Resource object from the dictionary
        
            count += 1
            if remove_messages:                
                queue_client.delete_message(message)
                logger.info(f"Deleted message {message.id}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            #queue_client.delete_message(message)
            #raise e
    
    logger.info(f"Processed {count} messages")