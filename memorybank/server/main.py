import llama_index

from memorybank.server.di import global_injector
from memorybank.server.launcher import create_app

# Add LlamaIndex simple observability
llama_index.set_global_handler("simple")

# Setup dependency injection
injector = global_injector

# Create the FastAPI application
app = create_app(injector)

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="127.0.0.1", port=7000)