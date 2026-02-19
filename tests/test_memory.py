from __future__ import annotations
import pytest
from monolith.memory import MemoryPool, Region
from monolith.errors import MemoryErrorLogical


@pytest.fixture()
def pool() -> MemoryPool:
    return MemoryPool(max_bytes=1024)


class TestAlloc:
    def test_alloc_returns_region(self, pool: MemoryPool) -> None:
        r = pool.alloc("r1", "task-a", 64)
        assert isinstance(r, Region)
        assert r.id == "r1"
        assert r.owner_task_id == "task-a"
        assert r.size == 64
        assert not r.read_only

    def test_alloc_tracks_used_bytes(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 100)
        assert pool.used_bytes == 100
        pool.alloc("r2", "task-a", 200)
        assert pool.used_bytes == 300

    def test_alloc_zero_size_raises(self, pool: MemoryPool) -> None:
        with pytest.raises(MemoryErrorLogical, match="size must be > 0"):
            pool.alloc("r1", "task-a", 0)

    def test_alloc_negative_size_raises(self, pool: MemoryPool) -> None:
        with pytest.raises(MemoryErrorLogical):
            pool.alloc("r1", "task-a", -1)

    def test_alloc_oom_raises(self, pool: MemoryPool) -> None:
        with pytest.raises(MemoryErrorLogical, match="out of logical memory"):
            pool.alloc("r1", "task-a", 2000)

    def test_alloc_duplicate_id_raises(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 64)
        with pytest.raises(MemoryErrorLogical, match="already exists"):
            pool.alloc("r1", "task-b", 32)


class TestFree:
    def test_free_releases_bytes(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 128)
        pool.free("r1", "task-a")
        assert pool.used_bytes == 0
        assert pool.region_count == 0

    def test_free_wrong_owner_raises(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 64)
        with pytest.raises(MemoryErrorLogical, match="owner mismatch"):
            pool.free("r1", "task-b")

    def test_free_unknown_region_raises(self, pool: MemoryPool) -> None:
        with pytest.raises(MemoryErrorLogical, match="unknown region"):
            pool.free("no-such-region", "task-a")


class TestReadWrite:
    def test_write_and_read_roundtrip(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 64)
        pool.write("r1", "task-a", 0, b"hello")
        assert pool.read("r1", 0, 5) == b"hello"

    def test_write_wrong_owner_raises(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 64)
        with pytest.raises(MemoryErrorLogical, match="owner mismatch"):
            pool.write("r1", "task-b", 0, b"x")

    def test_write_read_only_raises(self, pool: MemoryPool) -> None:
        r = pool.alloc("r1", "task-a", 64)
        r.read_only = True
        with pytest.raises(MemoryErrorLogical, match="read-only"):
            pool.write("r1", "task-a", 0, b"x")

    def test_read_out_of_bounds(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 10)
        with pytest.raises(MemoryErrorLogical, match="out-of-bounds"):
            pool.read("r1", 8, 5)  # 8 + 5 > 10

    def test_write_out_of_bounds(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 10)
        with pytest.raises(MemoryErrorLogical, match="out-of-bounds"):
            pool.write("r1", "task-a", 9, b"xx")

    def test_read_unknown_region_raises(self, pool: MemoryPool) -> None:
        with pytest.raises(MemoryErrorLogical, match="unknown region"):
            pool.read("ghost", 0, 1)

    def test_read_zero_length(self, pool: MemoryPool) -> None:
        pool.alloc("r1", "task-a", 8)
        assert pool.read("r1", 0, 0) == b""
