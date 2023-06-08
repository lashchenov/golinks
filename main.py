import uuid
from collections import defaultdict

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from schemas import URLCreate, URLList

app = FastAPI()


db = defaultdict(dict)


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


@app.get("/list")
def list_urls_for_user(request: Request):
    session_key = request.cookies.get("session_key")
    if session_key not in db:
        return URLList(urls=[])
    return URLList(urls=[URLCreate(short_url=k, url=v) for k, v in db[session_key].items()])


@app.get("/{short_url}")
def redirect(short_url: str, request: Request):
    session_key = request.cookies.get("session_key")
    exc = HTTPException(status_code=404, detail="Not found")
    if session_key not in db:
        raise exc
    if short_url not in db[session_key]:
        raise exc
    if short_url in db[session_key]:
        return RedirectResponse(url=db[session_key][short_url.lower()])

