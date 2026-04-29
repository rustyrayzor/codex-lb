from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from app.core.clients.proxy import ProxyResponseError
from app.core.resilience.overload import local_overload_error
from app.core.utils.request_id import get_request_id

logger = logging.getLogger(__name__)

_DEFAULT_ADMISSION_WAIT_TIMEOUT_SECONDS = 10.0


@dataclass(slots=True)
class AdmissionLease:
    _semaphore: asyncio.Semaphore | None
    _released: bool = False

    def release(self) -> None:
        if self._released or self._semaphore is None:
            return
        self._released = True
        self._semaphore.release()

    def __enter__(self) -> AdmissionLease:
        return self

    def __exit__(self, *args: object) -> None:
        self.release()

    def __del__(self) -> None:
        if self._released or self._semaphore is None:
            return
        self._released = True
        self._semaphore.release()
        logger.warning("AdmissionLease was garbage-collected without release() — this indicates a bug in the caller")


@dataclass(slots=True)
class AdmissionLeaseGroup:
    _leases: list[AdmissionLease]
    _released: bool = False

    def release(self) -> None:
        if self._released:
            return
        self._released = True
        for lease in reversed(self._leases):
            lease.release()

    def __enter__(self) -> AdmissionLeaseGroup:
        return self

    def __exit__(self, *args: object) -> None:
        self.release()


@dataclass(slots=True)
class _AdmissionGate:
    semaphore: asyncio.Semaphore
    wait_timeout_seconds: float


class WorkAdmissionController:
    def __init__(
        self,
        *,
        token_refresh_limit: int,
        websocket_connect_limit: int,
        response_create_limit: int,
        compact_response_create_limit: int,
        image_global_in_flight: int = 0,
        image_per_account_in_flight: int = 0,
        admission_wait_timeout_seconds: float = _DEFAULT_ADMISSION_WAIT_TIMEOUT_SECONDS,
    ) -> None:
        self._token_refresh = _make_gate(token_refresh_limit, admission_wait_timeout_seconds)
        self._websocket_connect = _make_gate(websocket_connect_limit, admission_wait_timeout_seconds)
        self._response_create = _make_gate(response_create_limit, admission_wait_timeout_seconds)
        self._compact_response_create = _make_gate(compact_response_create_limit, admission_wait_timeout_seconds)
        self._image_global = _make_gate(image_global_in_flight, admission_wait_timeout_seconds)
        self._image_per_account_limit = image_per_account_in_flight
        self._image_wait_timeout_seconds = admission_wait_timeout_seconds
        self._image_account_gates: dict[str, _AdmissionGate] = {}
        self._image_account_gates_lock = asyncio.Lock()

    async def acquire_token_refresh(self) -> AdmissionLease:
        return await self._acquire(self._token_refresh, stage="token_refresh")

    async def acquire_websocket_connect(self) -> AdmissionLease:
        return await self._acquire(self._websocket_connect, stage="upstream_websocket_connect")

    async def acquire_response_create(self, *, compact: bool = False) -> AdmissionLease:
        semaphore = self._compact_response_create if compact else self._response_create
        stage = "compact_response_create" if compact else "response_create"
        return await self._acquire(semaphore, stage=stage)

    async def acquire_image_generation(self, account_id: str) -> AdmissionLease | AdmissionLeaseGroup:
        global_lease = await self._acquire(self._image_global, stage="image_generation_global")
        try:
            account_gate = await self._image_account_gate(account_id)
            account_lease = await self._acquire(account_gate, stage="image_generation_account")
        except Exception:
            global_lease.release()
            raise
        return AdmissionLeaseGroup([global_lease, account_lease])

    async def _image_account_gate(self, account_id: str) -> _AdmissionGate | None:
        if self._image_per_account_limit <= 0:
            return None
        async with self._image_account_gates_lock:
            gate = self._image_account_gates.get(account_id)
            if gate is None:
                gate = _make_gate(self._image_per_account_limit, self._image_wait_timeout_seconds)
                assert gate is not None
                self._image_account_gates[account_id] = gate
            return gate

    async def _acquire(self, gate: _AdmissionGate | None, *, stage: str) -> AdmissionLease:
        if gate is None:
            return AdmissionLease(None)
        try:
            await asyncio.wait_for(gate.semaphore.acquire(), timeout=gate.wait_timeout_seconds)
        except asyncio.TimeoutError:
            available = gate.semaphore._value  # noqa: SLF001
            message = f"codex-lb is temporarily overloaded during {stage}"
            logger.warning(
                "proxy_admission_rejected request_id=%s stage=%s status=429 available=%s "
                "wait_timeout_seconds=%.1f message=%s",
                get_request_id(),
                stage,
                available,
                gate.wait_timeout_seconds,
                message,
            )
            raise ProxyResponseError(429, local_overload_error(message))
        return AdmissionLease(gate.semaphore)


def _make_gate(limit: int, wait_timeout_seconds: float) -> _AdmissionGate | None:
    if limit <= 0:
        return None
    return _AdmissionGate(
        semaphore=asyncio.Semaphore(limit),
        wait_timeout_seconds=wait_timeout_seconds,
    )
