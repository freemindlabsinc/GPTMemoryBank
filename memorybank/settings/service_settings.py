from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings

class EmbeddingType(str, Enum):
    azureai = "azureai"
    openai = "openai"
    huggingface = "huggingface"
    ollama = "ollama"
    
class LLMType(str, Enum):
    azureai = "azureai"
    openai = "openai"
    ollama = "ollama"


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
    
    llm: LLMType = Field(
        LLMType.openai,
        description="Type of the language model. Default: 'openai'.")
    
    embedding: EmbeddingType = Field(
        EmbeddingType.huggingface,
        description="Type of the embedding model. Default: 'huggingface'.")
