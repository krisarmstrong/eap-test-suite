"""Automation sessions for eap-test-suite."""

from __future__ import annotations

import nox

nox.options.sessions = ["tests"]


@nox.session
def tests(session: nox.Session) -> None:
    """Run the test suite under the active interpreter."""
    session.install("-e", ".")
    session.install("pytest", "pytest-cov")
    session.run("pytest", "--cov=eap_test_suite", "--cov-report=term-missing")
