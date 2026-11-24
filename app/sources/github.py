import httpx

from app.models.job import JobModel

from .source import SourceBase

JOB_REPOS = [
    "phpdevbr/vagas",
    "dotnetdevbr/vagas",
    "backend-br/vagas",
    "programadores-br/geral",
    "frontendbr/vagas",
    "react-brasil/vagas",
    "frontend-pt/vagas",
]


class GithubSource(SourceBase):
    def __init__(self) -> None:
        super().__init__("github")

    async def collect(self) -> list[JobModel]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "talent-labs-bot/1.0",
        }
        jobs: list[JobModel] = []
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            for repo in JOB_REPOS:
                r = await client.get(
                    f"https://api.github.com/repos/{repo}/issues",
                    params={"state": "open", "per_page": 100},
                )
                r.raise_for_status()

                for issue in r.json():
                    if "pull_request" in issue:
                        continue

                    jobs.append(
                        JobModel(
                            external_id=str(issue["id"]),
                            title=issue["title"],
                            url=issue["html_url"],
                            description=issue["body"] or "",
                            posted_at=issue["created_at"],
                        )
                    )

        return jobs
