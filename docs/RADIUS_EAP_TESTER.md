# EAPTestor v4.1

## Overview
EAPTestor v4.1 is a Python-based framework for testing Extensible Authentication Protocol (EAP) methods with FreeRADIUS. It uses a single JSON configuration file, supports parallel test execution, and includes advanced features like dry runs and result exporting.

### EAP Methods Supported:
1. **EAP-TLS** - Certificate-based authentication
2. **EAP-TTLS** - Tunneled Transport Layer Security
3. **PEAP** - Protected EAP with MSCHAPv2
4. **EAP-MD5** - Challenge-based EAP
5. **EAP-FAST** - Secure, fast authentication without certificates

## Installation and Setup

### Prerequisites
- Python 3.8+
- FreeRADIUS v3.2.3 or higher
- OpenSSL libraries
- `eapol_test` binary (part of wpa_supplicant)
- Dependencies: `jsonschema`, `tqdm` (install via `pip install -r requirements.txt`)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd eaptestor
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the package:
   ```bash
   python setup.py install
   ```
4. Generate a template configuration:
   ```bash
   eaptestor --generate-config
   ```
5. Update `conf/config.json` with your FreeRADIUS server details and EAP settings.

### Running the EAP Tests
Run all tests sequentially:
```bash
eaptestor
```
Run tests in parallel:
```bash
eaptestor --parallel
```
Perform a dry run:
```bash
eaptestor --dry-run
```
Enable verbose logging:
```bash
eaptestor --verbose
```
Specify a custom config file:
```bash
eaptestor --config path/to/config.json
```

### Testing
Run unit tests:
```bash
python -m unittest discover tests
```

### Configuration
All settings are stored in `conf/config.json`. Update the `server` section with FreeRADIUS details and the `eap_methods` section with EAP-specific configurations (e.g., certificate paths, PAC files). Sensitive settings can be set via environment variables (e.g., `EAPTESTOR_SECRETKEY`).

## Changelog
See `CHANGELOG.md` for detailed version history.

## License
MIT License (see `LICENSE` file).