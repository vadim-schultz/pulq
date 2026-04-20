"""HTTP(S) transport: worker pulls work from a remote queue API."""

from __future__ import annotations

import os
import ssl
from dataclasses import dataclass, field
from types import ModuleType, TracebackType
from typing import Any, Self

import httpx

from pulq.errors import TransportHttpError
from pulq.models.capabilities import DEFAULT_WORKER_CONTEXT, WorkerContext
from pulq.models.enums import CommandType
from pulq.models.http import ReportCompletionRequest, RequestWorkRequest, SendCommandRequest
from pulq.models.task import Task
from pulq.models.work import ManagementCommand, NoWork
from pulq.parsing import parse_work_response

_truststore: ModuleType | None
try:
    import truststore as _truststore_import

    _truststore = _truststore_import
except ImportError:
    _truststore = None

__all__ = ["HttpTransport"]


class _TruststoreState:
    """One-time truststore injection (avoids module-level ``global``)."""

    injected: bool = False


def _ensure_truststore_injected() -> None:
    if _TruststoreState.injected or _truststore is None:
        return
    _truststore.inject_into_ssl()
    _TruststoreState.injected = True


def _resolve_verify_ssl(verify_ssl: str | bool | ssl.SSLContext) -> str | bool | ssl.SSLContext:
    if verify_ssl is not True:
        return verify_ssl
    ca_bundle = os.getenv("PULQ_CA_BUNDLE")
    if ca_bundle:
        return ssl.create_default_context(cafile=ca_bundle)
    _ensure_truststore_injected()
    return True


@dataclass(kw_only=True)
class HttpTransport:
    """Minimal HTTP adapter for the queue worker wire protocol.

    ``base_url`` must be non-empty before any HTTP call. :meth:`setup_transport`
    (called by :class:`~pulq.core.worker.Worker`) opens the internal
    :class:`~httpx.AsyncClient`; :meth:`teardown_transport` closes it.

    You may still use ``async with`` for standalone use; it delegates to
    ``setup_transport`` / ``teardown_transport``.
    """

    base_url: str
    request_work_path: str = "/api/queue/request_work"
    report_completion_path: str = "/api/queue/complete"
    send_command_path: str = "/api/queue/send_command"
    headers: dict[str, str] = field(default_factory=dict)
    timeout: httpx.Timeout | None = None
    verify_ssl: str | bool | ssl.SSLContext = True
    follow_redirects: bool = False
    httpx_args: dict[str, Any] = field(default_factory=dict)
    _async_client: httpx.AsyncClient | None = field(init=False, default=None, repr=False)
    _owns_client: bool = field(init=False, default=False, repr=False)

    @property
    def _http(self) -> httpx.AsyncClient:
        """Lazily constructed client for queue HTTP calls."""
        if self._async_client is None:
            if not self.base_url:
                msg = "HttpTransport requires a non-empty base_url"
                raise ValueError(msg)
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
                verify=_resolve_verify_ssl(self.verify_ssl),
                follow_redirects=self.follow_redirects,
                **self.httpx_args,
            )
            self._owns_client = True
        return self._async_client

    async def aclose(self) -> None:
        """Close the internal client (alias for :meth:`teardown_transport`)."""
        await self.teardown_transport()

    async def setup_transport(self) -> None:
        """Open the HTTP client so requests can run (idempotent)."""
        _ = self._http

    async def teardown_transport(self) -> None:
        """Close the HTTP client opened by this transport (idempotent)."""
        if self._owns_client and self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
            self._owns_client = False

    async def __aenter__(self) -> Self:
        await self.setup_transport()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.teardown_transport()

    async def request_work(
        self,
        worker_id: str,
        *,
        worker_context: WorkerContext = DEFAULT_WORKER_CONTEXT,
    ) -> Task | ManagementCommand | NoWork:
        """POST ``request_work_path`` with ``worker_id``; response body is a work union."""
        payload = RequestWorkRequest(
            worker_id=worker_id,
            worker_context=worker_context,
        ).model_dump(mode="json")
        try:
            response = await self._http.post(self.request_work_path, json=payload)
        except httpx.RequestError as exc:
            msg = f"request_work failed: {exc}"
            raise TransportHttpError(msg) from exc
        if response.is_error:
            detail = f"request_work HTTP {response.status_code}: {response.text}"
            raise TransportHttpError(detail, status_code=response.status_code)
        return parse_work_response(response.json())

    async def report_completion(self, task_id: str, result: dict[str, Any]) -> None:
        """POST ``report_completion_path`` with ``task_id`` and ``result``."""
        payload = ReportCompletionRequest(task_id=task_id, result=result).model_dump(mode="json")
        try:
            response = await self._http.post(self.report_completion_path, json=payload)
        except httpx.RequestError as exc:
            msg = f"report_completion failed: {exc}"
            raise TransportHttpError(msg) from exc
        if response.is_error:
            detail = f"report_completion HTTP {response.status_code}: {response.text}"
            raise TransportHttpError(detail, status_code=response.status_code)

    async def send_command(self, worker_id: str, command: CommandType) -> None:
        """POST ``send_command_path`` (matches the example queue server)."""
        payload = SendCommandRequest(worker_id=worker_id, command=command).model_dump(mode="json")
        try:
            response = await self._http.post(self.send_command_path, json=payload)
        except httpx.RequestError as exc:
            msg = f"send_command failed: {exc}"
            raise TransportHttpError(msg) from exc
        if response.is_error:
            detail = f"send_command HTTP {response.status_code}: {response.text}"
            raise TransportHttpError(detail, status_code=response.status_code)
