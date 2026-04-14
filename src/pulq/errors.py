"""Exceptions raised by pulq."""


class PulqError(Exception):
    """Base class for pulq errors."""


class TaskNotFoundError(PulqError):
    """Raised when a task id does not exist in storage."""
