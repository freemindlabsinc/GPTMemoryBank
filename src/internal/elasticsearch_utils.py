import os
from elasticsearch import AsyncElasticsearch
from internal.config import get_configured
from elasticsearch import AsyncElasticsearch
import llama_index
from llama_index import (ServiceContext, SimpleDirectoryReader, VectorStoreIndex, Document)
from llama_index.llms import OpenAI
from llama_index.llms import OpenAI
from llama_index.embeddings import HuggingFaceEmbedding    
from llama_index.vector_stores import (ElasticsearchStore)
from llama_index.storage.storage_context import (StorageContext)
from llama_index.storage.docstore import (SimpleDocumentStore)
from llama_index.storage.index_store import (SimpleIndexStore)
from llama_index import (
    load_index_from_storage,
    load_indices_from_storage,
    load_graph_from_storage,
)
from llama_index.data_structs.data_structs import IndexStruct
from llama_index.storage.docstore import RedisDocumentStore
from llama_index.storage.index_store import RedisIndexStore

OPENAI_API_KEY = get_configured("OPENAI_API_KEY", is_required=True)
OPENAI_CHAT_MODEL = get_configured("OPENAI_CHAT_MODEL", is_required=True)
OPENAI_MODEL_TEMPERATURE = float(get_configured("OPENAI_MODEL_TEMPERATURE", 0.2))
EMBEDDING_MODEL = get_configured("EMBEDDING_MODEL", is_required=True)

REDIS_SERVER = get_configured("REDIS_SERVER", "localhost")
REDIS_PORT = int(get_configured("REDIS_PORT", 6379))

ES_URL = get_configured("ES_URL", "https://localhost:9200")
ES_CERTIFICATE_FINGERPRINT = get_configured("ES_CERTIFICATE_FINGERPRINT", is_required=True)
ES_USERNAME = get_configured("ES_USERNAME", is_required=True)
ES_PASSWORD = get_configured("ES_PASSWORD", is_required=True)
ES_DEFAULT_INDEX = get_configured("ES_DEFAULT_INDEX", "default")

def create_elasticsearch_client() -> AsyncElasticsearch:
    # Instantiate the Elasticsearch client
    es_client = AsyncElasticsearch(
        [ES_URL],
        #ssl_assert_fingerprint=ES_CERTIFICATE_FINGERPRINT,
        basic_auth=(ES_USERNAME, ES_PASSWORD),
        verify_certs=False,        
    )
    es_client.options(headers={"user-agent": "memory-bank/0.0.1"})        
    
    return es_client

def create_service_context() -> ServiceContext:
    llm = OpenAI(model=OPENAI_CHAT_MODEL, temperature=OPENAI_MODEL_TEMPERATURE)        
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    
    service_context = ServiceContext.from_defaults(
        # callback_manager=callback_manager, 
        llm=llm,
        embed_model=embed_model,
    )
    
    return service_context

async def get_index() -> VectorStoreIndex:
    # Instantiate the Elasticsearch client
    es_client = create_elasticsearch_client()    
    service_context = create_service_context()
    
    persist_directory = "./.persistDir"
    es_vector_store = ElasticsearchStore(
        index_name=ES_DEFAULT_INDEX,
        es_client=es_client    
    )
                              
    if (not os.path.exists(persist_directory)):
        storage_context = StorageContext.from_defaults(vector_store=es_vector_store)#, persist_dir=persist_directory)
        
        docs = SimpleDirectoryReader("./docs").load_data(show_progress=True)    
        index = VectorStoreIndex.from_documents(docs, storage_context=storage_context, show_progress=True)
        
        storage_context.persist(persist_dir=persist_directory)                
    else:
        storage_context = StorageContext.from_defaults(            
            persist_dir=persist_directory, 
            vector_store=es_vector_store)
        
        index = load_index_from_storage(storage_context, show_progress=True)
        pass
    
    #storage_context = StorageContext.from_defaults(
    #    vector_store=VectorStoreIndex.from_vector_store(vector_store= es_vector_store, 
    #                                                    service_context=service_context),
    #    #docstore=SimpleDocumentStore.from_persist_dir(persist_dir=persist_directory),        
    #    #index_store=SimpleIndexStore.from_persist_dir(persist_dir=persist_directory)
    #)
        
    #storage_context.persist(persist_dir=persist_directory)      
    
    #index = load_index_from_storage(storage_context=storage_context)
    #from_vector_store(
    #    vector_store=es_vector_store,         
    #    service_context=service_context)          
    
    
    return index