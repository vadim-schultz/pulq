"""HttpTransport with mocked httpx."""

from __future__ import annotations

import json

import httpx
import pytest

from pulq import CommandType, HttpTransport, NoWork, NoWorkReason, Task
from pulq.errors import TransportHttpError


def _mocked_transport(mock: httpx.MockTransport) -> HttpTransport:
    return HttpTransport(base_url="http://example", httpx_args={"transport": mock})


@pytest.mark.asyncio
async def test_request_work_returns_task() -> None:
    task = Task(priority="high", handler_name="h", payload={"n": 1})
    task_json = task.model_dump(mode="json")

    def handle(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/api/queue/request_work":
            body = json.loads(request.content.decode())
            assert body["worker_id"] == "w1"
            return httpx.Response(200, json=task_json)
        return httpx.Response(500)

    async with _mocked_transport(httpx.MockTransport(handle)) as t:
        work = await t.request_work("w1")
    assert isinstance(work, Task)
    assert work.handler_name == "h"


@pytest.mark.asyncio
async def test_request_work_returns_no_work() -> None:
    nw = NoWork(reason=NoWorkReason.QUEUE_EMPTY).model_dump(mode="json")

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/queue/request_work":
            return httpx.Response(200, json=nw)
        return httpx.Response(500)

    async with _mocked_transport(httpx.MockTransport(handle)) as t:
        work = await t.request_work("w1")
    assert isinstance(work, NoWork)


@pytest.mark.asyncio
async def test_report_completion_posts_json() -> None:
    captured: dict[str, object] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/api/queue/complete":
            captured["body"] = json.loads(request.content.decode())
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(500)

    async with _mocked_transport(httpx.MockTransport(handle)) as t:
        await t.report_completion("tid-1", {"ok": True, "x": 1})

    assert captured["body"] == {"task_id": "tid-1", "result": {"ok": True, "x": 1}}


@pytest.mark.asyncio
async def test_send_command_posts_json() -> None:
    captured: dict[str, object] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/api/queue/send_command":
            captured["body"] = json.loads(request.content.decode())
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(500)

    async with _mocked_transport(httpx.MockTransport(handle)) as t:
        await t.send_command("w1", CommandType.STOP)

    assert captured["body"] == {"worker_id": "w1", "command": "stop"}


@pytest.mark.asyncio
async def test_request_work_raises_on_http_error() -> None:
    def handle(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    async with _mocked_transport(httpx.MockTransport(handle)) as t:
        with pytest.raises(TransportHttpError) as excinfo:
            await t.request_work("w1")
        assert excinfo.value.status_code == 500


@pytest.mark.asyncio
async def test_lazy_opens_client_on_first_request() -> None:
    task_json = Task(priority="low", handler_name="x", payload={}).model_dump(mode="json")

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/queue/request_work":
            return httpx.Response(200, json=task_json)
        return httpx.Response(404)

    async with _mocked_transport(httpx.MockTransport(handle)) as t:
        work = await t.request_work("w1")
    assert isinstance(work, Task)


@pytest.mark.asyncio
async def test_empty_base_url_raises_when_opening_client() -> None:
    t = HttpTransport(base_url="")
    with pytest.raises(ValueError, match="base_url"):
        await t.setup_transport()
