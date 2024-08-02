from dotenv import load_dotenv
from injector import inject
from pydantic import BaseModel, Field
from memorybank.settings.ollama_settings import OllamaSettings
from memorybank.settings.azure_openai_settings import AzureOpenAISettings
from memorybank.settings.azure_queues_settings import AzureQueuesSettings
from memorybank.settings.elasticsearch_settings import ElasticsearchSettings
from memorybank.settings.openai_settings import OpenAISettings
from memorybank.settings.prompt_settings import PromptSettings
from memorybank.settings.redis_settings import REDISSettings
from memorybank.settings.service_settings import ServiceSettings
from memorybank.settings.embeddings_settings import (
    BaseEmbeddingSettings, OllamaEmbeddingSettings, HuggingFaceEmbeddingSettings,
    OpenAIEmbeddingSettings, AzureOpenAIEmbeddingSettings)


class AppSettings(BaseModel):
    service: ServiceSettings = Field(
        default=ServiceSettings(),
        description="Service settings."
    )
    prompt: PromptSettings = Field(
        default=PromptSettings(),
        description="Prompt settings."
    )    
    huggingface_embeddings: HuggingFaceEmbeddingSettings = Field(
        default=HuggingFaceEmbeddingSettings(),
        description="HuggingFace embeddings settings."
    )
    ollama: OllamaSettings = Field(
        default=OllamaSettings(),
        description="Ollama settings."
    )
    ollama_embeddings: OllamaEmbeddingSettings = Field(
        default=OllamaEmbeddingSettings(),
        description="Ollama embeddings settings."
    )
    openai: OpenAISettings = Field(
        default=OpenAISettings(),
        description="OpenAI settings."
    )
    openai_embeddings: OpenAIEmbeddingSettings = Field(
        default=OpenAIEmbeddingSettings(),
        description="OpenAI embeddings settings."
    )
    azure_openai: AzureOpenAISettings = Field(
        default=AzureOpenAISettings(),
        description="Azure OpenAI settings."
    )
    azure_openai_embeddings: AzureOpenAIEmbeddingSettings = Field(
        default=AzureOpenAIEmbeddingSettings(),
        description="Azure OpenAI embeddings settings."
    )
    elasticsearch: ElasticsearchSettings = Field(
        default=ElasticsearchSettings(),
        description="Elasticsearch settings."
    )
    redis: REDISSettings = Field(
        default=REDISSettings(),
        description="Redis settings."
    )
    azure_queues: AzureQueuesSettings = Field(  
        default=AzureQueuesSettings(),
        description="Azure Queues settings."
    )
    

# NOTE Apparently this is not needed anymore?

#def _load_app_settings_from_env() -> AppSettings:
#    loaded = load_dotenv()  # Load environment variables from .env file
#        
#    if not loaded:
#        # NOTE Possibly not a good idea in production
#        raise Exception("Could not load .env file")
#    
#    return AppSettings()   