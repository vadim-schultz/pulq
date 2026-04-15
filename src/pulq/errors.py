"""Exceptions raised by pulq."""


class PulqError(Exception):
    """Base class for pulq errors."""


class TaskNotFoundError(PulqError):
    """Raised when a task id does not exist in storage."""


class TransportHttpError(PulqError):
    """Raised when a remote transport HTTP call fails."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
