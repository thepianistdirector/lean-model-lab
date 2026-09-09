"""Deterministic offered-arrival replay with fixed lanes and a bounded global queue.

The caller supplies actual monotonic observations and performs dispatched work.
This module has no clock, threads, sleeps, network, or backend. It never expires
in-flight work: completion lateness belongs to the separate SLO evaluator.
"""
from __future__ import annotations

from .contracts import ContractError, validate_workload
from .workloads import MAX_NS, validate_workload_v2


class ReplayError(ValueError):
    """A workload, observation clock, or completion violates replay state."""


def _integer(value: int, minimum: int, maximum: int, name: str) -> None:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ReplayError(f'{name} must be an integer in [{minimum}, {maximum}]')


class LaneReplay:
    """Single-caller state machine for a validated v2 workload.

    Request index modulo concurrency fixes its slot for the whole attempt.
    ``pending_count`` counts only waiting requests, excluding active slots and
    future arrivals. ``next_arrival_ns`` is the next unoffered absolute arrival,
    or None when all arrivals have been offered. ``done`` also requires every
    dispatched request to have completed and the waiting queue to be empty.

    An advance observes all due offers at its supplied time; it does not pretend
    an overdue arrival was observed or dispatched at its earlier frozen time.
    Repeating an observation time is allowed; clock reversal is refused.
    """

    def __init__(self, workload: dict, concurrency: int, service_started_ns: int):
        try:
            validate_workload(workload)
            if workload['schema_version'] not in (2, 3):
                raise ContractError('arrival replay requires schema 2 or 3')
        except ContractError as exc:
            raise ReplayError(f'replay requires a validated v2 workload: {exc}') from exc
        _integer(concurrency, 1, 8, 'concurrency')
        if concurrency not in workload['concurrency_modes']:
            raise ReplayError('concurrency is not admitted by this workload')
        _integer(service_started_ns, 0, MAX_NS, 'service_started_ns')
        # Copy only immutable scheduling values. Caller mutations cannot alter
        # the already-validated population, queue capacity, or deadlines.
        arrivals = tuple(service_started_ns + row['arrival_offset_ns']
                         for row in workload['requests'])
        if any(value > MAX_NS for value in arrivals):
            raise ReplayError('service epoch plus arrival exceeds signed 64-bit nanoseconds')
        deadline = workload['request_deadline_ns']
        deadlines = tuple(value + deadline for value in arrivals) if deadline is not None else None
        if deadlines is not None and any(value > MAX_NS for value in deadlines):
            raise ReplayError('absolute request deadline exceeds signed 64-bit nanoseconds')
        self._concurrency = concurrency
        self._arrivals = arrivals
        self._deadlines = deadlines
        self._capacity = workload['max_queue_requests']
        self._last_ns = service_started_ns
        self._next_index = 0
        self._waiting: list[int] = []
        self._active: list[int | None] = [None] * concurrency

    @property
    def done(self) -> bool:
        return (self._next_index == len(self._arrivals) and
                not self._waiting and not any(index is not None for index in self._active))

    @property
    def pending_count(self) -> int:
        return len(self._waiting)

    @property
    def active_count(self) -> int:
        return sum(index is not None for index in self._active)

    @property
    def next_arrival_ns(self) -> int | None:
        return self._arrivals[self._next_index] if self._next_index < len(self._arrivals) else None

    def _check_clock(self, now_ns: int) -> None:
        _integer(now_ns, 0, MAX_NS, 'now_ns')
        if now_ns < self._last_ns:
            raise ReplayError('observation clock moved backwards')

    def _expired(self, index: int, now_ns: int) -> bool:
        return self._deadlines is not None and now_ns >= self._deadlines[index]

    def _event(self, kind: str, index: int, now_ns: int) -> dict:
        return {'kind': kind, 'index': index, 'slot': index % self._concurrency,
                'observed_ns': now_ns}

    def advance(self, now_ns: int) -> list[dict]:
        """Expire queued deadlines, dispatch free queued lanes, then offer arrivals.

        Queue expiration frees capacity even when its assigned lane stays busy.
        A free target slot dispatches directly and consumes no waiting capacity.
        Due arrivals observed at or beyond their deadline fail before dispatch.
        Busy lanes use drop-tail when the shared waiting capacity is exhausted.
        """
        self._check_clock(now_ns)
        self._last_ns = now_ns
        events = []
        waiting = []
        for index in self._waiting:
            if self._expired(index, now_ns):
                events.append(self._event('deadline', index, now_ns))
            else:
                waiting.append(index)
        self._waiting = []
        for index in waiting:
            slot = index % self._concurrency
            if self._active[slot] is None:
                self._active[slot] = index
                events.append(self._event('dispatch', index, now_ns))
            else:
                self._waiting.append(index)
        while self._next_index < len(self._arrivals) and self._arrivals[self._next_index] <= now_ns:
            index = self._next_index
            self._next_index += 1
            slot = index % self._concurrency
            if self._expired(index, now_ns):
                events.append(self._event('deadline', index, now_ns))
            elif self._active[slot] is None:
                self._active[slot] = index
                events.append(self._event('dispatch', index, now_ns))
            elif len(self._waiting) < self._capacity:
                self._waiting.append(index)
            else:
                events.append(self._event('queue_full', index, now_ns))
        return events

    def complete(self, slot: int, index: int, now_ns: int) -> None:
        """Free exactly the active request; call advance separately to dispatch more.

        Completing beyond the request deadline is accepted. An invalid identity
        or timestamp changes neither state nor the last accepted observation.
        """
        _integer(slot, 0, self._concurrency - 1, 'slot')
        _integer(index, 0, len(self._arrivals) - 1, 'index')
        self._check_clock(now_ns)
        if self._active[slot] != index:
            raise ReplayError('completion does not identify the active request in this slot')
        self._last_ns = now_ns
        self._active[slot] = None
