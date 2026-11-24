import asyncio
import logging
from collections.abc import Callable
from enum import StrEnum

import httpx
from pydantic import BaseModel

from app.core.config import get_settings
from app.models.job import JobModel
from app.sources.github import GithubSource
from app.sources.source import SourceBase

logger = logging.getLogger(__name__)

SourceFactory = Callable[[], SourceBase]

ENABLED_SOURCES: list[SourceFactory] = [GithubSource]


class RunStatus(StrEnum):
    COLLECTING = "collecting"
    COMPLETED = "completed"
    FAILED = "failed"


class PostbackPayload(BaseModel):
    run_id: str
    status: RunStatus
    source: str | None = None
    jobs: list[JobModel] = []
    qty: int = 0
    error: str | None = None
    failed_sources: list[str] = []


class CollectService:
    async def run_and_notify(self, run_id: str, postback_url: str) -> None:
        failed_sources: list[str] = []
        total_qty = 0

        async def collect_one(factory: SourceFactory) -> None:
            name = getattr(factory, "__name__", "unknown")
            try:
                instance = factory()
                name = instance.name
                async with asyncio.timeout(get_settings().source_timeout):
                    jobs = await instance.collect()
            except Exception as exc:
                logger.exception("Collect run %s failed on %s", run_id, name)
                failed_sources.append(name)
                payload = PostbackPayload(
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    source=name,
                    error=str(exc) or type(exc).__name__,
                )
            else:
                nonlocal total_qty
                total_qty += len(jobs)
                payload = PostbackPayload(
                    run_id=run_id,
                    status=RunStatus.COLLECTING,
                    source=name,
                    jobs=jobs,
                    qty=len(jobs),
                )
            await self._send_postback(postback_url, payload)

        async with asyncio.TaskGroup() as tg:
            for factory in ENABLED_SOURCES:
                tg.create_task(collect_one(factory))

        await self._send_postback(
            postback_url,
            PostbackPayload(
                run_id=run_id,
                status=RunStatus.COMPLETED,
                qty=total_qty,
                failed_sources=failed_sources,
            ),
        )

    async def _send_postback(self, url: str, payload: PostbackPayload) -> None:
        timeout = get_settings().webhook_timeout
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(url, json=payload.model_dump(mode="json"))
                r.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Postback delivery failed for run %s", payload.run_id)
