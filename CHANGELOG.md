# Changelog

## 0.2.1 — 2026-04-15

### Fixed

* Optional `truststore` import in `pulq.transport.http` is now typed as `ModuleType | None`, fixing mypy and Sphinx autodoc builds when `truststore` is absent or when static analysis runs on the module.

## 0.2.0 — 2026-04-15

### Added

* `Task.handler_name` — required string for worker-side handler dispatch (RPC-style).
* `HandlerRegistry` in `pulq.core.handler_registry` — named handlers plus `default`, `startup`, `shutdown`, `before_process`, `after_process`.
* `HttpTransport` in `pulq.transport.http` (optional dependency group `pulq[http]`): `request_work` and `report_completion` over HTTP; lazy-imported from `pulq` when `httpx` is installed.
* Pydantic HTTP contract models in `pulq.models.http` (`RequestWorkRequest`, `ScheduleTaskRequest`, `SendCommandRequest`, etc.).
* `TransportHttpError` in `pulq.errors`.
* Example Litestar queue server under `examples/http_server/` (install `examples/http_server/requirements.txt` for the server).
* Documentation page `docs/transports.md`.

### Changed

* `Worker(..., registry=...)` — third argument is a `TaskHandler` or `HandlerRegistry` (single handler is auto-wrapped).
* `WorkerConfig` — only `no_work_delay_seconds` remains; hooks moved to `HandlerRegistry`.

### Removed

* `WorkerHooks` (alpha breaking change).

## 0.1.2 — 2026-04-14

### Added

* Automated release workflow (`.github/workflows/release.yml`) that triggers on merge to main: extracts version from `pyproject.toml`, creates git tags, builds packages, publishes to PyPI via trusted publishing, and creates GitHub releases.
* Documentation for release process in `docs/releasing.md` with PyPI trusted publishing setup instructions.

### Changed

* Manual publish workflow (`.github/workflows/publish.yml`) updated with `workflow_dispatch` input for dry-run builds.
* README and docs index now reference the release documentation.

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
