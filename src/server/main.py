import llama_index

from src.server.di import create_application_injector
from src.server.launcher import create_app

# Add LlamaIndex simple observability
llama_index.set_global_handler("simple")

# Create the FastAPI application
injector = create_application_injector()
app = create_app(injector)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7000)