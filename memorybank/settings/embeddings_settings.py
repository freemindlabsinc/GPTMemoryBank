from enum import Enum
from pydantic import Field
from pydantic_settings import BaseSettings
from abc import ABC, abstractmethod
from llama_index.core.constants import DEFAULT_EMBED_BATCH_SIZE
from typing import Optional

class BaseEmbeddingSettings(BaseSettings):
    model: Optional[str] = Field(
        None,
        description="The name of the embedding model.")
    
    embed_batch_size: Optional[int] = Field(default=DEFAULT_EMBED_BATCH_SIZE)

class OllamaEmbeddingSettings(BaseEmbeddingSettings):
    class Config:
        env_prefix = 'OLLAMA_EMBEDDING_'        
    
class HuggingFaceEmbeddingSettings(BaseEmbeddingSettings):
    class Config:
        env_prefix = 'HUGGINGFACE_EMBEDDING_'
        
class OpenAIEmbeddingSettings(BaseEmbeddingSettings):
    class Config:
        env_prefix = 'OPENAI_EMBEDDING_'
            
class AzureOpenAIEmbeddingSettings(BaseEmbeddingSettings):
    class Config:
        env_prefix = 'AZURE_OPENAI_EMBEDDING_'
        
        