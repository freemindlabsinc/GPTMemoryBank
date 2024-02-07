from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class PromptSettings(BaseSettings):
    class Config:
        env_prefix = 'PROMPT_'

    debug_question: Optional[str] = Field(
        None,
        description="The question to ask if the user question is empty.")

    first_prompt: str = Field(
        "Upload files and ask questions...",
        description="The first prompt to show to the user.")