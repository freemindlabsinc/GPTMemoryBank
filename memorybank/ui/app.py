import asyncio
from llama_index import VectorStoreIndex
import numpy as np
#from llama_index import VectorStoreIndex
from loguru import logger

logger.debug("Starting up the basics")
import gradio as gr
from transformers import pipeline

logger.debug("Starting up the Memory Bank")
from memorybank.server.di import setup_services
from memorybank.services.index_factory import IndexFactory
from memorybank.settings.app_settings import AppSettings

logger.debug("Setting up dependency injection")
injector = setup_services()
appSettings = injector.get(AppSettings)
index_factory = injector.get(IndexFactory)

logger.debug("Creating speech recognition pipeline")
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

logger.debug("Launching UI")

# UI stuff

import gradio as gr
import os
import time

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.
# UI stuff

async def _get_index() -> VectorStoreIndex:
    index = await index_factory.get_index()    
    return index

def _get_formatted_sources(response, length: int = 100) -> str:
        """Get formatted sources text."""
        texts = []
        for source_node in response.source_nodes:
            #fmt_text_chunk = truncate_text(source_node.node.get_content(), length)
            doc_id = source_node.node.node_id or "None"
            file_name = source_node.node.metadata["file_name"]
            source_text = f"> Source (Doc id: {doc_id}): {file_name}"
            texts.append(source_text)
        return "\n\n".join(texts)

def _transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    txt = transcriber({"sampling_rate": sr, "raw": y})["text"]
    return txt

async def ask_llama_index(message):
    #await asyncio.sleep(2)  # simulate a long-running task
    if message is None or message == "":
        return "Ask a question please"
                    
    index = await asyncio.wait_for(_get_index(), timeout=20)
    engine = index.as_query_engine()
        
    response = await asyncio.wait_for(engine.aquery(message), timeout=20)
    response_text = response.response
    response_links = _get_formatted_sources(response=response, length=100)
    
    full_response = f"""
Response:
{response_text}

Links:
{response_links}
"""
    #full_response = "the response to " + message + " is: " + message
    logger.debug(f"Response: {full_response}")
    
    return full_response

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_file(history, file):
    for f in file:
        history = history + [((f.name,), None)]            
    
    return history


async def add_text(history, text):    
    history = history + [(text, None)]
    
    return history, gr.Textbox(value="", interactive=False)


async def add_audio(history, audio):
    if audio is not None:    
        try:    
            transcribed_msg = _transcribe(audio)
        except Exception as e:
            transcribed_msg = f"Error: {e}"
        
        history = history + [(transcribed_msg, None)]
        
    return history, gr.Audio(sources=["microphone"])

async def bot(history):
    answered = history[-1][1] is not None
    if answered:
        return history
        
    question = history[-1][0]
    
    try:
        response = await ask_llama_index(question)
    except Exception as e:
        response = f"Error: {e}"
        
    history[-1][1] = response
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "icon.png"))),
    )
    
    with gr.Row():
        audio = gr.Audio(sources=["microphone"])

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        upload_btn = gr.UploadButton(
            "📁", 
            file_types=["image", "video", "audio", "text"],
            file_count="multiple",
        )        

    audio_msg = audio.change(add_audio, [chatbot, audio], [chatbot, audio], queue=False)
    audio_msg.then(bot, [chatbot], [chatbot])                 
    audio_msg.then(lambda: gr.Audio(sources=["microphone"], interactive=True), None, [audio], queue=False)
    
    # chatbot --> history list
    # txt -> current edit box text
    
    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False)
    txt_msg.then(bot, [chatbot], [chatbot])
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
    
    file_msg = upload_btn.upload(add_file, [chatbot, upload_btn], [chatbot], queue=False)
    file_msg.then(bot, chatbot, chatbot)

    chatbot.like(print_like_dislike, None, None)


demo.queue()
if __name__ == "__main__":
    demo.launch()

