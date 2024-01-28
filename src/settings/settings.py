from typing import Literal
from dotenv import load_dotenv

from pydantic import BaseModel, Field

#from private_gpt.settings.settings_loader import load_active_settings

class OpenAISettings(BaseModel):
    class Config:
        env_prefix = 'OPENAI_'
        
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
    class Config:
        env_prefix = 'AZURE_OPENAI_'
        
    api_version: str = Field(
        "2023-07-01-preview", 
        description="API version to use. Example: '2023-07-01-preview'.")
    
    deployment_id: str = Field(
        None,
        description="Model deployment ID.")
    
class ElasticsearchSettings(BaseModel):
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
    
class RedisSettings(BaseModel):
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
    
class AzureQueuesSettings(BaseModel):
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
    
def load_settings_from_env():
    load_dotenv()  # Load environment variables from .env file

    # Create instances of your settings classes
    # The environment variables will be automatically used to populate the fields
    redis_settings = RedisSettings()
    azure_queues_settings = AzureQueuesSettings()

    return redis_settings, azure_queues_settings
    
if __name__ == "__main__":
    redis_settings, azure_queues_settings = load_settings_from_env()
    print(redis_settings.server)
    print(azure_queues_settings.connection_string)        