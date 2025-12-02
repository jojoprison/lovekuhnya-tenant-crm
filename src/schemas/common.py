from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


class MessageResponse(BaseModel):
    message: str
