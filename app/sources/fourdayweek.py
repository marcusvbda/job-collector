from datetime import UTC, datetime

import httpx

from app.core.config import get_settings
from app.models.job import JobModel

from .source import SourceBase

API_URL = "https://4dayweek.io/api/jobs"
JOB_URL = "https://4dayweek.io/remote-job/{slug}"
PAGE_SIZE = 100


class FourDayWeekSource(SourceBase):
    def __init__(self) -> None:
        super().__init__("4dayweek")

    async def collect(self) -> list[JobModel]:
        headers = {"Accept": "application/json", "User-Agent": "talent-labs-bot/1.0"}
        max_pages = get_settings().fourdayweek_max_pages
        jobs: list[JobModel] = []

        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            page = 1
            while page <= max_pages:
                r = await client.get(API_URL, params={"page": page, "limit": PAGE_SIZE})
                r.raise_for_status()

                data = r.json()
                for item in data["jobs"]:
                    # Fresh jobs are paywalled: the API hides slug and company,
                    # so there is no public URL to point to.
                    if item.get("locked") or item.get("is_expired") or not item["slug"]:
                        continue
                    jobs.append(self._to_job(item))

                if not data["has_more"]:
                    break
                page += 1

        return jobs

    @staticmethod
    def _to_job(item: dict) -> JobModel:
        return JobModel(
            external_id=str(item["id"]),
            title=item["title"],
            url=JOB_URL.format(slug=item["slug"]),
            company=item["company_name"] or None,
            location=_location(item),
            posted_at=datetime.fromtimestamp(item["posted"], tz=UTC),
        )


def _location(item: dict) -> str | None:
    locations = item.get("locations") or []
    primary = next((loc for loc in locations if loc.get("is_primary")), None)
    loc = primary or (locations[0] if locations else None)
    if loc is None:
        return item.get("work_arrangement")
    parts = [loc.get("city"), loc.get("country")]
    return ", ".join(p for p in parts if p) or item.get("work_arrangement")
