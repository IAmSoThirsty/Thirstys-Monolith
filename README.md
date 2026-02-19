# Thirstys-Monolith

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE.txt)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black?style=flat-square\&logo=github)](https://github.com/IAmSoThirsty/Thirstys-Monolith/actions)

**Sovereign Stack multi-process runtime.** `monolith` is the execution kernel that ingests Thirsty-Lang task payloads, schedules them across isolated worker processes, enforces logical memory ownership, and exposes Prometheus metrics + Kubernetes health probes.

---

## Architecture

```
Supervisor (main process)
├─ multiprocessing.Queue  ──[TASK_SUBMIT]──►  Worker-0 ──► Scheduler ──► MemoryPool
├─ multiprocessing.Queue  ──[TASK_SUBMIT]──►  Worker-1 ──► Scheduler ──► MemoryPool
│                                                  │
│  ◄────────────────[TASK_RESULT]─────────────────┘
├─ HealthServer  :8080  /healthz /readyz
└─ MetricsServer :9100  /metrics  (Prometheus)
```

- **Zero runtime dependencies** — pure Python stdlib.
- **Process model:** `spawn` context; no fork-safety hazards.
- **Cooperative scheduling:** highest-`priority` task runs first; deadline expiry → `CANCELLED`; quantum overruns are tracked as metrics.
- **Memory isolation:** `MemoryPool` enforces owner, bounds, and read-only constraints in Python-space (simulation layer for Thirsty-Lang VM).

---

## Quick Start

```bash
pip install -e ".[dev]"   # dev extras: pytest, ruff, mypy, black, …
pytest -q                 # run all 40+ tests
```

```python
from monolith import Supervisor, load_config

with Supervisor(load_config()) as sup:
    sup.submit_task({
        "meta": {"owner": "demo-tenant", "priority": 10},
        "agent": "retriever",
        "input": {"query": "hello"},
    })
    results = sup.collect_results(timeout=2.0)
    print(results)
    # [{'id': '...', 'owner': 'demo-tenant', 'state': 'DONE', 'last_error': None}]
```

### Full Thirsty-Lang Pipeline

```python
from thirsty_lang import parse_yaml, validate_and_normalize, ir_to_monolith_tasks
from monolith import Supervisor, load_config

ir = validate_and_normalize(parse_yaml(open("flow.tl.yaml").read()))
with Supervisor(load_config()) as sup:
    for payload in ir_to_monolith_tasks(ir):
        sup.submit_task(payload)
    results = sup.collect_results()
```

---

## Package Structure

```
src/monolith/
  __init__.py    # public API surface
  models.py      # TaskState, TaskMetadata, Task
  errors.py      # MonolithError, TaskExecutionError, MemoryErrorLogical, IPCError
  config.py      # MonolithConfig (env-driven)
  memory.py      # MemoryPool — logical isolation per task
  ipc.py         # MessageType, Message, send(), recv()
  logging.py     # NDJSON structured logging
  metrics.py     # Prometheus Counter/Gauge + /metrics HTTP thread
  health.py      # /healthz + /readyz HTTP for k8s probes
  scheduler.py   # Priority scheduler with deadline enforcement
  worker.py      # worker_main() — per-process event loop
  supervisor.py  # Supervisor — spawn pool, lifecycle, collect_results
```

---

## Configuration

All settings are read from environment variables at process start.

| Variable | Default | Description |
|---|---|---|
| `MONOLITH_NUM_WORKERS` | `4` | Number of worker processes to spawn |
| `MONOLITH_QUANTUM_MS` | `10` | Cooperative scheduling quantum (ms) |
| `MONOLITH_MEMORY_POOL_BYTES` | `67108864` | Logical memory per worker (64 MiB) |
| `MONOLITH_LOG_LEVEL` | `INFO` | Python logging level |
| `MONOLITH_METRICS_PORT` | `9100` | Prometheus `/metrics` port (0 = off) |
| `MONOLITH_HEALTH_PORT` | `8080` | Health probe port (0 = off) |
| `MONOLITH_IPC_SEND_TIMEOUT` | `5.0` | Seconds before `IPCError` on send |

---

## Development

```bash
# Install dev extras
pip install -e ".[dev]"

# Run tests
pytest -q

# Lint
ruff check src/ tests/

# Type-check
mypy src/monolith/

# Audit dependencies
pip-audit
```

---

## License

MIT © Thirstys-Hub
