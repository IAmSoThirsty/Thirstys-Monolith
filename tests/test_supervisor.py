from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock
from monolith.supervisor import Supervisor
from monolith.config import MonolithConfig


@pytest.fixture()
def cfg() -> MonolithConfig:
    return MonolithConfig(
        num_workers=2,
        quantum_ms=10,
        memory_pool_bytes=1024 * 1024,
        log_level="WARNING",
        metrics_port=0,        # disable metrics server
        ipc_send_timeout=2.0,
    )


class TestSupervisorLifecycle:
    def test_start_and_stop(self, cfg: MonolithConfig) -> None:
        """Supervisor spawns workers and stops cleanly."""
        with patch("monolith.supervisor.HealthServer"):
            with patch("monolith.supervisor.start_metrics_server"):
                sup = Supervisor(config=cfg)
                sup.start()
                assert sup._started
                assert len(sup._workers) == cfg.num_workers
                assert all(p.is_alive() for p in sup._workers)
                sup.stop(timeout=5.0)
                assert not sup._started

    def test_double_start_raises(self, cfg: MonolithConfig) -> None:
        with patch("monolith.supervisor.HealthServer"):
            with patch("monolith.supervisor.start_metrics_server"):
                sup = Supervisor(config=cfg)
                sup.start()
                try:
                    with pytest.raises(RuntimeError, match="already started"):
                        sup.start()
                finally:
                    sup.stop(timeout=5.0)

    def test_context_manager(self, cfg: MonolithConfig) -> None:
        with patch("monolith.supervisor.HealthServer"):
            with patch("monolith.supervisor.start_metrics_server"):
                with Supervisor(config=cfg) as sup:
                    assert sup._started
                assert not sup._started

    def test_submit_before_start_raises(self, cfg: MonolithConfig) -> None:
        sup = Supervisor(config=cfg)
        with pytest.raises(RuntimeError, match="not started"):
            sup.submit_task({"meta": {"owner": "test"}})


class TestTaskSubmitAndCollect:
    def test_submit_and_collect_result(self, cfg: MonolithConfig) -> None:
        """Submit one task and collect a result within 3 seconds."""
        with patch("monolith.supervisor.HealthServer"):
            with patch("monolith.supervisor.start_metrics_server"):
                with Supervisor(config=cfg) as sup:
                    sup.submit_task({"meta": {"owner": "test", "priority": 0}})
                    import time
                    deadline = time.time() + 3.0
                    results = []
                    while time.time() < deadline and not results:
                        results = sup.collect_results(timeout=0.1)
                    assert len(results) == 1
                    assert results[0]["state"] == "DONE"

    def test_collect_returns_empty_when_no_results(self, cfg: MonolithConfig) -> None:
        with patch("monolith.supervisor.HealthServer"):
            with patch("monolith.supervisor.start_metrics_server"):
                with Supervisor(config=cfg) as sup:
                    results = sup.collect_results(timeout=0.05)
                    assert results == []
