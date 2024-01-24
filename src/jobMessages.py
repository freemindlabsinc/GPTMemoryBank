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

# Get the Azure storage connection string and the save message queue from environment variables
AZURE_STORAGE_CONNECTION_STRING = get_configured('AZURE_STORAGE_CONNECTION_STRING', is_required=True)
SAVE_MESSAGE_QUEUE = get_configured('SAVE_MESSAGE_QUEUE', is_required=True)

OPENAI_API_KEY = get_configured("OPENAI_API_KEY", is_required=True)
OPENAI_CHAT_MODEL = get_configured("OPENAI_CHAT_MODEL", is_required=True)
OPENAI_MODEL_TEMPERATURE = float(get_configured("OPENAI_MODEL_TEMPERATURE", 0.2))
EMBEDDING_MODEL = get_configured("EMBEDDING_MODEL", is_required=True)

ES_URL = get_configured("ES_URL", "https://localhost:9200")
ES_CERTIFICATE_FINGERPRINT = get_configured("ES_CERTIFICATE_FINGERPRINT", is_required=True)
ES_USERNAME = get_configured("ES_USERNAME", is_required=True)
ES_PASSWORD = get_configured("ES_PASSWORD", is_required=True)
ES_DEFAULT_INDEX = get_configured("ES_DEFAULT_INDEX", "default")

DELETE_QUEUE = False
REMOVE_MESSAGES = False

# Set up logging
logger = setup_logger(__name__)

# Stuff

async def connect_to_elasticsearch():
    # Instantiate the Elasticsearch client right away to check we can connect
    
    es_client = AsyncElasticsearch(
        [ES_URL],
        #ssl_assert_fingerprint=ES_CERTIFICATE_FINGERPRINT,
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        verify_certs=False
    )
    
    await es_client.info() # this connects to the cluster and gets its version
    
    return es_client

def load_data(es_client):
    
    # Creates a reader for the /data folder        
    #if bulk_data:
    #    documents = SimpleDirectoryReader("./data").load_data(show_progress=True)

    # Creates the ES vector store
    es_vector_store = ElasticsearchStore(
        index_name=ES_DEFAULT_INDEX,
        es_client=es_client,        
    )

    # Service ctx for debug    
    llm = OpenAI(model=OPENAI_CHAT_MODEL, temperature=OPENAI_MODEL_TEMPERATURE)        
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

    service_context = ServiceContext.from_defaults(
        # callback_manager=callback_manager, 
        llm=llm,
        embed_model=embed_model
    )
    
    llama_index.set_global_handler("simple")    

    storage_context = StorageContext.from_defaults(vector_store=es_vector_store)
    
    index = VectorStoreIndex.from_vector_store(
        vector_store=es_vector_store, 
        service_context=service_context)        
    
    return index;

# Functionality

async def main():
    es_client = await connect_to_elasticsearch()
    index = load_data(es_client)
    
    def save_message(resource_dict):
        message = Message(**resource_dict)
        # For now we just print a message
        doc = Document(
            text=message.text,
            metadata={"collection": message.collection, "author": "user" },
        )
        
        index.insert(doc)
        
        print(f"Saving message '{message.text}' in collection {message.collection}")    
    
    queue_service = setup_queue(AZURE_STORAGE_CONNECTION_STRING, SAVE_MESSAGE_QUEUE, DELETE_QUEUE)
    process_queue(queue_service, SAVE_MESSAGE_QUEUE, save_message, logger, REMOVE_MESSAGES)
    
if __name__ == "__main__":
    asyncio.run(main())