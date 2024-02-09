import os
from loguru import logger
logger.debug("Starting application...")

        
from llama_index.vector_stores.types import VectorStoreQueryMode
from llama_index.response_synthesizers.type import ResponseMode        

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.abstractions.transcriber import Transcriber
from memorybank.models.models import Query

from memorybank.server.di import setup_services
from memorybank.settings.app_settings import AppSettings

from memorybank.ui.chat_tab import create_chat_tab

injector = setup_services()
appSettings:AppSettings = injector.get(AppSettings)
memory_store:MemoryStore = injector.get(MemoryStore)
transcriber:Transcriber = injector.get(Transcriber)

# -------------------------
logger.debug("Launching UI")
import gradio as gr

# FIXME Global variable to store the last question asked
last_query = None


CSS ="""
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
#component-0 { height: 100%; }
#chatbot { flex-grow: 1; overflow: auto; }
#audio { flex-grow: 1; overflow: auto; }
#textbox { flex-grow: 1; overflow: auto; }
footer { visibility: hidden; }
"""
use_queue = True

#with gr.Blocks(title=appSettings.service.name, css=CSS) as demo:
#    tab = create_chat_tab()    

tab = create_chat_tab()
demo = gr.TabbedInterface([tab], ["Chat Tab"])

demo.queue()
if __name__ == "__main__":
    demo.launch()#share=True)

