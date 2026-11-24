import json

import httpx

from app.core.config import get_settings
from app.models.job import JobModel

from .source import SourceBase

API_URL = "https://realjobsfromanywhere.com/api/trpc/jobs.getJobListings"
PAGE_SIZE = 100  # the API rejects limit > 100


class RealJobsFromAnywhereSource(SourceBase):
    def __init__(self) -> None:
        super().__init__("realjobsfromanywhere")

    async def collect(self) -> list[JobModel]:
        headers = {"Accept": "application/json", "User-Agent": "talent-labs-bot/1.0"}
        max_pages = get_settings().realjobs_max_pages
        jobs: list[JobModel] = []

        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            page = 1
            while page <= max_pages:
                batch_input = {"0": {"page": page, "limit": PAGE_SIZE, "search": ""}}
                r = await client.get(
                    API_URL,
                    params={"batch": 1, "input": json.dumps(batch_input)},
                )
                r.raise_for_status()

                data = r.json()[0]["result"]["data"]
                jobs.extend(self._to_job(item) for item in data["jobs"])

                if page >= data["pagination"]["totalPages"]:
                    break
                page += 1

        return jobs

    @staticmethod
    def _to_job(item: dict) -> JobModel:
        company = item.get("company") or {}
        return JobModel(
            external_id=str(item["id"]),
            title=item["title"],
            url=item["applyUrl"],
            company=company.get("name"),
            location=item.get("location"),
            posted_at=item.get("postedDate"),
        )
