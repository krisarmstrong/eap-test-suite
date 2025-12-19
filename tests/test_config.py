"""Unit tests for the EAP test suite helpers."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from eap_test_suite import cli as eap_auth_test


@pytest.fixture
def config_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Prepare an isolated configuration directory for tests."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    monkeypatch.setattr(eap_auth_test, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(eap_auth_test, "CONFIG_FILE", config_file)
    return config_dir


def write_config(config_dir: Path, data: dict) -> Path:
    config_file = config_dir / "config.json"
    config_file.write_text(json.dumps(data), encoding="utf-8")
    return config_file


def minimal_config() -> dict:
    return {
        "radius": {"server": "127.0.0.1", "port": 1812, "secret": "shared"},
        "eap_types": {
            "eap_md5": {
                "method": "MD5",
                "identity": "alice",
                "password": "wonderland",
            }
        },
    }


def test_load_config_success(config_workspace: Path) -> None:
    write_config(config_workspace, minimal_config())

    config = eap_auth_test.load_config()

    assert config.radius.server == "127.0.0.1"
    assert "eap_md5" in config.eap_types
    assert config.eap_types["eap_md5"].settings["password"] == "wonderland"
    assert config.eap_types["eap_md5"].conf_path == config_workspace / "eap_md5.conf"


def test_load_config_invalid_triggers_exit(config_workspace: Path) -> None:
    invalid = minimal_config()
    invalid["radius"].pop("secret")
    write_config(config_workspace, invalid)

    with pytest.raises(SystemExit):
        eap_auth_test.load_config()


def test_execute_eapol_test_requires_conf_file(
    config_workspace: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("ERROR")
    write_config(config_workspace, minimal_config())

    config = eap_auth_test.load_config()

    eap_auth_test.execute_eapol_test(config, "eap_md5")

    assert "Configuration file" in caplog.text


def test_execute_eapol_test_runs_when_conf_present(
    config_workspace: Path, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    caplog.set_level("INFO")
    write_config(config_workspace, minimal_config())
    (config_workspace / "eap_md5.conf").write_text("network=0", encoding="utf-8")

    config = eap_auth_test.load_config()

    calls = {}

    def fake_run(command, **kwargs):
        calls["command"] = command
        assert kwargs.get("capture_output") is True
        assert kwargs.get("text") is True
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(eap_auth_test.subprocess, "run", fake_run)

    eap_auth_test.execute_eapol_test(config, "eap_md5")

    assert calls["command"][0] == str(eap_auth_test.EAPOL_TEST_PATH)
    assert any("test passed" in message.message for message in caplog.records)
