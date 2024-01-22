from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uvicorn.config import HTTPProtocolType
#from dependencies import get_query_token, get_token_header
from routers import memory, wellknown
from fastapi.openapi.utils import get_openapi
from routers.wellknown import get_ai_plugin

app = FastAPI()#dependencies=[Depends(get_query_token)])

origins = ["*",]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wellknown.router)
app.include_router(memory.router)

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

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Memory Bank API"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7000)