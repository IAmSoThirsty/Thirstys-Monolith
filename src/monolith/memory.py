from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from .errors import MemoryErrorLogical


@dataclass
class Region:
    id: str
    owner_task_id: str
    size: int
    read_only: bool = False


class MemoryPool:
    """
    Logical memory pool. Simulation only: all protection is enforced in Python,
    not by the OS / MMU. Suitable for Thirsty-Lang VM and Waterfall DAG tasks.

    Thread-safety: NOT thread-safe. Access must be serialized by the owning
    Scheduler (one scheduler per worker process — no sharing across processes).

    Limits:
      - max_bytes: total logical capacity; configurable via MONOLITH_MEMORY_POOL_BYTES
      - region count: bounded by the number of concurrent tasks (max 8192 per worker)
    """

    def __init__(self, max_bytes: int) -> None:
        self._max_bytes = max_bytes
        self._used_bytes = 0
        self._regions: Dict[str, Region] = {}
        self._storage: Dict[str, bytearray] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def alloc(self, region_id: str, owner_task_id: str, size: int) -> Region:
        """Allocate a new logical memory region.

        Args:
            region_id: Unique region identifier (e.g., task_id + "/stack").
            owner_task_id: Task that owns and can write this region.
            size: Number of bytes to allocate (must be > 0).

        Returns:
            Region descriptor.

        Raises:
            MemoryErrorLogical: on size ≤ 0, OOM, or duplicate region_id.
        """
        if size <= 0:
            raise MemoryErrorLogical("size must be > 0")
        if self._used_bytes + size > self._max_bytes:
            raise MemoryErrorLogical(
                f"out of logical memory: need {size}B, have "
                f"{self._max_bytes - self._used_bytes}B free"
            )
        if region_id in self._regions:
            raise MemoryErrorLogical(f"region {region_id!r} already exists")

        region = Region(id=region_id, owner_task_id=owner_task_id, size=size)
        self._regions[region_id] = region
        self._storage[region_id] = bytearray(size)
        self._used_bytes += size
        return region

    def free(self, region_id: str, requester_task_id: str) -> None:
        """Free a logical memory region.

        Raises:
            MemoryErrorLogical: if region doesn't exist or requester is not the owner.
        """
        region = self._require_region(region_id)
        self._ensure_owner(region, requester_task_id)
        self._used_bytes -= region.size
        del self._regions[region_id]
        del self._storage[region_id]

    def read(self, region_id: str, offset: int, length: int) -> bytes:
        """Read bytes from a region (no ownership check — all tasks may read).

        Raises:
            MemoryErrorLogical: if region doesn't exist or access is out of bounds.
        """
        region = self._require_region(region_id)
        self._ensure_bounds(region, offset, length)
        buf = self._storage[region_id]
        return bytes(buf[offset : offset + length])

    def write(
        self,
        region_id: str,
        requester_task_id: str,
        offset: int,
        data: bytes,
    ) -> None:
        """Write bytes into a region.

        Raises:
            MemoryErrorLogical: if region doesn't exist, is read-only, requester
            is not the owner, or access is out of bounds.
        """
        region = self._require_region(region_id)
        if region.read_only:
            raise MemoryErrorLogical(f"region {region_id!r} is read-only")
        self._ensure_owner(region, requester_task_id)
        self._ensure_bounds(region, offset, len(data))
        buf = self._storage[region_id]
        buf[offset : offset + len(data)] = data

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def used_bytes(self) -> int:
        return self._used_bytes

    @property
    def free_bytes(self) -> int:
        return self._max_bytes - self._used_bytes

    @property
    def region_count(self) -> int:
        return len(self._regions)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _require_region(self, region_id: str) -> Region:
        try:
            return self._regions[region_id]
        except KeyError as exc:
            raise MemoryErrorLogical(f"unknown region {region_id!r}") from exc

    @staticmethod
    def _ensure_bounds(region: Region, offset: int, length: int) -> None:
        if offset < 0 or length < 0 or offset + length > region.size:
            raise MemoryErrorLogical(
                f"out-of-bounds access: offset={offset} length={length} "
                f"region_size={region.size}"
            )

    @staticmethod
    def _ensure_owner(region: Region, requester_task_id: str) -> None:
        if region.owner_task_id != requester_task_id:
            raise MemoryErrorLogical(
                f"owner mismatch: region owned by {region.owner_task_id!r}, "
                f"requested by {requester_task_id!r}"
            )
