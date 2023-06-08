import validators
from pydantic import BaseModel, validator


class URLCreate(BaseModel):
    url: str
    short_url: str

    @validator("url")
    def validate_url(value):
        if validators.url(value):
            return value
        raise ValueError("Not a valid URL")


# class URLCreateResponse(URLCreate):
#     short_url: str
