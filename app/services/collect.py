from app.sources.github import GithubSource

ENABLED_SOURCES = [GithubSource]


class CollectService:
    def getSources():
        return [source().name for source in ENABLED_SOURCES]
