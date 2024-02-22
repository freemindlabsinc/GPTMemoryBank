import os
from pathlib import Path
import gradio as gr

from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core.response_synthesizers.type import ResponseMode
from loguru import logger

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.abstractions.transcriber import Transcriber
from memorybank.models.models import Query

from memorybank.server.di import setup_services
from memorybank.settings.app_settings import AppSettings


injector = setup_services()
appSettings:AppSettings = injector.get(AppSettings)
memory_store:MemoryStore = injector.get(MemoryStore)
transcriber:Transcriber = injector.get(Transcriber)
use_queue = True

def create_file_manager_tab():
    with gr.Blocks() as tab:
        file_manager = _create_file_manager()
    
    # chatbox.value1, value2 --> function add_audio() --> the results are passed back t
      
    #audio_msg = audio.change(add_audio, [chatbot, audio], [chatbot, audio], queue=use_queue)
    #audio_msg.then(bot, [chatbot], [chatbot])                 
    #audio_msg.then(_create_audio, None, [audio], queue=use_queue)
    
    return tab
        

#def add_audio(history, audio):
#    if audio is not None:    
#        try:    
#            transcribed_msg = transcriber.transcribe(audio)
#        except Exception as e:
#            transcribed_msg = f"Error: {e}"
#        
#        history = history + [(transcribed_msg, None)]
#        
#    return history, gr.Audio(sources=["microphone"])

def _create_file_manager():
    current_file_path = Path(__file__).resolve()
    absolute_path = (current_file_path.parent / ".." / ".." / "docs").resolve()
    
    return gr.FileExplorer(
        label="Files",
        elem_id="fileexporer",
        glob="*.*",
        root=absolute_path,
        interactive=True,                
        show_label=True)