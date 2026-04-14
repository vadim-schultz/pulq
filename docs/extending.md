# Extending PULQ

## Custom `TaskRepository`

Implement {py:class}`pulq.types.TaskRepository` with:

* `schedule(task)` — enqueue a {py:class}`pulq.models.Task` in `PENDING` state.
* `claim_next_pending(priority, worker_id)` — return a claimed `RUNNING` {py:class}`pulq.models.Task`
  or {py:class}`pulq.models.NoPendingTask` for that `priority`.
* `mark_complete(task_id, result)` — persist terminal state; treat `result["ok"] is False` as failure.

Keep claims **atomic** if multiple workers pull concurrently.

## Custom `Transport`

Implement {py:class}`pulq.types.Transport` to serialize `WorkResponse` over HTTP, gRPC, Redis, etc.

* Server decodes JSON → {py:func}`pulq.parse_work_response` (Pydantic validates using discriminated unions).
* Client encodes models with `.model_dump(mode="json")`.

The core {py:class}`pulq.core.pull_queue.PullQueue` stays identical; only the transport changes.

## Management commands

Use {py:class}`pulq.models.CommandType` enums (`STOP`, `PAUSE`, `RESUME`). Per-worker queues live in
{py:class}`pulq.core.dispatcher.CommandDispatcher` (exposed as `PullQueue.commands`).
