# Transports and storage

## Transports

Workers talk to a queue only through {py:class}`pulq.types.Transport`:

* **Local** — {py:class}`pulq.transport.local.LocalTransport` calls {py:class}`pulq.core.pull_queue.PullQueue` in-process (tests and single-process apps).
* **HTTP** — {py:class}`pulq.transport.http.HttpTransport` posts JSON to your server. :class:`~pulq.core.worker.Worker` runs ``async with`` the transport, which opens and closes the internal :class:`httpx.AsyncClient` for the worker’s lifetime. Optional :meth:`~pulq.transport.http.HttpTransport.send_command` matches the example server’s management endpoint. Install with `pip install pulq[http]` (adds `httpx` and `truststore`). A minimal Litestar integration lives under `examples/http_server/` (install its `requirements.txt` separately).

HTTP bodies are described by the Pydantic models in {py:mod}`pulq.models.http` (`RequestWorkRequest`, `ScheduleTaskRequest`, etc.) so you can wire the same shapes into any ASGI framework.

## Task routing (`handler_name`)

Every {py:class}`pulq.models.Task` carries a **handler_name** string. The worker resolves it through {py:class}`pulq.core.handler_registry.HandlerRegistry` (or a single callable, which is wrapped as `HandlerRegistry(default=...)`). This matches common RPC-style dispatch and works the same for local and remote transports.

Lifecycle hooks (`startup`, `shutdown`, `before_process`, `after_process`) live on `HandlerRegistry`, not on a separate hooks model.

## Repositories

{py:class}`pulq.storage.memory.InMemoryTaskRepository` keeps state in the process that owns the `PullQueue`. For HTTP, the **queue server** must use the repository that backs scheduling; workers only pull/complete via transport. A shared backend (e.g. Redis) is the next step for multiple queue processes; until then, treat in-memory + HTTP as a **demo** unless both sides share one logical store. # TODO: provide own repos for queue / workers

## Further reading

* {doc}`extending` — implementing `TaskRepository` and `Transport`.
* {doc}`architecture` — data flow between worker, transport, and queue.
