from loguru import logger
from fastapi_injector import Injected

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import llama_index
from memorybank.settings.app_settings import AppSettings

def _setup_cors(app: FastAPI):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"])    
    
def _setup_routers(app: FastAPI):    
    from memorybank.routers import memory, wellknown, resources

    app.include_router(wellknown.router)
    app.include_router(memory.router)
    app.include_router(resources.router)
    
def _setup_openapi(app: FastAPI):
    from fastapi.openapi.utils import get_openapi
    from memorybank.routers.wellknown import get_ai_plugin
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        ai_plugin = get_ai_plugin()
        openapi_schema = get_openapi(
            title=ai_plugin["name_for_human"],
            version="0.0.1",
            description=ai_plugin["description_for_human"],
            routes=app.routes        
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi

def create_app() -> FastAPI:
    # Add LlamaIndex simple observability
    llama_index.set_global_handler("simple")
    
    # Add injector to request state    
    #async def bind_injector_to_request(request: Request) -> None:
    #    request.state.injector = app_injector

    # Create the FastAPI application
    app = FastAPI()#dependencies=[Depends(bind_injector_to_request)])    
    _setup_cors(app)
    _setup_routers(app)
    _setup_openapi(app)
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root(app_settings: AppSettings = Injected(AppSettings)):
        logger.info("Root endpoint called")
        return {
            "name": app_settings.service.name,
            "description": app_settings.service.description
        }        
    
    return app