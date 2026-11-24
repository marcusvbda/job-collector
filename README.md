# Job Collector

FastAPI service.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Getting started

```sh
cp .env.example .env
make dev
```

- API: http://127.0.0.1:8000/api/v1/hello
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Commands

Run `make help` to list all targets (`dev`, `test`, `lint`, `format`, `typecheck`, `check`).

## Layout

```
app/
├── main.py          # app factory
├── api/
│   ├── router.py    # versioned API router
│   └── routes/      # one module per resource
└── core/
    └── config.py    # pydantic-settings
tests/
```
