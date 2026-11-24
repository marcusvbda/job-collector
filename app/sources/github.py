from .source import SourceBase


class GithubSource(SourceBase):
    def __init__(self):
        super().__init__("github")
