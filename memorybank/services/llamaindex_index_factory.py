from loguru import logger

from elasticsearch import AsyncElasticsearch
from injector import inject

from llama_index.llms import (AzureOpenAI, OpenAI)
from llama_index.embeddings import (AzureOpenAIEmbedding, HuggingFaceEmbedding)
from llama_index.vector_stores import (ElasticsearchStore)
from llama_index.storage.storage_context import (StorageContext)

from llama_index import (ServiceContext, 
                         VectorStoreIndex,
                         set_global_handler,
                         load_index_from_storage,
                         load_indices_from_storage,
                         load_graph_from_storage,
)

from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler
)

from memorybank.settings.app_settings import AppSettings
from memorybank.settings.embeddings_settings import EmbeddingType
from memorybank.abstractions.index_factory import IndexFactory

class LlamaIndexIndexFactory(IndexFactory):
    @inject
    def __init__(self, app_settings: AppSettings):
        self.app_settings = app_settings
        
        self.es_client = self._create_elasticsearch_client()
        self.embed_model = self._create_embedding_model()
        self.callback_mgr = self._create_callback_manager()
        self.callback_manager = self._create_callback_manager()
        self.llm = self._create_llm()
        self.vector_store = self._create_vector_store()
        self.storage_context =self._create_storage_context
        self.service_context = self._create_service_context() 
        self.vector_index = self.create_vector_index()
        
    def _create_elasticsearch_client(self) -> AsyncElasticsearch:
        logger.debug("Creating Elasticsearch client...")
        
        # Instantiate the Elasticsearch client        
        es_client = AsyncElasticsearch(
            [self.app_settings.elasticsearch.url],
            #ssl_assert_fingerprint=app_settings.elasticsearch.certificate_fingerprint,
            basic_auth=(self.app_settings.elasticsearch.username, self.app_settings.elasticsearch.password),
            verify_certs=False,        
        )
        es_client.options(headers={"user-agent": "memory-bank/0.0.1"})        
    
        return es_client

    def _create_embedding_model(self):    
        logger.debug("Creating embedding model...")
        
        model_name = self.app_settings.embeddings.model
        model_type = self.app_settings.embeddings.type
        
        if model_type == EmbeddingType.huggingface:    
            embed_model = HuggingFaceEmbedding(model_name=model_name)
            
        elif model_type == EmbeddingType.azureai:
            embed_model = AzureOpenAIEmbedding(
                model=self.app_settings.azure_openai.model,
                deployment_name=self.app_settings.azure_openai.deployment_id,
                api_key=self.app_settings.azure_openai.api_key,
                azure_endpoint=self.app_settings.azure_openai.api_base,
                api_version=self.app_settings.azure_openai.api_version,
            )
        else:        
            # FIXME finish / instantiate OpenAI
            raise Exception("Not supported embedding type fix me")
        
        return embed_model    
    
    def _create_callback_manager(self):
        logger.debug("Creating callback manager...")
        
        llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        callback_manager = CallbackManager([llama_debug])
        
    def _create_llm(self):
        logger.debug("Creating LLM...")
        
        if self.app_settings.openai.api_key is not None:
            ai_config = self.app_settings.openai
            
            llm = OpenAI(model= ai_config.model, temperature=ai_config.temperature)
            
        elif self.app_settings.azure_openai.api_key is not None:
            ai_config = self.app_settings.azure_openai
            
            llm = AzureOpenAI(
                model=ai_config.model,
                deployment_name=ai_config.deployment_id ,
                api_key=ai_config.api_key,
                azure_endpoint=ai_config.api_base,
                api_version=ai_config.api_version,
            )                
        else:
            raise Exception("No LLM API key provided")                               
        
        return llm
    
    def _create_service_context(self) -> ServiceContext:        
        logger.debug("Creating service context...")
        
        service_context = ServiceContext.from_defaults(
            llm=self.llm,
            callback_manager=self.callback_manager,             
            embed_model=self.embed_model,            
        )
        
        return service_context
    
    def _create_vector_store(self) -> ElasticsearchStore:
        logger.debug("Creating vector store...")
        
        es_vector_store = ElasticsearchStore(
            index_name= self.app_settings.elasticsearch.default_index,
            es_client=self.es_client,               
        )            
        
        return es_vector_store

    def _create_storage_context(self) -> StorageContext:
        logger.debug("Creating storage context...")
        
        persist_directory = "./.persistDir"
        storage_context = StorageContext.from_defaults(            
            persist_dir=persist_directory,
            vector_store=self.vector_store)
        
        return storage_context

    def create_vector_index(self) -> VectorStoreIndex:                
        logger.debug("Creating vector index...")

        # Instantiate the Elasticsearch client
        index = VectorStoreIndex.from_vector_store(
            self.vector_store, 
            service_context=self.service_context, 
            show_progress=True)
        
        return index

    async def get_vector_index(self) -> VectorStoreIndex:                
        logger.debug("Getting vector index...")

        # Instantiate the Elasticsearch client
        return self.vector_index