import asyncio
import random
import time
import uuid
import os
from llama_index import VectorStoreIndex
from loguru import logger

logger.debug("Starting up the UI")
import gradio as gr

logger.debug("Starting up the Memory Bank")
from memorybank.server.di import setup_services
from memorybank.services.index_factory import IndexFactory
from memorybank.settings.app_settings import AppSettings

logger.debug("Setting up dependency injection")
injector = setup_services()
appSettings = injector.get(AppSettings)
index_factory = injector.get(IndexFactory)

import gradio as gr

logger.debug("Launching UI")

async def get_index() -> VectorStoreIndex:
    index = await index_factory.get_index()    
    return index

def get_formatted_sources(response, length: int = 100) -> str:
        """Get formatted sources text."""
        texts = []
        for source_node in response.source_nodes:
            #fmt_text_chunk = truncate_text(source_node.node.get_content(), length)
            doc_id = source_node.node.node_id or "None"
            file_name = source_node.node.metadata["file_name"]
            source_text = f"> Source (Doc id: {doc_id}): {file_name}"
            texts.append(source_text)
        return "\n\n".join(texts)

async def ask_llama_index(message, history):
    #await asyncio.sleep(2)  # simulate a long-running task
    if message is None or message == "":
        message="What do you know of the moon?"
                    
    index = await asyncio.wait_for(get_index(), timeout=20)
    engine = index.as_query_engine()
        
    response = await asyncio.wait_for(engine.aquery(message), timeout=20)
    response_text = response.response
    response_links = get_formatted_sources(response=response, length=100)
    
    full_response = f"""
Response:
{response_text}

Links:
{response_links}
"""
    #full_response = "the response to " + message + " is: " + message
    logger.debug(f"Response: {full_response}")
    
    return full_response

gr.ChatInterface(
    fn=ask_llama_index
    ).launch()
