import os
from loguru import logger
logger.debug("Starting application...")

from memorybank.abstractions.memory_store import MemoryStore
from memorybank.abstractions.transcriber import Transcriber
from memorybank.models.models import Query

from memorybank.server.di import setup_services
from memorybank.settings.app_settings import AppSettings

injector = setup_services()
appSettings:AppSettings = injector.get(AppSettings)
memory_store:MemoryStore = injector.get(MemoryStore)
transcriber:Transcriber = injector.get(Transcriber)

# -------------------------
logger.debug("Launching UI")
import gradio as gr

async def run_query(message: str) -> str:
    try:    
        if message is None or message == "":
            return "No question provided."        
        
        response = await memory_store.query(
            Query(text=message, filter=None, top_k=3))
            
        full_response = f"""
**Response:**
{response.answer}

*Links:*
{response.formatted_sources}
"""
        
        logger.debug(f"Message: {message}\nResponse: {full_response}")
        
        return full_response
    
    except Exception as e:
      return f"Error: {e}"        

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)

async def add_files(history, file_list):    
    try:
        res = await memory_store.upload(
            file_names=file_list,
            chunk_token_size=None,)
        
        only_filenames = [os.path.basename(f) for f in file_list]
        
        usr_msg = f"Upload {only_filenames}..."
        
        history = history + [(usr_msg, f"Uploaded {len(file_list)} file(s) and generated {len(res)} document chunks.")]
            
    except Exception as e:
        history = history + [(usr_msg, f"Error: {e}")]
    finally:
        return history

def add_text(history, text):    
    history = history + [(text, None)]
    
    return history, gr.Textbox(value="", interactive=False)

def add_audio(history, audio):
    if audio is not None:    
        try:    
            transcribed_msg = transcriber.transcribe(audio)
        except Exception as e:
            transcribed_msg = f"Error: {e}"
        
        history = history + [(transcribed_msg, None)]
        
    return history, gr.Audio(sources=["microphone"])

async def bot(history):
    try:
        if len(history) == 0:
            return history
        
        bot_response = history[-1][1] is not None
        if bot_response:
            return history
        
        user_question = history[-1][0]
                    
        try:
            response = await run_query(user_question)
        except Exception as e:
            response = f"Error: {e}"
        
        # sets the bot response
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
footer {visibility: hidden}
"""
use_queue = True

def _create_audio():
    return gr.Audio(
        label="🎤 Record or upload audio files...",
        sources=["microphone", "upload"], 
        show_download_button=True,
        editable=True,
        interactive=True,         
        show_label=True)
    
def _create_textbox():
    return gr.Textbox(
        scale=4,
        show_label=False,
        placeholder="Enter text and press enter, or upload a text file or audio file.",
        value="What is carbon?",
        container=False,
        interactive=True,
    )
    
def _create_upload_button():
    return gr.UploadButton(
        "📁 Upload", 
        file_types=["text", "audio"],
        file_count="multiple",            
        interactive=True,
    )

with gr.Blocks(title="Memory Bank by Free Mind Labs", css=CSS) as demo:    
    chatbot = gr.Chatbot(
        [],
        label = "Memory Bank",
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "icon.png")))
        #examples=["What do you know of the moon?", "Tell me about Pyhton", "What is the application Magic?"],        
    )
        
    with gr.Row():
        txt = _create_textbox()
        upload_btn = _create_upload_button()
    
    with gr.Row():
        audio = _create_audio()

    # chatbox.value1, value2 --> function add_audio() --> the results are passed back t
    audio_msg = audio.change(add_audio, [chatbot, audio], [chatbot, audio], queue=use_queue)
    audio_msg.then(bot, [chatbot], [chatbot])                 
    audio_msg.then(_create_audio, None, [audio], queue=use_queue)
    
    # chatbot --> history list
    # txt -> current edit box text
    
    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=use_queue)
    txt_msg.then(bot, [chatbot], [chatbot])
    txt_msg.then(_create_textbox, None, [txt], queue=use_queue)
    
    file_msg = upload_btn.upload(add_files, [chatbot, upload_btn], [chatbot], queue=use_queue)
    file_msg.then(bot, chatbot, chatbot)

    chatbot.like(print_like_dislike, None, None)

demo.queue()
if __name__ == "__main__":
    demo.launch()

