# API Reference

## Command-Line Interface

### eap-test-suite

Run EAP authentication tests against RADIUS server.

**Syntax:**
```bash
eap-test-suite [OPTIONS]
```

**Options:**
- `--eap <type>`: Test specific EAP type (PEAP, TLS, TTLS, etc.)
- `--debug`: Enable debug logging
- `--config <file>`: Use custom config file (default: `config/config.json`)
- `--help`: Show help message

**Examples:**
```bash
# Test all EAP types
eap-test-suite

# Test specific type
eap-test-suite --eap PEAP

# Debug mode
eap-test-suite --debug

# Custom config
eap-test-suite --config /path/to/config.json

# Combine options
eap-test-suite --eap TLS --debug
```

**Exit Codes:**
- `0`: All tests passed
- `1`: One or more tests failed
- `2`: Configuration error
- `3`: Dependency error

---

## Configuration Format

### config/config.json

```json
{
  "radius": {
    "server": "192.168.1.1",
    "port": 1812,
    "secret": "shared_secret"
  },
  "eap_types": {
    "PEAP": {
      "enabled": true,
      "username": "user@example.com",
      "password": "password"
    },
    "TLS": {
      "enabled": true,
      "cert": "/path/to/cert.pem",
      "key": "/path/to/key.pem"
    }
  }
}
```

---

## Module: eap_test_suite.cli

### Functions

#### `main() -> int`

Main entry point for CLI.

**Returns:**
- int: Exit code (0 for success)

**Example:**
```python
from eap_test_suite.cli import main

exit_code = main()
```

---

## Test Output

### Success Example

```
[INFO] Testing EAP-PEAP
[INFO] RADIUS server reachable: 192.168.1.1:1812
[INFO] Running eapol_test for PEAP
[SUCCESS] EAP-PEAP authentication succeeded
[INFO] Test duration: 2.5s
```

### Failure Example

```
[INFO] Testing EAP-PEAP
[ERROR] RADIUS server unreachable: 192.168.1.1:1812
[FAIL] EAP-PEAP authentication failed
[ERROR] Error: Connection timeout
```

---

## Dependency Management

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install jq wpa-supplicant git make gcc libssl-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install jq wpa_supplicant git make gcc openssl-devel
```

**Arch Linux:**
```bash
sudo pacman -S jq wpa_supplicant git make gcc openssl
```

**macOS:**
```bash
brew install jq wpa_supplicant git make openssl
```

---

## Log Files

### Log Locations

- `logs/eap_test_suite.log`: Main application log
- `logs/eapol_test_<type>.log`: Per-EAP-type test logs
- `logs/build.log`: eapol_test compilation log

### Log Format

```
2025-11-03 10:30:45 [INFO] Starting EAP test suite
2025-11-03 10:30:46 [INFO] Testing PEAP
2025-11-03 10:30:48 [SUCCESS] PEAP authentication succeeded
```

---

## Building eapol_test

The suite automatically builds eapol_test if not found:

```bash
# Manual build
cd hostap/wpa_supplicant
cp defconfig .config
make eapol_test
```

---

Author: Kris Armstrong
