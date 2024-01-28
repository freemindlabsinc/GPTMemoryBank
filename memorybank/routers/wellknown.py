import yaml
import json
import os
from string import Template
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, Response

router = APIRouter(prefix="/.well-known", tags=["well-known"])

def get_host(request: Request):
    host_header = request.headers.get("X-Forwarded-Host") or request.headers.get("Host")
    protocol = request.headers.get("X-Forwarded-Proto") or request.url.scheme
    return f"{protocol}://{host_header}"


def get_ai_plugin():
    currDir = os.getcwd()
    with open("./memorybank/.well-known/ai-plugin.json", encoding="utf-8") as file:
        return json.loads(file.read())

@router.get("/openapi.yaml", include_in_schema=False)
async def openapi_yaml(request: Request):
    openapi = request.app.openapi()
    openapi["servers"] = [{"url": get_host(request)}]
    ai_plugin = get_ai_plugin()
    openapi["info"]["title"] = ai_plugin["name_for_human"]
    openapi["info"]["description"] = ai_plugin["description_for_human"]
    return Response(
        content=yaml.dump(openapi),
        media_type="text/vnd.yaml",
    )


@router.get("/logo.png", include_in_schema=False)
async def logo():
    return FileResponse(".well-known/logo.png", media_type="image/png")

@router.get("/legal.txt", include_in_schema=False)
async def legal():
    return FileResponse(".well-known/legal.txt", media_type="text/plain")


@router.get("/ai-plugin.json", include_in_schema=False)
async def manifest(request: Request):
    ai_plugin = get_ai_plugin()
    return Response(
        content=Template(json.dumps(ai_plugin)).substitute(host=get_host(request)),
        media_type="application/json",
    )
