import os
import gradio as gr

from llama_index.vector_stores.types import VectorStoreQueryMode
from llama_index.response_synthesizers.type import ResponseMode
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

async def run_query(
    message: str, 
    top_k: int, 
    response_mode: ResponseMode, 
    vector_query_mode: VectorStoreQueryMode) -> str:
    global last_query  # Declare the global variable inside the function
    try:    
        if message is None or message == "":
            if last_query is not None:
                message = last_query  # Set the current question to the last one if it's not None
            else:
                return "No question provided."        
        else:
            last_query = message  # Update the last question if the current one is not empty

        query = Query(text=message)
        query.top_k = top_k
        vector_query_mode = VectorStoreQueryMode[vector_query_mode]
        query.query_mode = vector_query_mode
        
        response_mode = ResponseMode[response_mode]
        query.response_mode = response_mode
        
        response = await memory_store.query(query)
            
        full_response = f"""
**Answer**
{response.answer}

**Links**
{response.formatted_sources}

**Query**
```
{query}
```
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


async def bot(history, top_k: int, response_mode: ResponseMode, vector_query_mode: VectorStoreQueryMode):
    try:
        if len(history) == 0:
            return history
        
        bot_response = history[-1][1] is not None
        if bot_response:
            return history
        
        user_question = history[-1][0]
        if (user_question == ""):
            user_question = last_query
                    
            
        try:
            response = await run_query(
                message=user_question, 
                top_k=top_k, 
                response_mode=response_mode, 
                vector_query_mode=vector_query_mode)
        except Exception as e:
            response = f"Error: {e}"
        
        # sets the bot response
        history[-1][1] = response        
    
    except Exception as e:
        history = history + [(f"Error: {e}", None)]
    
    finally:
        return history
    

def create_chat_tab():
    with gr.Blocks() as tab:    
        chatbot = _create_chatbot()        
            
        with gr.Row():
            txt = _create_textbox()
            upload_btn = _create_upload_button()
            clear_btn = _create_clear_button(chatbot, txt)
        
        with gr.Row():                
            top_k_number = _create_topk_control()        
            response_mode = _create_response_mode_dropdown()        
            vector_query_mode = _create_vectorstore_query_mode()
            
        
        txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=use_queue)
        txt_msg.then(bot, [chatbot, top_k_number, response_mode, vector_query_mode], [chatbot])
        txt_msg.then(_create_textbox, None, [txt], queue=use_queue)
        
        file_msg = upload_btn.upload(add_files, [chatbot, upload_btn], [chatbot], queue=use_queue)
        file_msg.then(bot, [chatbot, top_k_number, response_mode, vector_query_mode], [chatbot])

        chatbot.like(print_like_dislike, None, None)    

        return tab

    
def _create_chatbot():
    return gr.Chatbot(
        [(None, appSettings.prompt.first_prompt)],
        #label = "Chat",
        line_breaks=True,
        render_markdown=True,
        elem_id="chatbot",
        bubble_full_width=False,
        show_share_button=True,
        show_copy_button=True,
        # FIXME this shows the file path
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "icon.png")))        
    )    
    
def _create_textbox():
    
    return gr.Textbox(
        
        scale=4,        
        elem_id="textbox",
        show_label=False,
        placeholder="Enter text and press enter, or upload a text file or audio file.",
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

def _create_topk_control():
    return gr.Number(
            label="Top K", 
            value=3, 
            minimum=1,
            maximum=100,
            step=1, 
            info="Sets number of nearest neighbors to return."
        )

def _create_response_mode_dropdown():
    response_mode_names = list(ResponseMode.__members__.keys())
    default1 = ResponseMode.COMPACT
    response_mode = gr.Dropdown(
            response_mode_names, 
            label="Response Mode", 
            info="Sets response modes of the response builder (and synthesizer).",
            value=default1.upper()
        )
    
    return response_mode

def _create_vectorstore_query_mode():
    vector_store_query_mode_names = list(VectorStoreQueryMode.__members__.keys())        
    default2 = str(VectorStoreQueryMode.DEFAULT).split('.')[-1].lower()
    vector_query_mode = gr.Dropdown(
            vector_store_query_mode_names, 
            label="Query Mode", 
            info="Sets the vector store query mode.",
            value=default2.upper()
        )
    
    return vector_query_mode

def _create_clear_button(chatbot, txt):
    return gr.ClearButton([txt, chatbot])