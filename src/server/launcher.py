import loguru

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from injector import Injector

def setup_cors(app: FastAPI):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"])    
    
def setup_routers(app: FastAPI):    
    from src.routers import memory, wellknown, resources

    app.include_router(wellknown.router)
    app.include_router(memory.router)
    app.include_router(resources.router)
    
def setup_openapi(app: FastAPI):
    from fastapi.openapi.utils import get_openapi
    from src.routers.wellknown import get_ai_plugin
    
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

def create_app(root_injector: Injector) -> FastAPI:
    # Start the API
    async def bind_injector_to_request(request: Request) -> None:
        request.state.injector = root_injector

    app = FastAPI(dependencies=[Depends(bind_injector_to_request)])
    setup_cors(app)
    setup_routers(app)
    setup_openapi(app)
        
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Memory Bank API"}
    
    return app