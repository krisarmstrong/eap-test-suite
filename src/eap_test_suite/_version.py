from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path


def _find_pyproject(start: Path) -> Path | None:
    for parent in (start, *start.parents):
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def _read_pyproject_version() -> str:
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        return "0.0.0"

    pyproject = _find_pyproject(Path(__file__).resolve())
    if not pyproject:
        return "0.0.0"
    try:
        data = tomllib.loads(pyproject.read_text())
    except Exception:
        return "0.0.0"
    return data.get("project", {}).get("version", "0.0.0")


_pyproject_version = _read_pyproject_version()
if _pyproject_version != "0.0.0":
    version = _pyproject_version
else:
    try:
        version = _pkg_version("eap-test-suite")
    except PackageNotFoundError:
        version = "0.0.0"
