from pydantic import Field
from pydantic_settings import BaseSettings


class AzureQueuesSettings(BaseSettings):
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