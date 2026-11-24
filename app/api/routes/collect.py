from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from pydantic import BaseModel, HttpUrl

from app.services.collect import CollectService

router = APIRouter(prefix="/collect", tags=["collect"])


class CollectResponse(BaseModel):
    run_id: str


CollectServiceDep = Annotated[CollectService, Depends()]


@router.get(
    "",
    response_model=CollectResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def collect(
    postback_url: Annotated[
        HttpUrl, Query(description="URL that will receive the postback")
    ],
    service: CollectServiceDep,
    background_tasks: BackgroundTasks,
) -> CollectResponse:
    run_id = str(uuid4())
    background_tasks.add_task(service.run_and_notify, run_id, str(postback_url))
    return CollectResponse(run_id=run_id)
