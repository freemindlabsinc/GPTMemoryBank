from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dependencies import get_query_token, get_token_header
from internal import admin
from routers import items, users, memory

app = FastAPI(dependencies=[Depends(get_query_token)])

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

app.include_router(memory.router)

#app.include_router(users.router)
#app.include_router(items.router)
#app.include_router(
#    admin.router,
#    prefix="/admin",
#    tags=["admin"],
#    dependencies=[Depends(get_token_header)],
#    responses={418: {"description": "I'm a teapot"}},
#)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)