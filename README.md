# PULQ

**Fair task scheduling with async pull — WDRR-based priority queue for Python**

[![CI](https://github.com/vadim-schultz/pulq/actions/workflows/ci.yml/badge.svg)](https://github.com/vadim-schultz/pulq/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/pulq/badge/?version=latest)](https://pulq.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/vadim-schultz/pulq/branch/main/graph/badge.svg)](https://codecov.io/gh/vadim-schultz/pulq)
[![PyPI version](https://img.shields.io/pypi/v/pulq)](https://pypi.org/project/pulq/)

[![Python versions](https://img.shields.io/pypi/pyversions/pulq)](https://pypi.org/project/pulq/)
[![License](https://img.shields.io/pypi/l/pulq)](https://github.com/vadim-schultz/pulq/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Typing: Strict](https://img.shields.io/badge/typing-strict-blue)](https://github.com/vadim-schultz/pulq/blob/main/pyproject.toml)

PULQ schedules **pull-based** work across named priority buckets using **Weighted Deficit Round Robin (WDRR)** so higher-weight classes get proportionally more CPU time without starving lower classes. Management commands (e.g. **STOP**) are delivered per worker ahead of normal tasks.

## Install

```bash
pip install pulq
```

## Quick start

```python
import asyncio

from pulq import (
    CommandType,
    InMemoryTaskRepository,
    LocalTransport,
    PullQueue,
    Task,
    Worker,
)

async def handle(task: Task) -> dict:
    return {"ok": True, "echo": task.payload}

async def main() -> None:
    repo = InMemoryTaskRepository()
    queue = PullQueue(
        repo,
        priority_order=("high", "medium", "low"),
        weights={"high": 3, "medium": 2, "low": 1},
        quantum=1,
    )
    await queue.schedule(Task(priority="high", payload={"job": "a"}))
    await queue.schedule(Task(priority="low", payload={"job": "b"}))

    transport = LocalTransport(queue)
    worker = Worker(transport, "worker-1", handle, no_work_delay_seconds=0.01)

    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        queue.send_command("worker-1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_later())

asyncio.run(main())
```

## Documentation

Full docs: **[pulq.readthedocs.io](https://pulq.readthedocs.io/)**

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check src tests
mypy src
pytest
```

## License

MIT — see [LICENSE](LICENSE).
