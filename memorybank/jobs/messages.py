import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from models.memory_models import (Message)
from services.config import get_option
from services.logger import setup_logger
from services.queue_utils import setup_queue, process_queue
from elasticsearch import AsyncElasticsearch
import llama_index
from llama_index import (ServiceContext, SimpleDirectoryReader, VectorStoreIndex, Document)
from llama_index.llms import OpenAI
from llama_index.embeddings import HuggingFaceEmbedding    
from llama_index.vector_stores import ElasticsearchStore
from llama_index.storage.storage_context import StorageContext
from memorybank.services import indexUtils as esutils


# Get the Azure storage connection string and the save message queue from environment variables
AZURE_STORAGE_CONNECTION_STRING = get_option('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
SAVE_MESSAGE_QUEUE = get_option('SAVE_MESSAGE_QUEUE', is_required=True)

DELETE_QUEUE = False
REMOVE_MESSAGES = True

# Set up logging
logger = setup_logger(__name__)

# Functionality

async def main():
    index = await esutils.get_index()
    
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