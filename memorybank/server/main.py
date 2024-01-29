import llama_index

from memorybank.server.di import setup_services
from memorybank.server.appbuilder import create_app

# Add LlamaIndex simple observability
llama_index.set_global_handler("simple")

# Create the FastAPI application
app_injector = setup_services()
app = create_app(app_injector)

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="127.0.0.1", port=7000)