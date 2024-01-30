from abc import ABC
import os
from elasticsearch import AsyncElasticsearch
from injector import inject
from memorybank.settings.app_settings import AppSettings
from memorybank.settings.embeddings_settings import EmbeddingType

from elasticsearch import AsyncElasticsearch
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
from llama_index.llms import AzureOpenAI
from llama_index.embeddings import AzureOpenAIEmbedding

class IndexFactory:
    @inject
    def __init__(self, app_settings: AppSettings):
        self.app_settings = app_settings            
    
    def _create_elasticsearch_client(self) -> AsyncElasticsearch:
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
    
    
    def _create_llm_service_context(self) -> ServiceContext:        
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
        
        embed_model = self._create_embedding_model()
        
        service_context = ServiceContext.from_defaults(
            # callback_manager=callback_manager, 
            llm=llm,
            embed_model=embed_model,
        )
        
        return service_context

    vector_store_index = None
    async def get_index(self) -> VectorStoreIndex:
        if self.vector_store_index is None:
            self.vector_store_index = await self._get_index()
        
        return self.vector_store_index
        

    async def _get_index(self) -> VectorStoreIndex:
        # Instantiate the Elasticsearch client
        es_client = self._create_elasticsearch_client()    
        service_context = self._create_llm_service_context()
        
        persist_directory = "./.persistDir"
        es_vector_store = ElasticsearchStore(
            index_name= self.app_settings.elasticsearch.default_index,
            es_client=es_client,
        )
                                
        if (not os.path.exists(persist_directory)):
            storage_context = StorageContext.from_defaults(vector_store=es_vector_store)#, persist_dir=persist_directory)
            
            docs = []
            #docs = SimpleDirectoryReader("./docs").load_data(show_progress=True) # DEBUG
            
            index = VectorStoreIndex.from_documents(
                docs, 
                service_context=service_context, 
                storage_context=storage_context, 
                show_progress=True)            
            
            storage_context.persist(persist_dir=persist_directory)                
        else:
            storage_context = StorageContext.from_defaults(
                persist_dir=persist_directory, 
                vector_store=es_vector_store,
                )
            
            index = load_index_from_storage(            
                storage_context=storage_context,            
                show_progress=True)
            index._service_context = service_context # Hack to get around the fact that the service context is correct        
        
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