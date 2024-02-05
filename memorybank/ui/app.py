import asyncio
from fastapi_injector import Injected
from llama_index import Document, SimpleDirectoryReader, VectorStoreIndex
import numpy as np
from loguru import logger

import gradio as gr
from transformers import pipeline
from memorybank.abstractions.memory_store import MemoryStore
from memorybank.models.models import Query

from memorybank.server.di import setup_services
from memorybank.abstractions.index_factory import IndexFactory
from memorybank.settings.app_settings import AppSettings

injector = setup_services()
appSettings:AppSettings = injector.get(AppSettings)
memory_store:MemoryStore = injector.get(MemoryStore)

logger.debug("Creating speech recognition pipeline")
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

logger.debug("Launching UI")

# UI stuff

import gradio as gr
import os

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.
# UI stuff

def _transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    txt = transcriber({"sampling_rate": sr, "raw": y})["text"]
    return txt

async def query_llama_index(message: str) -> str:
    #await asyncio.sleep(2)  # simulate a long-running task
    if message is None or message == "":
        return "No question provided."
    
    
    
    # TODO try-catch
    qry = Query(
        text=message,
        filter=None,
        top_k=3
    )
    
    results = await memory_store.query([qry])
    
    first_response = results[0]
    response_text = first_response.answer
    response_links = first_response.formatted_sources
    
    full_response = f"""
Response:
{response_text}

Links:
{response_links}
"""
    
    logger.debug(f"Message: {message}\nResponse: {full_response}")
    
    return full_response

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)

async def add_files(history, file_list):    
    try:
        file_paths = []        
        
        for f in file_list:                 
            file_paths.append(f)
            history = history + [(f"#Consider {f} uploaded...", None)]            
            
        chunks = SimpleDirectoryReader(            
                input_files=file_list,
                filename_as_id=True,
                exclude_hidden=False).load_data(
                    show_progress=True)
                
        res = await memory_store.upsert(chunks)
            
    except Exception as e:
        history = history + [(f"Error: {e}", None)]
    finally:
        return history


def add_text(history, text):    
    history = history + [(text, None)]
    
    return history, gr.Textbox(value="", interactive=False)


def add_audio(history, audio):
    if audio is not None:    
        try:    
            transcribed_msg = _transcribe(audio)
        except Exception as e:
            transcribed_msg = f"Error: {e}"
        
        history = history + [(transcribed_msg, None)]
        
    return history, gr.Audio(sources=["microphone"])

async def bot(history):
    try:
        if len(history) == 0:
            return history
        answered = history[-1][1] is not None
        if answered:
            return history
            
        question = history[-1][0]
        
        if question.startswith("#"):
            return history
        
        try:
            response = await query_llama_index(question)
        except Exception as e:
            response = f"Error: {e}"
            
        history[-1][1] = response        
    
    except Exception as e:
        history = history + [(f"Error: {e}", None)]
    
    finally:
        return history
    


CSS ="""
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; overflow: auto;}
"""
use_queue = True
with gr.Blocks(css=CSS) as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "icon.png"))),
        #examples=["What do you know of the moon?", "Tell me about Pyhton", "What is the application Magic?"],        
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
            "📁 Upload", 
            file_types=["text", "audio"],
            file_count="multiple",            
        )        

    audio_msg = audio.change(add_audio, [chatbot, audio], [chatbot, audio], queue=use_queue)
    audio_msg.then(bot, [chatbot], [chatbot])                 
    audio_msg.then(lambda: gr.Audio(sources=["microphone"], interactive=True), None, [audio], queue=use_queue)
    
    # chatbot --> history list
    # txt -> current edit box text
    
    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=use_queue)
    txt_msg.then(bot, [chatbot], [chatbot])
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=use_queue)
    
    file_msg = upload_btn.upload(add_files, [chatbot, upload_btn], [chatbot], queue=use_queue)
    file_msg.then(bot, chatbot, chatbot)

    chatbot.like(print_like_dislike, None, None)

demo.queue()
if __name__ == "__main__":
    demo.launch()

