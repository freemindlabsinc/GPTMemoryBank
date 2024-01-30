from pydantic import Field
from pydantic_settings import BaseSettings


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