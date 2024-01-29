from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic import Field

class ServiceSettings(BaseSettings):
    class Config:
        env_prefix = 'SERVICE_'
        
    name: str = Field(
        None,
        description="Name of the service. Example: 'Memory Bank'.")
    
    description: str = Field(
        None,
        description="Description of the service.")
    
    host: str = Field(
        "0.0.0.0",
        description="The ip the service will listen to. Example: 0.0.0.0"),
    
    port: int = Field(
        8001,
        description="Port to run the service. Example: 8001.")
        

class OpenAISettings(BaseSettings):
    class Config:
        env_prefix = 'OPENAI_'

    api_base: str = Field(
        "https://api.openai.com/v1",
        description="Base URL of OpenAI API. Example: 'https://api.openai.com/v1'.",
    )
    api_key: str = Field(
        None,
        description="API key of OpenAI API. Example: 'sk-1234567890'.",
    )
    model: str = Field(
        "gpt-3.5-turbo",
        description="OpenAI Model to use. Example: 'gpt-4'.",
    )
    temperature: float = Field(
        "0.7"
    )


class AzureOpenAISettings(OpenAISettings):
    class Config:
        env_prefix = 'AZURE_OPENAI_'

    api_version: str = Field(
        "2023-07-01-preview",
        description="API version to use. Example: '2023-07-01-preview'.")

    deployment_id: str = Field(
        None,
        description="Model deployment ID.")    

class ElasticsearchSettings(BaseSettings):
    class Config:
        env_prefix = 'ELASTICSEARCH_'

    url: str = Field(
        "https://localhost:9200",
        description="Elasticsearch URL. Example: 'https://localhost:9200'.")

    username: str = Field(
        None,
        description="Elasticsearch username. Example: 'elastic'.")

    password: str = Field(
        None,
        description="Elasticsearch password. Example: 'changeme'.")

    certificate_fingerprint: str = Field(
        None,
        description="Elasticsearch certificate fingerprint. Example: 'A1:B2:C3:D4:E5:F6:G7:H8:I9:J0:K1:L2:M3:N4:O5:P6:Q7:R8:S9:T0'.")

    default_index: str = Field(
        "memorybank",
        description="Default Elasticsearch index. Example: 'memorybank'.")
    
class AzureQueuesSettings(BaseSettings):
    class Config:
        env_prefix = 'AZURE_QUEUES_'

    connection_string: str = Field(
        None,
        description="Azure storage connection string. Example: 'DefaultEndpointsProtocol=https;AccountName=your_storage_account_name;AccountKey=your_storage_account_key;EndpointSuffix=core.windows.net'.")

    import_resource_queue: str = Field(
        "memorybank-resources",
        description="Azure storage queue to import resource. Example: 'memorybank-resources'.")

    save_messages_queue: str = Field(
        "memorybank-messages",
        description="Azure storage queue to import messages. Example: 'memorybank-messages'.")    

class RedisSettings(BaseSettings):
    class Config:
        env_prefix = 'REDIS_'

    server: str = Field(
        "localhost",
        description="Redis server. Example: 'localhost'.")

    port: int = Field(
        6379,
        description="Redis port. Example: 6379.")

    document_store_namespace: str = Field(
        "document_store",
        description="Redis namespace for document store. Example: 'document_store'.")

    cache_collection: str = Field(
        "memorybankcache",
        description="Redis collection for cache. Example: 'memorybankcache'.")    

class EmbeddingType(str, Enum):
    azureai = "azureai"
    openai = "openai"
    huggingface = "huggingface"

class EmbeddingsSettings(BaseSettings):
    class Config:
        env_prefix = 'EMBEDDINGS_'
    
    type: EmbeddingType = Field(
        EmbeddingType.huggingface,
        description="Type of the embedding model. Default: 'huggingface'.")
    
    model: str = Field(
        None,
        description="Name of the embedding model. Example: 'HuggingFace'.")
    pass    

class AppSettings(BaseModel):
    service: ServiceSettings
    embeddings: EmbeddingsSettings
    openai: OpenAISettings
    azure_openai: AzureOpenAISettings
    elasticsearch: ElasticsearchSettings
    redis: RedisSettings
    azure_queues: AzureQueuesSettings  

def load_app_settings_from_env() -> AppSettings:
    loaded = load_dotenv()  # Load environment variables from .env file
        
    if not loaded:
        # NOTE Possibly not a good idea in production
        raise Exception("Could not load .env file")
    
    #import os
    #key = os.getenv("OPENAI_API_KEY")
    
    # TODO it's probably unnecessary to instantiate them all here... investigate at some point
    settings = AppSettings(
        service=ServiceSettings(),
        embeddings=EmbeddingsSettings(),
        openai=OpenAISettings(),
        azure_openai=AzureOpenAISettings(),
        elasticsearch=ElasticsearchSettings(),
        redis=RedisSettings(),
        azure_queues=AzureQueuesSettings()
    )   
    
    return settings