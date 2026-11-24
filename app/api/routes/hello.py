from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/hello", tags=["hello"])


class HelloResponse(BaseModel):
    message: str


@router.get("", response_model=HelloResponse, summary="Hello world")
async def hello() -> HelloResponse:
    return HelloResponse(message="Hello, World!")
