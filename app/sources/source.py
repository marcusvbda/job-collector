from app.models.job import JobModel


class SourceBase:
    """Base class for job sources (API, scraper, feed, ...).

    Sources run concurrently on the event loop, so ``collect`` must not block it:
    use async clients (e.g. ``httpx.AsyncClient``) and wrap any blocking work
    (``requests``, BeautifulSoup parsing of large pages, sync SDKs, ...) with
    ``await asyncio.to_thread(...)``.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    async def collect(self) -> list[JobModel]:
        return []
