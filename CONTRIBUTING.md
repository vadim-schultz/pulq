# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

```bash
ruff check src tests examples benchmarks
ruff format src tests examples benchmarks
mypy src
pytest
```

## Docs

```bash
pip install -e ".[docs]"
sphinx-build -W -b html docs docs/_build
```

Pull requests should keep CI green (Ruff, Mypy, Pytest, Sphinx `-W`).
