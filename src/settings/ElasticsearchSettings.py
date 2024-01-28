from pydantic import Field
from pydantic_settings import BaseSettings


class ElasticsearchSettings(BaseSettings):
    class Config:
        env_prefix = 'ELASTICSEARCH_'

    url: str = Field(
        "https://localhost:9200",
        description="Elasticsearch URL. Example: 'https://localhost:9200'.")

    username: str = Field(
        None,
        description="Elasticsearch username. Example: 'elastic'.")

    password: str = Field(
        None,
        description="Elasticsearch password. Example: 'changeme'.")

    certificate_fingerprint: str = Field(
        None,
        description="Elasticsearch certificate fingerprint. Example: 'A1:B2:C3:D4:E5:F6:G7:H8:I9:J0:K1:L2:M3:N4:O5:P6:Q7:R8:S9:T0'.")

    default_index: str = Field(
        "memorybank",
        description="Default Elasticsearch index. Example: 'memorybank'.")