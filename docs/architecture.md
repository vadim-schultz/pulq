# Architecture

## Components

* **Worker** → **Transport** → **PullQueue** → **CommandDispatcher** / **DeficitScheduler** / **TaskRepository**

* **PullQueue** — orchestrates heartbeat hooks, management commands, WDRR, and storage claims. Constructor options are grouped in {py:class}`pulq.core.queue_config.PullQueueConfig` (defaults give a standard three-priority WDRR setup).
* **Worker** — pull loop; idle delay via {py:class}`pulq.models.worker_config.WorkerConfig`, task dispatch and lifecycle hooks via {py:class}`pulq.core.handler_registry.HandlerRegistry` (or a single handler wrapped as the registry default).
* **DeficitScheduler** — pure deficit ledger (credits per epoch, debit on claim, zero-out on empty priority).
* **CommandDispatcher** — per-`worker_id` FIFO of {py:class}`pulq.models.ManagementCommand`.
* **TaskRepository** — protocol for enqueue + atomic claim + completion (default: {py:class}`pulq.storage.memory.InMemoryTaskRepository`).

### Storage backends

The bundled {py:class}`~pulq.storage.memory.InMemoryTaskRepository` is a **reference implementation** for tests and single-process runs: it does not persist tasks or coordinate across processes.

For shared storage, install ``pulq[redis]`` and use {py:class}`~pulq.storage.redis.RedisTaskRepository`: Redis LISTs per priority, task documents in hashes, and atomic claims under a per-priority lock (same scheduling semantics as the in-memory backend). Other databases remain supported by implementing {py:class}`~pulq.types.TaskRepository` yourself.
* **Transport** — protocol for async context (``setup_transport`` / ``teardown_transport``), `request_work` / `report_completion` (default: {py:class}`pulq.transport.local.LocalTransport`).

## Data models (`pulq.models`)

The package groups Pydantic types by concern:

* {py:mod}`pulq.models.enums` — `TaskStatus`, `CommandType`, `NoWorkReason`
* {py:mod}`pulq.models.task` — `Task`
* {py:mod}`pulq.models.work` — `ManagementCommand`, `NoWork`, `NoPendingTask`
* {py:mod}`pulq.models.unions` — `WorkResponse` and `ClaimResult` type aliases with discriminated union validation
* {py:mod}`pulq.models.scheduler_config` — `DeficitSchedulerConfig` (WDRR parameters; embedded in `PullQueueConfig.scheduler`; also re-exported from {py:mod}`pulq.core.scheduler` for convenience)
* {py:mod}`pulq.core.queue_config` — `PullQueueConfig` (queue-level settings, including optional `commands` injection for tests)
* {py:mod}`pulq.models.worker_config` — `WorkerConfig`
* {py:mod}`pulq.core.handler_registry` — `HandlerRegistry`

Wire formats are parsed with {py:mod}`pulq.parsing` using Pydantic's `TypeAdapter`.

## Discriminated unions

Work items returned from pulls use a `type` discriminator:

* `task` → {py:class}`pulq.models.Task`
* `command` → {py:class}`pulq.models.ManagementCommand`
* `no_work` → {py:class}`pulq.models.NoWork` (null object instead of `None`)

Use {py:func}`pulq.parse_work_response` to validate untrusted data. Pydantic's discriminated union validation automatically handles routing to the correct model based on the `type` field.
