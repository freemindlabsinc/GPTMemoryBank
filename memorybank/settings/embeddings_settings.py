from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings

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