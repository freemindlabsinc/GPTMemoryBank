from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class OllamaSettings(BaseSettings):
    class Config:
        env_prefix = 'OLLAMA_'

    api_base: Optional[str] = Field(
        default=None,
        description="Base URL of Ollama. (e.g. http://localhost:11434)'.",
    )
    model: str = Field(
        "mistral",
        description="Ollama Model to use. Example: 'mistral'.",
    )
    temperature: float = Field(
        "0.7"
    )