from memorybank.settings.openai_Settings import OpenAISettings
from pydantic import Field

class AzureOpenAISettings(OpenAISettings):
    class Config:
        env_prefix = 'AZURE_OPENAI_'

    api_version: str = Field(
        "2023-07-01-preview",
        description="API version to use. Example: '2023-07-01-preview'.")

    deployment_id: str = Field(
        None,
        description="Model deployment ID.")