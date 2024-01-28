from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic.main import BaseModel

class OpenAISettings(BaseSettings):
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
    