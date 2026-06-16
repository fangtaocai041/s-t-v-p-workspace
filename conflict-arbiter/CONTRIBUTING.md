# Contributing

Thanks for your interest!

## Setup

```bash
cd conflict-arbiter
pip install -e .
pip install pytest ruff
```

## Testing

```bash
python -m pytest tests/ -v
ruff check src/
```

To test arbitration rules:
```python
from pathlib import Path
from src.arbiter import ConflictArbiter
a = ConflictArbiter(Path("config/agent.yaml"))
result = a.detect_conflicts("test", [...], region="china")
```

## License

MIT
