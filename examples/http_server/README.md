# HTTP queue example

Minimal Litestar server that wraps `PullQueue`, plus a worker and task submitter.

## Setup

From the repo root, install pulq with HTTP extras and this folder’s server deps:

```bash
pip install -e ".[http]"
pip install -r examples/http_server/requirements.txt
```

## Run

Terminal 1 — server:

```bash
python examples/http_server/server.py
```

Terminal 2 — schedule tasks:

```bash
python examples/http_server/task_submitter.py
```

Terminal 3 — worker:

```bash
python examples/http_server/worker_client.py
```

The worker uses `handler_name="echo"` tasks from the submitter. See [Transports](../../docs/transports.md) for design notes and repository options.
