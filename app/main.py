from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.config import HTTPProtocolType
from dependencies import get_query_token, get_token_header
from internal import admin
from routers import items, users, memory, wellknown
from fastapi.openapi.utils import get_openapi

app = FastAPI()#dependencies=[Depends(get_query_token)])

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wellknown.wellknown)
app.include_router(memory.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        summary="This is a very custom OpenAPI schema",
        description="Here's a longer description of the custom **OpenAPI** schema",
        routes=app.routes,
        servers=[{ "url": "https://bbe3-100-34-174-93.ngrok-free.app" }]
    )    
    openapi_schema["info"]["x-logo"]  = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

#app.include_router(users.router)
#app.include_router(items.router)
#app.include_router(
#    admin.router,
#    prefix="/admin",
#    tags=["admin"],
#    dependencies=[Depends(get_token_header)],
#    responses={418: {"description": "I'm a teapot"}},
#)


#@app.get("/")
#async def root():
#    return {"message": "Hello Bigger Applications!"}

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)