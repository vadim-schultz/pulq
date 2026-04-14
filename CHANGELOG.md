# Changelog

## 0.1.1 — 2026-04-14

### Added

* `PullQueueConfig` in `pulq.core.queue_config` for validated queue settings: nested `DeficitSchedulerConfig`, optional `commands` injection (tests / custom wiring), and optional `on_heartbeat`.
* `WorkerConfig` and `WorkerHooks` in `pulq.models.worker_config` for idle delay and lifecycle hooks (`startup`, `shutdown`, `before_process`, `after_process`).

### Changed

* `DeficitSchedulerConfig` is constructible with no arguments; defaults match the common three-priority WDRR setup (`high` / `medium` / `low`, weights 3:2:1, `quantum` 1).
* `Worker` default `no_work_delay_seconds` is now `0.01` when using default `WorkerConfig` (reduces busy-wait when the queue is idle).
* Documentation and examples emphasize zero-config usage first, then configuration objects.

### Breaking

* **`PullQueue`**: `__init__` is now `PullQueue(repository, *, config=None)` only. The previous keyword arguments (`priority_order`, `weights`, `quantum`, `commands`, `deficits`, `on_heartbeat`) are replaced by `PullQueueConfig`. Injected `DeficitScheduler` instances (`deficits=`) are no longer supported; the scheduler is always built from `config.scheduler`.
* **`Worker`**: `__init__` is now `Worker(transport, worker_id, handler, *, config=None)` only. Hook and delay parameters move to `WorkerConfig` / `WorkerHooks`.

## 0.1.0 — 2026-04-13

* Initial release: `PullQueue`, WDRR `DeficitScheduler`, `CommandDispatcher`, `InMemoryTaskRepository`, `LocalTransport`, `Worker`.
* Pydantic models under `pulq.models` (`enums`, `task`, `work`, `unions`, `scheduler_config`) with discriminated unions (`Task`, `ManagementCommand`, `NoWork`, `NoPendingTask`).
* JSON parsing helpers in `pulq.parsing` (`parse_work_response`, `parse_claim_result`).
* Documentation on Read the Docs and GitHub Actions CI.
