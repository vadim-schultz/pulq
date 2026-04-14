# Changelog

## 0.1.0 — 2026-04-13

* Initial release: `PullQueue`, WDRR `DeficitScheduler`, `CommandDispatcher`, `InMemoryTaskRepository`, `LocalTransport`, `Worker`.
* Pydantic models under `pulq.models` (`enums`, `task`, `work`, `unions`, `scheduler_config`) with discriminated unions (`Task`, `ManagementCommand`, `NoWork`, `NoPendingTask`).
* JSON parsing helpers in `pulq.parsing` (`parse_work_response`, `parse_claim_result`).
* Documentation on Read the Docs and GitHub Actions CI.
