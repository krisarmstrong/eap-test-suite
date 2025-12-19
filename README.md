# EAP Test Suite (Python 3)
[![Checks](https://github.com/krisarmstrong/eap-test-suite/actions/workflows/checks.yml/badge.svg)](https://github.com/krisarmstrong/eap-test-suite/actions/workflows/checks.yml)


[![CI](https://github.com/krisarmstrong/eap-test-suite/workflows/CI/badge.svg)](https://github.com/krisarmstrong/eap-test-suite/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Automated testing suite for EAP (Extensible Authentication Protocol) authentication methods.

## Description

EAP Test Suite automates the testing of various EAP authentication methods supported by FreeRADIUS using the eapol_test tool from Hostapd. It detects system dependencies, builds required tools, and executes comprehensive authentication tests against RADIUS servers.

This project is the modern successor to `freeradius-eapol-test-tool` (legacy bash implementation), providing a complete Python rewrite with enhanced features, better error handling, and cross-platform support.

## Features

- Automatic dependency detection and installation
- Cross-platform package manager support (apt, dnf, pacman, brew)
- Automated eapol_test compilation from source
- JSON-based configuration management
- Multiple EAP type testing (PEAP, TLS, TTLS, etc.)
- Log rotation and detailed logging
- RADIUS server reachability checks
- Debug mode support

## Requirements

- Python 3.14+ (tested with 3.14.0)
- FreeRADIUS server configured
- System dependencies: jq, wpa_supplicant, git, make, gcc, libssl-dev
- Network access to the target RADIUS server

## Installation

```bash
git clone <repository-url>
cd eap_test_suite_py3
python3.14 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

The script will automatically build eapol_test and install required dependencies on first run.

### macOS Installation

For detailed macOS-specific installation instructions, see [docs/INSTALL_MACOS.md](docs/INSTALL_MACOS.md).

## Usage

Test all configured EAP types:
```bash
python3 -m eap_test_suite.cli
```

Test specific EAP type:
```bash
python3 -m eap_test_suite.cli --eap PEAP
```

Enable debug logging:
```bash
python3 -m eap_test_suite.cli --debug
```

Once installed via `pip`, you can also use the console entry point:
```bash
eap-test-suite --help
```

## Development
Run the full local checks:

```bash
./check.sh
```


- Run linting and formatting: `pre-commit run --all-files`
- Run the automated test suite: `pytest`
- Execute the repository smoke test: `bash scripts/smoke.sh`

## Configuration

Edit `config/config.json` to configure:
- RADIUS server address, port, and shared secret
- EAP types to test
- Authentication credentials

## Project Structure

- `src/eap_test_suite/` - Python package containing the CLI implementation
- `config/` - Configuration files for RADIUS and EAP types
- `logs/` - Test execution logs
- `hostap/` - Hostapd source code (auto-downloaded)

## License

This project is licensed under the MIT License. See LICENSE file for details.

## RADIUS EAP Testing

This suite now includes comprehensive RADIUS EAP testing capabilities (merged from radius-eap-tester).

### RADIUS Testing Features
- RADIUS server authentication testing
- Multiple EAP method support
- RADIUS attribute validation
- Server response analysis

See `docs/RADIUS_EAP_TESTER.md` for detailed RADIUS testing documentation.

