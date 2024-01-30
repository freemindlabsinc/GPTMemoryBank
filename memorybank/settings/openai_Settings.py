from pydantic import Field
from pydantic_settings import BaseSettings


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