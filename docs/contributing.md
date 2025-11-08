# Contributing Guide

## Quick Start

```bash
git clone <repository-url>
cd eap_test_suite
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Development Workflow

1. **Branch**: `git checkout -b feature/your-feature`
2. **Code**: Follow PEP 8, add type hints
3. **Test**: `pytest -v`
4. **Lint**: `pre-commit run --all-files`
5. **Commit**: `git commit -m "feat: description"`
6. **Push**: `git push origin feature/your-feature`
7. **PR**: Open pull request

## Code Standards

- Python 3.14+
- PEP 8 compliant
- Type hints required
- Comprehensive error handling
- Logging for all major operations

## Testing

```bash
# Unit tests
pytest -v

# Smoke test
bash scripts/smoke.sh

# With coverage
pytest --cov=eap_test_suite
```

## Adding EAP Types

1. Add configuration to `config/config.json`
2. Implement test logic in CLI
3. Add test case
4. Update documentation

---

Author: Kris Armstrong
