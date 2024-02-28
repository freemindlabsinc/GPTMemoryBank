from loguru import logger
from elasticsearch import AsyncElasticsearch
from injector import inject
from llama_index.core.settings import Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.callbacks import CallbackManager
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.retrievers import (VectorIndexRetriever)
from llama_index.core.response_synthesizers import (get_response_synthesizer, BaseSynthesizer)
from llama_index.core.query_engine import (RetrieverQueryEngine)
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.callbacks import (CallbackManager, LlamaDebugHandler)
from memorybank.settings.app_settings import AppSettings
from memorybank.settings.service_settings import EmbeddingType, LLMType
from memorybank.abstractions.rag_factory import RAGFactory
from llama_index.core.response_synthesizers.type import ResponseMode        
from llama_index.core.vector_stores.types import VectorStoreQueryMode

class LlamaIndexRAGFactory(RAGFactory):
    """
    Configures and returns a LlamaIndex VecorStoreIndex instance.
    """
    @inject
    def __init__(self, app_settings: AppSettings):
        """
        Constructor for the LlamaIndexIndexFactory class.
        """
        self.callback_manager = self._create_callback_manager(app_settings)
        
        self.embed_model = self._create_embedding_model(app_settings)                
        self.llm = self._create_llm(app_settings)
        self.storage_context = self._create_storage_context(app_settings)        
        self.vector_index = self._create_vector_index(app_settings)#, self.storage_context, self.embed_model) 
    
    def _create_callback_manager(self, app_settings: AppSettings) -> CallbackManager:
        # Add LlamaIndex simple observability
        Settings.global_handler = "simple"
        
        logger.debug("Creating callback manager...")
        
        llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        return CallbackManager([llama_debug])
        
    def _create_embedding_model(self, app_settings: AppSettings) -> BaseEmbedding:            
        """
        Creates and returns the configured embedding model.
        """                
        embedding_type = app_settings.service.embedding
        logger.debug(f"Creating embedding model {embedding_type}.")
        
        if embedding_type == EmbeddingType.ollama:
            embed_model = OllamaEmbedding(
                model_name=app_settings.ollama_embeddings.model,
                embed_batch_size=app_settings.ollama_embeddings.embed_batch_size,                                                
                callback_manager=self.callback_manager,
                # other    
                base_url=app_settings.ollama.api_base
            )                                                          
        
        elif embedding_type == EmbeddingType.huggingface:    
            embed_model = HuggingFaceEmbedding(
                model_name=app_settings.huggingface_embeddings.model,
                embed_batch_size=app_settings.huggingface_embeddings.embed_batch_size,
                callback_manager=self.callback_manager
                # other                                
                )
            
        elif embedding_type == EmbeddingType.azureai:
            embed_model = AzureOpenAIEmbedding(                
                model=app_settings.azure_openai_embeddings.model,                
                embed_batch_size=app_settings.azure_openai_embeddings.embed_batch_size,
                callback_manager=self.callback_manager,                
                #other
                deployment_name=app_settings.azure_openai.deployment_name, 
                api_key=app_settings.azure_openai.api_key, 
                azure_endpoint=app_settings.azure_openai.api_base,
                api_version=app_settings.azure_openai.api_version,                
            )
            
        elif embedding_type == EmbeddingType.openai:
            embed_model = OpenAIEmbedding(
                model=app_settings.openai_embeddings.model,
                embed_batch_size=app_settings.openai_embeddings.embed_batch_size,
                callback_manager=self.callback_manager,                
                # other
                api_key=app_settings.openai.api_key, 
                #temperature=app_settings.openai.temperature,
                
            )
            
        else:        
            # FIXME finish / instantiate OpenAI
            raise Exception("Embedding type not supported.")
        
        logger.debug(f"Embedding model created: {embed_model}")
        
        return embed_model    
            
    def _create_llm(self, app_settings: AppSettings) -> LLM:
        logger.debug("Creating LLM...")
        
        llm = app_settings.service.llm
        
        if llm == LLMType.ollama:
            # If there's an Ollama API key, use Ollama
            llm = Ollama(
                model=app_settings.ollama.model, 
                request_timeout=60.0, 
                base_url=app_settings.ollama.api_base,
                callback_manager=self.callback_manager)
        
        elif llm == LLMType.openai:
            # If there's an openai key, use OpenAI
            ai_config = app_settings.openai
            
            llm = OpenAI(
                model= ai_config.model, 
                api_key=ai_config.api_key,
                temperature=ai_config.temperature, 
                callback_manager=self.callback_manager)
            
        elif llm == LLMType.azureai:
            # If there's an Azure OpenAI key, use Azure OpenAI
            ai_config = app_settings.azure_openai
            
            llm = AzureOpenAI(
                model=ai_config.model,
                deployment_name=ai_config.deployment_name ,
                api_key=ai_config.api_key,
                azure_endpoint=ai_config.api_base,
                api_version=ai_config.api_version,
                callback_manager=self.callback_manager
            )                
        else:
            raise Exception("Invalid LLM type provided")                               
        
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
    
    def _create_storage_context(self, app_settings: AppSettings) -> StorageContext:
        logger.debug("Creating vector store...")
        
        es_client = self._create_elasticsearch_client(app_settings)        
        
        es_vector_store = ElasticsearchStore(
            index_name= app_settings.elasticsearch.default_index,
            es_client=es_client,
            
        )       
        
        logger.debug(f"Vector store created: {es_vector_store}")                     
        logger.debug("Creating storage context...")
        
        storage_context = StorageContext.from_defaults(                                                                   
            docstore=None,
            index_store=None,
            image_store=None,
            graph_store=None,            
            vector_store=es_vector_store)
        
        logger.debug(f"Storage context created: {storage_context}")
        
        return storage_context

    def _create_vector_index(self, app_settings: AppSettings) -> VectorStoreIndex:                
        logger.debug("Creating vector index...")

        # Instantiate the Elasticsearch client
        index = VectorStoreIndex.from_vector_store(            
            vector_store = self.storage_context.vector_store,    
            embed_model= self.embed_model,                     
            # TODO look intoi this. might need more args
            #service_context=self.service_context,             
            show_progress=True)
        
        logger.debug(f"Vector index created: {index}")
        
        return index
    
    def _create_synthesizer(self, response_mode: ResponseMode) -> BaseSynthesizer:
        synth = get_response_synthesizer(
                llm=self.llm,
                #prompt_helper=None, # manages the chat window
                #text_qa_template=
                #refine_template=
                #summary_template=
                #simple_template=                
                response_mode=response_mode,
                callback_manager=self.callback_manager
                #service_context=idx.service_context,                                
                #use_async=
                #streaming=
                #structured_answer_filtering=
                #output_cls=
                #program_factory=
            )
        
        return synth
    
    def _create_retriever(self, top_k: float, vector_store_query_mode: VectorStoreQueryMode) -> BaseRetriever:
        #return self.vector_index.as_retriever()
    
        retriever = VectorIndexRetriever(
                index= self.vector_index,
                similarity_top_k=top_k,
                vector_store_query_mode=vector_store_query_mode,
                #filters=MetadataFilters(),
                #alpha = float,                                
                #node_ids=None,
                #doc_ids=None,
                #sparse_top_k=                
                callback_manager=self.callback_manager,
                #object_map=
                verbose=True,                
            )
        return retriever
    
# IndexFactory implementations
    
    def get_vector_index(self) -> VectorStoreIndex:                
        return self.vector_index
        
    def get_chat_engine(self) -> BaseChatEngine:           
        return self.vector_index.as_chat_engine(
            chat_mode = ChatMode.simple,
            llm = self.llm,            
        )
    
    def get_retriever(self, 
                      top_k: float, 
                      vector_store_query_mode: VectorStoreQueryMode) -> BaseRetriever:
        
        return self._create_retriever(
            top_k=top_k,
            vector_store_query_mode=vector_store_query_mode
        )
        
    def get_query_engine(self,                          
                         top_k: float, 
                         vector_store_query_mode: VectorStoreQueryMode,
                         response_mode: ResponseMode
                        ) -> BaseQueryEngine:
        
        retriever = self._create_retriever(
            top_k, 
            vector_store_query_mode)
            
        synth = self._create_synthesizer(response_mode)
                    
        query_engine = RetrieverQueryEngine(
            callback_manager=self.callback_manager,
            retriever=retriever,
            response_synthesizer=synth,
            node_postprocessors=None,            
        )
            
        return query_engine