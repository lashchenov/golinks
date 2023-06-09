import uuid
from collections import defaultdict

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from schemas import URLCreate, URLList

app = FastAPI()

db = defaultdict(dict)
sharedb = defaultdict(dict)
share_key = "share"

@app.post("/shorten")
def shorten_url(data: URLCreate, request: Request, response: Response):
    session_key = request.cookies.get("session_key", None)
    if session_key is None:
        session_key = str(uuid.uuid4())

    if session_key in db and data.short_url.lower() in db[session_key]:
        raise HTTPException(status_code=409, detail="Already exists")

    exc = HTTPException(status_code=400, detail="Inaccessible URL")
    try:
        result = httpx.get(data.url, follow_redirects=True)
    except httpx.ConnectError:
        raise exc
    if result.status_code != 200:
        raise exc
    db[session_key][data.short_url.lower()] = data.url
    response.set_cookie(key="session_key", value=session_key)
    return "", 200

@app.post("/s/shorten")
def shorten_url(data: URLCreate, request: Request, response: Response):

    if share_key in sharedb and data.short_url.lower() in sharedb[share_key]:
        raise HTTPException(status_code=409, detail="Already exists")

    exc = HTTPException(status_code=400, detail="Inaccessible URL")
    try:
        result = httpx.get(data.url, follow_redirects=True)
    except httpx.ConnectError:
        raise exc
    if result.status_code != 200:
        raise exc
    sharedb[share_key][data.short_url.lower()] = data.url
    response.set_cookie(key="share_key", value=share_key)
    return "", 200

@app.get("/list")
def list_urls_for_user(request: Request):
    session_key = request.cookies.get("session_key")
    if session_key not in db:
        return URLList(urls=[])
    return URLList(urls=[URLCreate(short_url=k, url=v) for k, v in db[session_key].items()])

@app.get("/s/list")
def list_urls_for_user(request: Request):
    if share_key not in sharedb:
        return URLList(urls=[])
    return URLList(urls=[URLCreate(short_url=k, url=v) for k, v in sharedb[share_key].items()])

# Old list
# @app.get("/{short_url}")
# def redirect(short_url: str, request: Request):
#     session_key = request.cookies.get("session_key")
#     exc = HTTPException(status_code=404, detail="Not found")
#     if session_key not in db:
#         raise exc
#     if short_url not in db[session_key]:
#         raise exc
#     if short_url in db[session_key]:
#         return RedirectResponse(url=db[session_key][short_url.lower()])

# Prioritize personal over shared
@app.get("/{short_url}")
def redirect(short_url: str, request: Request):
    session_key = request.cookies.get("session_key")
    exc = HTTPException(status_code=404, detail="Not found")
    if session_key in db and short_url in db[session_key]:
        return RedirectResponse(url=db[session_key][short_url.lower()])
    elif share_key in sharedb and short_url in sharedb[share_key]:
        return RedirectResponse(url=sharedb[share_key][short_url.lower()])
    else:
        raise exc


# @app.delete("/{short_url}")
# def remove(short_url: str, request: Request):
#     session_key = request.cookies.get("session_key")
#     exc = HTTPException(status_code=404, detail="Not found")
#     session_key = request.cookies.get("session_key")
#     if session_key not in db:
#         raise exc
#     if short_url not in db[session_key]:
#         raise exc
#     if short_url in db[session_key]:
#         db[session_key].pop(short_url)
#         return "", 204