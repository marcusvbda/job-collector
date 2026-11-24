from app.models.job import JobModel


class SourceBase:
    def __init__(self, name: str) -> None:
        self.name = name

    async def collect(self) -> list[JobModel]:
        return []
