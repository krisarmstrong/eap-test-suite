# Architecture

## Overview

EAP Test Suite is a Python 3.14+ automated testing framework for EAP (Extensible Authentication Protocol) authentication methods. It integrates with FreeRADIUS servers using the eapol_test tool from Hostapd.

## System Design

### Core Components

1. **CLI Module** (`cli.py`)
   - Command-line argument parsing
   - Test orchestration
   - Output formatting and reporting

2. **Dependency Manager**
   - System package detection
   - Cross-platform package installation (apt, dnf, pacman, brew)
   - eapol_test compilation from source

3. **Test Runner**
   - JSON configuration parsing
   - RADIUS server connectivity checks
   - EAP test execution
   - Result collection and analysis

4. **Configuration System**
   - JSON-based configuration (`config/config.json`)
   - EAP type definitions
   - RADIUS server settings
   - Authentication credentials

### Data Flow

```
Configuration File (JSON)
    ↓
Dependency Check & Installation
    ↓
eapol_test Build (if needed)
    ↓
RADIUS Server Reachability Test
    ↓
EAP Test Execution (per type)
    ↓
Log Collection & Rotation
    ↓
Test Results Report
```

## Module Dependencies

### External Tools
- **eapol_test**: Hostapd's EAP testing utility
- **jq**: JSON processing
- **wpa_supplicant**: WPA functionality
- **FreeRADIUS**: RADIUS server

### External Libraries
- **subprocess**: Process execution (Python stdlib)
- **json**: Configuration parsing (Python stdlib)
- **pathlib**: Path handling (Python stdlib)
- **logging**: Test logging (Python stdlib)

### Internal Modules
- **src/eap_test_suite/cli.py**: Main CLI implementation

## EAP Test Types

Supported EAP methods:
- PEAP (Protected EAP)
- TLS (Transport Layer Security)
- TTLS (Tunneled TLS)
- FAST (Flexible Authentication via Secure Tunneling)
- MD5 (Message Digest 5)
- MSCHAPV2 (Microsoft Challenge-Handshake Authentication Protocol v2)

## Build System

1. **Dependency Detection**: Checks for system packages
2. **Package Installation**: Uses platform-appropriate package manager
3. **Source Download**: Clones Hostapd repository if needed
4. **Compilation**: Builds eapol_test from source
5. **Verification**: Tests eapol_test functionality

## Logging System

- **Log Directory**: `logs/`
- **Log Rotation**: Automatic rotation to prevent disk fill
- **Debug Mode**: Detailed verbose logging
- **Per-Test Logs**: Separate logs for each EAP type

## Error Handling

- Dependency installation failures
- RADIUS server unreachable
- eapol_test compilation errors
- Authentication failures
- Invalid configuration

---

Author: Kris Armstrong
