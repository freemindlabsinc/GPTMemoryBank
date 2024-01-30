from pydantic import Field
from pydantic_settings import BaseSettings


class REDISSettings(BaseSettings):
    class Config:
        env_prefix = 'REDIS_'

    server: str = Field(
        "localhost",
        description="Redis server. Example: 'localhost'.")

    port: int = Field(
        6379,
        description="Redis port. Example: 6379.")

    document_store_namespace: str = Field(
        "document_store",
        description="Redis namespace for document store. Example: 'document_store'.")

    cache_collection: str = Field(
        "memorybankcache",
        description="Redis collection for cache. Example: 'memorybankcache'.")