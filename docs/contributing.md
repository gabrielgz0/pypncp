# Contribuindo

## Requisitos

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/gabrielgz0/pypncp
cd pypncp
uv sync
```

## Rodar verificações

```bash
uv run pytest -v
uv run ruff check src/ tests/
uv run mypy src/
```

## Licença

MIT
