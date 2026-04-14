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

`PullQueue` and `Worker` use **sensible defaults** so you can schedule tasks and run a worker with almost no configuration:

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
    queue = PullQueue(repo)  # default: high / medium / low with 3:2:1 weights, quantum 1
    await queue.schedule(Task(priority="high", payload={"job": "a"}))
    await queue.schedule(Task(priority="low", payload={"job": "b"}))

    transport = LocalTransport(queue)
    worker = Worker(transport, "worker-1", handle)  # default short backoff when idle

    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        queue.send_command("worker-1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_later())

asyncio.run(main())
```

### Customizing with Pydantic config

For different priorities, weights, quantum, or worker hooks, pass validated config objects:

```python
from pulq import DeficitSchedulerConfig, PullQueueConfig, WorkerConfig, WorkerHooks

queue = PullQueue(
    repo,
    config=PullQueueConfig(
        scheduler=DeficitSchedulerConfig(
            priority_order=("critical", "high", "low"),
            weights={"critical": 5, "high": 3, "low": 1},
            quantum=2,
        ),
    ),
)

worker = Worker(
    transport,
    "worker-1",
    handle,
    config=WorkerConfig(
        no_work_delay_seconds=0.05,
        hooks=WorkerHooks(startup=my_startup, shutdown=my_shutdown),
    ),
)
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
