# Getting started

## Install

```bash
pip install pulq
```

## Editable install (development)

```bash
git clone https://github.com/vadim-schultz/pulq.git
cd pulq
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Minimal example

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
    return {"ok": True}

async def main() -> None:
    repo = InMemoryTaskRepository()
    queue = PullQueue(
        repo,
        priority_order=("high", "medium", "low"),
        weights={"high": 3, "medium": 2, "low": 1},
    )
    await queue.schedule(Task(priority="high", payload={"job": "example"}))
    transport = LocalTransport(queue)
    worker = Worker(transport, "worker-1", handle, no_work_delay_seconds=0.01)

    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        queue.send_command("worker-1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_later())

asyncio.run(main())
```

See also the `examples/` directory in the repository.
