import asyncio

from models.memory_models import (Message)
from internal.config import get_configured
from internal.logger import setup_logger
from internal.queue_utils import setup_queue, process_queue
from elasticsearch import AsyncElasticsearch
import llama_index
from llama_index import (ServiceContext, SimpleDirectoryReader, VectorStoreIndex, Document)
from llama_index.llms import OpenAI
from llama_index.embeddings import HuggingFaceEmbedding    
from llama_index.vector_stores import ElasticsearchStore
from llama_index.storage.storage_context import StorageContext
from internal import elasticsearch_utils as esutils

# Get the Azure storage connection string and the save message queue from environment variables
AZURE_STORAGE_CONNECTION_STRING = get_configured('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
SAVE_MESSAGE_QUEUE = get_configured('SAVE_MESSAGE_QUEUE', is_required=True)

DELETE_QUEUE = False
REMOVE_MESSAGES = False

# Set up logging
logger = setup_logger(__name__)

# Functionality

async def main():
    index = esutils.get_index()
    
    def index_message(resource_dict):
        message = Message(**resource_dict)
        # For now we just print a message
        doc = Document(
            text=message.text,
            metadata={"collection": message.collection, "author": "user" },
        )
        
        index.insert(doc)
        
        print(f"Saving message '{message.text}' in collection {message.collection}")    
    
    queue_service = setup_queue(AZURE_STORAGE_CONNECTION_STRING, SAVE_MESSAGE_QUEUE, DELETE_QUEUE)
    process_queue(queue_service, SAVE_MESSAGE_QUEUE, index_message, logger, REMOVE_MESSAGES)
    
if __name__ == "__main__":
    asyncio.run(main())