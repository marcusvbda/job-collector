import logging
from enum import StrEnum

import httpx
from pydantic import BaseModel

from app.core.config import get_settings
from app.models.job import JobModel
from app.sources.github import GithubSource

logger = logging.getLogger(__name__)

ENABLED_SOURCES = [GithubSource]


class RunStatus(StrEnum):
    COLLECTING = "collecting"
    COMPLETED = "completed"
    FAILED = "failed"


class PostbackPayload(BaseModel):
    run_id: str
    status: RunStatus
    source: str | None = None
    jobs: list[JobModel] = []
    error: str | None = None


class CollectService:
    async def run_and_notify(self, run_id: str, postback_url: str) -> None:
        last_index = len(ENABLED_SOURCES) - 1

        for index, source in enumerate(ENABLED_SOURCES):
            instance = source()
            try:
                jobs = await instance.collect()
            except Exception as exc:
                logger.exception("Collect run %s failed on %s", run_id, instance.name)
                await self._send_postback(
                    postback_url,
                    PostbackPayload(
                        run_id=run_id,
                        status=RunStatus.FAILED,
                        source=instance.name,
                        error=str(exc),
                    ),
                )
                return

            status = (
                RunStatus.COMPLETED if index == last_index else RunStatus.COLLECTING
            )
            await self._send_postback(
                postback_url,
                PostbackPayload(
                    run_id=run_id, status=status, source=instance.name, jobs=jobs
                ),
            )

        if not ENABLED_SOURCES:
            await self._send_postback(
                postback_url,
                PostbackPayload(run_id=run_id, status=RunStatus.COMPLETED),
            )

    async def _send_postback(self, url: str, payload: PostbackPayload) -> None:
        timeout = get_settings().webhook_timeout
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(url, json=payload.model_dump(mode="json"))
                r.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Postback delivery failed for run %s", payload.run_id)
