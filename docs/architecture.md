# Architecture

## Components

* **Worker** → **Transport** → **PullQueue** → **CommandDispatcher** / **DeficitScheduler** / **TaskRepository**

* **PullQueue** — orchestrates heartbeat hooks, management commands, WDRR, and storage claims.
* **DeficitScheduler** — pure deficit ledger (credits per epoch, debit on claim, zero-out on empty priority).
* **CommandDispatcher** — per-`worker_id` FIFO of {py:class}`pulq.models.ManagementCommand`.
* **TaskRepository** — protocol for enqueue + atomic claim + completion (default: {py:class}`pulq.storage.memory.InMemoryTaskRepository`).
* **Transport** — protocol for `request_work` / `report_completion` (default: {py:class}`pulq.transport.local.LocalTransport`).

## Data models (`pulq.models`)

The package groups Pydantic types by concern:

* {py:mod}`pulq.models.enums` — `TaskStatus`, `CommandType`, `NoWorkReason`
* {py:mod}`pulq.models.task` — `Task`
* {py:mod}`pulq.models.work` — `ManagementCommand`, `NoWork`, `NoPendingTask`
* {py:mod}`pulq.models.unions` — `WorkResponse` and `ClaimResult` type aliases with discriminated union validation
* {py:mod}`pulq.models.scheduler_config` — `DeficitSchedulerConfig` (WDRR parameters; also re-exported from {py:mod}`pulq.core.scheduler` for convenience)

Wire formats are parsed with {py:mod}`pulq.parsing` using Pydantic's `TypeAdapter`.

## Discriminated unions

Work items returned from pulls use a `type` discriminator:

* `task` → {py:class}`pulq.models.Task`
* `command` → {py:class}`pulq.models.ManagementCommand`
* `no_work` → {py:class}`pulq.models.NoWork` (null object instead of `None`)

Use {py:func}`pulq.parse_work_response` to validate untrusted data. Pydantic's discriminated union validation automatically handles routing to the correct model based on the `type` field.
