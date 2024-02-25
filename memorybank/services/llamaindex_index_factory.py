from loguru import logger
from elasticsearch import AsyncElasticsearch
from injector import inject
from llama_index.core.settings import Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.callbacks import (CallbackManager, LlamaDebugHandler)
from memorybank.settings.app_settings import AppSettings
from memorybank.settings.embeddings_settings import EmbeddingType
from memorybank.abstractions.index_factory import IndexFactory

class LlamaIndexIndexFactory(IndexFactory):
    """
    Configures and returns a LlamaIndex VecorStoreIndex instance.
    """
    @inject
    def __init__(self, app_settings: AppSettings):
        """
        Constructor for the LlamaIndexIndexFactory class.
        """
        self.callback_manager = self._create_callback_manager(app_settings)
        # FIX ME: This is a hack to get the callback manager to other classes
        Settings.callback_manager = self.callback_manager
        
        self.embed_model = self._create_embedding_model(app_settings)                
        self.llm = self._create_llm(app_settings)        
        
        self.vector_store = self._create_vector_store(app_settings)
        self.storage_context = self._create_storage_context(app_settings)        
        
        self.vector_index = self._create_vector_index(app_settings)            
    
    def _create_embedding_model(self, app_settings: AppSettings
                               ) -> BaseEmbedding:            
        """
        Creates and returns the configured embedding model.
        """
        logger.debug("Creating embedding model...")
        
        #model_to_use = "mistral"    
        #embed_model = OllamaEmbedding(
        #    model_name=self.model_to_use,
        #    base_url="http://localhost:11434",
        #    #embed_batch_size=1,
        #    callback_manager=Settings.callback_manager)
                                      
        #return embed_model
        
        model_name = app_settings.embeddings.model
        model_type = app_settings.embeddings.type
            
        
        if model_type == EmbeddingType.huggingface:    
            embed_model = HuggingFaceEmbedding(model_name=model_name, 
                                               callback_manager=self.callback_manager)
            
        elif model_type == EmbeddingType.azureai:
            embed_model = AzureOpenAIEmbedding(
                model=app_settings.azure_openai.model,
                deployment_name=app_settings.azure_openai.deployment_id,
                api_key=app_settings.azure_openai.api_key,
                azure_endpoint=app_settings.azure_openai.api_base,
                api_version=app_settings.azure_openai.api_version,
                callback_manager=Settings.callback_manager
            )
        else:        
            # FIXME finish / instantiate OpenAI
            raise Exception("Embedding type not supported.")
        
        logger.debug(f"Embedding model created: {embed_model}")
        
        return embed_model    
    
    def _create_callback_manager(self, app_settings: AppSettings) -> CallbackManager:
        # Add LlamaIndex simple observability
        Settings.global_handler = "simple"
        
        logger.debug("Creating callback manager...")
        
        llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        return CallbackManager([llama_debug])
        
    def _create_llm(self, app_settings: AppSettings) -> LLM:
        logger.debug("Creating LLM...")
        #llm = Ollama(model="llama2", request_timeout=60.0, base_url="http://localhost:11434")
        
        if app_settings.openai.api_key is not None:
            ai_config = app_settings.openai
            
            llm = OpenAI(model= ai_config.model, temperature=ai_config.temperature, callback_manager=Settings.callback_manager)
            
        elif app_settings.azure_openai.api_key is not None:
            ai_config = app_settings.azure_openai
            
            llm = AzureOpenAI(
                model=ai_config.model,
                deployment_name=ai_config.deployment_id ,
                api_key=ai_config.api_key,
                azure_endpoint=ai_config.api_base,
                api_version=ai_config.api_version,
                callback_manager=Settings.callback_manager
            )                
        else:
            raise Exception("No LLM API key provided")                               
        
        logger.debug(f"LLM created: {llm}")
        
        return llm            
    
    def _create_elasticsearch_client(self, app_settings: AppSettings) -> AsyncElasticsearch:
        logger.debug("Creating Elasticsearch client...")
        
        # Instantiate the Elasticsearch client        
        es_client = AsyncElasticsearch(
            [app_settings.elasticsearch.url],
            #ssl_assert_fingerprint=app_settings.elasticsearch.certificate_fingerprint,
            basic_auth=(app_settings.elasticsearch.username, app_settings.elasticsearch.password),
            verify_certs=False,        
        )
        es_client.options(headers={"user-agent": "memory-bank/0.0.1"})        
    
        logger.debug(f"Elasticsearch client created: {es_client}")
    
        return es_client
    
    def _create_vector_store(self, app_settings: AppSettings) -> ElasticsearchStore:
        logger.debug("Creating vector store...")
        
        es_client = self._create_elasticsearch_client(app_settings)        
        
        es_vector_store = ElasticsearchStore(
            index_name= app_settings.elasticsearch.default_index,
            es_client=es_client,                           
        )       
        
        logger.debug(f"Vector store created: {es_vector_store}")     
        
        return es_vector_store

    def _create_storage_context(self, app_settings: AppSettings) -> StorageContext:
        logger.debug("Creating storage context...")
        
        storage_context = StorageContext.from_defaults(            
            docstore=None,
            index_store=None,
            image_store=None,
            graph_store=None,            
            vector_store=self.vector_store)
        
        logger.debug(f"Storage context created: {storage_context}")
        
        return storage_context

    def _create_vector_index(self, app_settings: AppSettings) -> VectorStoreIndex:                
        logger.debug("Creating vector index...")

        # Instantiate the Elasticsearch client
        index = VectorStoreIndex.from_vector_store(
            vector_store = self.vector_store,             
            # TODO look intoi this. might need more args
            #service_context=self.service_context,             
            show_progress=True)
        
        logger.debug(f"Vector index created: {index}")
        
        return index

    def get_callback_manager(self) -> CallbackManager:
        logger.debug("Getting callback manager...")
        return self.callback_manager

    async def get_vector_index(self) -> VectorStoreIndex:                
        logger.debug("Getting vector index...")

        # Instantiate the Elasticsearch client
        return self.vector_index