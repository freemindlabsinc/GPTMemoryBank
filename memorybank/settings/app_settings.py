from dotenv import load_dotenv
from pydantic import BaseModel
from memorybank.settings.azure_openai_settings import AzureOpenAISettings
from memorybank.settings.azure_queues_settings import AzureQueuesSettings
from memorybank.settings.elasticsearch_settings import ElasticsearchSettings
from memorybank.settings.embeddings_settings import EmbeddingsSettings
from memorybank.settings.openai_Settings import OpenAISettings
from memorybank.settings.redis_settings import REDISSettings
from memorybank.settings.service_settings import ServiceSettings

class AppSettings(BaseModel):
    service: ServiceSettings
    embeddings: EmbeddingsSettings
    openai: OpenAISettings
    azure_openai: AzureOpenAISettings
    elasticsearch: ElasticsearchSettings
    redis: REDISSettings
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
        redis=REDISSettings(),
        azure_queues=AzureQueuesSettings()
    )   
    
    return settings