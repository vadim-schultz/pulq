"""Weighted Deficit Round Robin (WDRR) deficit ledger."""

from __future__ import annotations

from pulq.models.scheduler_config import DeficitSchedulerConfig

__all__ = ["DeficitScheduler", "DeficitSchedulerConfig"]


class DeficitScheduler:
    """Tracks WDRR deficits for fair weighted service among priority buckets.

    Each scheduling epoch credits every priority with its configured weight.
    Work claims debit ``quantum`` from the served priority. Empty priorities are
    zeroed so the scheduler does not stall on idle buckets.
    """

    def __init__(self, config: DeficitSchedulerConfig) -> None:
        self.priority_order = config.priority_order
        self.weights = dict(config.weights)
        self.quantum = config.quantum
        self._balances: dict[str, int] = dict.fromkeys(self.priority_order, 0)

    @property
    def is_epoch_complete(self) -> bool:
        """``True`` when every priority has less than one quantum of budget."""
        return all(b < self.quantum for b in self._balances.values())

    @property
    def claimable_priorities(self) -> tuple[str, ...]:
        """Priorities that can still be served this pass, in configured order."""
        return tuple(p for p in self.priority_order if self._balances[p] >= self.quantum)

    def credit_all(self) -> None:
        """Start a new epoch: add each priority's weight to its balance."""
        for priority, weight in self.weights.items():
            self._balances[priority] += weight

    def debit(self, priority: str) -> None:
        """Consume one quantum from ``priority`` after a successful claim."""
        self._balances[priority] -= self.quantum

    def zero_out(self, priority: str) -> None:
        """Clear balance when no pending work exists for ``priority``."""
        self._balances[priority] = 0
