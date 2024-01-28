from typing import Literal

from pydantic import BaseModel, Field

#from private_gpt.settings.settings_loader import load_active_settings

class OpenAISettings(BaseModel):
    api_base: str = Field(
        None,
        description="Base URL of OpenAI API. Example: 'https://api.openai.com/v1'.",
    )
    api_key: str
    model: str = Field(
        "gpt-3.5-turbo",
        description="OpenAI Model to use. Example: 'gpt-4'.",
    )
    temperature: float = Field(
        "0.9"
    )
    
class AzureOpenAISettings(OpenAISettings):
    api_version: str = Field(
        "2023-07-01-preview", 
        description="API version to use. Example: '2023-07-01-preview'.")
    
    model_deployment_id: str = Field(
        None,
        description="Model deployment ID.")
    
class ElasticsearchSettings(BaseModel):
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
    
class RedisSettings(BaseModel):
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
    
class AzureQueuesSettings(BaseModel):
    connection_string: str = Field(
        None,
        description="Azure storage connection string. Example: 'DefaultEndpointsProtocol=https;AccountName=your_storage_account_name;AccountKey=your_storage_account_key;EndpointSuffix=core.windows.net'.")
    
    import_resource_queue: str = Field(
        "memorybank-resources",
        description="Azure storage queue to import resource. Example: 'memorybank-resources'.")
    
    save_messages_queue: str = Field(
        "memorybank-messages",
        description="Azure storage queue to import messages. Example: 'memorybank-messages'.")