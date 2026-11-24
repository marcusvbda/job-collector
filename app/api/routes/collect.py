from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.collect import CollectService

router = APIRouter(prefix="/collect", tags=["collect"])


class CollectResponse(BaseModel):
    run_id: str
    sources: list[str]


CollectServiceDep = Annotated[CollectService, Depends()]


@router.get("", response_model=CollectResponse)
async def collect() -> CollectResponse:
    sources = CollectServiceDep.getSources()
    return CollectResponse(run_id=str(uuid4()), sources=sources)
