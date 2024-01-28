from dotenv import load_dotenv
from pydantic import BaseModel

from src.settings import (
    AzureOpenAISettings, 
    AzureQueuesSettings, 
    ElasticsearchSettings,
    OpenAISettings,
    RedisSettings)

class AppSettings(BaseModel):
    openai: OpenAISettings
    azure_openai: AzureOpenAISettings
    elasticsearch: ElasticsearchSettings
    redis: RedisSettings
    azure_queues: AzureQueuesSettings  

def load_app_settings_from_env() -> AppSettings:
    load_dotenv()  # Load environment variables from .env file
    
    settings = AppSettings(
        openai=OpenAISettings(),
        azure_openai=AzureOpenAISettings(),
        elasticsearch=ElasticsearchSettings(),
        redis=RedisSettings(),
        azure_queues=AzureQueuesSettings()
    )   
    
    return settings
    
if __name__ == "__main__":
    settings = load_app_settings_from_env()
    print(settings)