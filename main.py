import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from schemas import URLCreate

app = FastAPI()


db = {}


@app.post("/shorten")
def shorten_url(data: URLCreate):
    if data.short_url in db:
        raise HTTPException(status_code=409, detail="Already exists")

    exc = HTTPException(status_code=400, detail="Inaccessible URL")
    try:
        response = httpx.get(data.url, follow_redirects=True)
    except httpx.ConnectError:
        raise exc
    if response.status_code != 200:
        raise exc
    db[data.short_url.lower()] = data.url
    return "", 200


@app.get("/{short_url}")
def redirect(short_url: str):
    if short_url in db:
        return RedirectResponse(url=db[short_url.lower()])
    raise HTTPException(status_code=404, detail="Not found")
