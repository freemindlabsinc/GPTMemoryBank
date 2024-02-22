import os
from loguru import logger
logger.debug("Starting application...")

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.abstractions.transcriber import Transcriber

from memorybank.server.di import setup_services
from memorybank.settings.app_settings import AppSettings

from memorybank.ui.filemanager_tab import create_file_manager_tab
from memorybank.ui.video_tab import create_video_tab
from memorybank.ui.voice_tab import create_voice_tab
from memorybank.ui.chat_tab import create_chat_tab

injector = setup_services()
appSettings:AppSettings = injector.get(AppSettings)
memory_store:MemoryStore = injector.get(MemoryStore)

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

chat_tab = create_chat_tab()
voice_tab = create_voice_tab()
video_tab = create_video_tab()
file_manager_tab = create_file_manager_tab()
demo = gr.TabbedInterface(
    # [chat_tab, voice_tab, video_tab, file_manager_tab], 
    [chat_tab], 
    #["Chat", "Voice", "Video", "File Manager"])
    ["Chat"])

demo.queue()
if __name__ == "__main__":
    demo.launch()#share=True)