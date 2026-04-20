# Extending PULQ

## Custom `TaskRepository`

Implement {py:class}`pulq.types.TaskRepository` with:

* `schedule(task)` — enqueue a {py:class}`pulq.models.Task` in `PENDING` state.
* `claim_next_pending(priority, worker_id)` — return a claimed `RUNNING` {py:class}`pulq.models.Task`
  or {py:class}`pulq.models.NoPendingTask` for that `priority`.
* `mark_complete(task_id, result)` — persist terminal state; treat `result["ok"] is False` as failure.

Keep claims **atomic** if multiple workers pull concurrently.

Bundled production-oriented backend: {py:class}`pulq.storage.redis.RedisTaskRepository` (requires ``pip install pulq[redis]``). It uses a Redis LIST per priority plus task hashes, with batched reads/writes under a per-priority lock so behavior matches {py:class}`~pulq.storage.memory.InMemoryTaskRepository` (including capability rotation). See ``examples/redis_local/basic.py`` and a local Redis instance (e.g. ``docker run -p 6379:6379 redis:7``).

## Custom `Transport`

Implement {py:class}`pulq.types.Transport` to serialize `WorkResponse` over HTTP, gRPC, Redis, etc.

* :meth:`~pulq.types.Transport.setup_transport` / :meth:`~pulq.types.Transport.teardown_transport` — prepare and release wire resources (no-ops for in-process transports).
* :meth:`~pulq.types.Transport.__aenter__` / :meth:`~pulq.types.Transport.__aexit__` — must delegate to setup/teardown (``Worker`` runs ``async with transport``).
* :meth:`~pulq.types.Transport.request_work` / :meth:`~pulq.types.Transport.report_completion` — pull and complete.
* Server decodes JSON → {py:func}`pulq.parse_work_response` (Pydantic validates using discriminated unions).
* Client encodes models with `.model_dump(mode="json")`.

The core {py:class}`pulq.core.pull_queue.PullQueue` stays identical; only the transport changes.
Bundled reference: {py:class}`pulq.transport.http.HttpTransport` (requires `pip install pulq[http]`). Workers resolve tasks using {py:class}`pulq.core.handler_registry.HandlerRegistry` and each task’s {attr}`~pulq.models.task.Task.handler_name`.

## Management commands

Use {py:class}`pulq.models.CommandType` enums (`STOP`, `PAUSE`, `RESUME`). Per-worker queues live in
{py:class}`pulq.core.dispatcher.CommandDispatcher` (exposed as `PullQueue.commands`).
