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

The defaults match the common three-tier setup (high / medium / low with 3:2:1 weights). Schedule tasks, attach a local transport, run a worker, and stop it with a management command:

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
    queue = PullQueue(repo)
    await queue.schedule(Task(priority="high", handler_name="default", payload={"job": "example"}))
    transport = LocalTransport(queue)
    worker = Worker(transport, "worker-1", handle)

    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        queue.send_command("worker-1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_later())

asyncio.run(main())
```

## Configuration objects

When you need different WDRR parameters, an optional heartbeat on each pull, or worker lifecycle hooks, use `PullQueueConfig`, `HandlerRegistry`, and `WorkerConfig`:

```python
from pulq import (
    DeficitSchedulerConfig,
    HandlerRegistry,
    PullQueueConfig,
    WorkerConfig,
)

queue = PullQueue(
    repo,
    config=PullQueueConfig(
        scheduler=DeficitSchedulerConfig(
            priority_order=("urgent", "normal"),
            weights={"urgent": 2, "normal": 1},
        ),
    ),
)

async def on_start() -> None:
    ...

registry = HandlerRegistry(default=handle, startup=on_start)
worker = Worker(
    transport,
    "worker-1",
    registry,
    config=WorkerConfig(no_work_delay_seconds=0.02),
)
```

See {doc}`transports` for HTTP and repository notes, and the `examples/` directory in the repository.
