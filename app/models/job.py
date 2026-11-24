from datetime import datetime

from pydantic import BaseModel


class JobModel(BaseModel):
    external_id: str
    title: str
    url: str
    description: str = ""
    company: str | None = None
    location: str | None = None
    posted_at: datetime | None = None
