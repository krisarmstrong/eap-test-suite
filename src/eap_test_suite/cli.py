"""
EAP Authentication Test Script

This script automates testing of various EAP (Extensible Authentication Protocol) authentication methods
supported by FreeRADIUS using the `eapol_test` tool from Hostapd. It ensures that all necessary dependencies
are installed, builds `eapol_test` if it is not already present, and executes authentication tests for each
configured EAP type defined in a JSON configuration file.

Key Features:
- Detects the system's package manager and installs missing dependencies.
- Clones the latest `eapol_test` source from the Hostapd repository and builds it if required.
- Loads EAP authentication test configurations from a JSON file.
- Runs EAP authentication tests against a RADIUS server and logs results.
- Implements log rotation to prevent excessive log growth.
- Validates the configuration file for required fields.
- Supports command-line arguments for specifying a single EAP type and enabling debug mode.

Requirements:
- FreeRADIUS server set up and configured.
- JSON configuration file specifying EAP test parameters.
- System dependencies: `jq`, `wpa_supplicant`, `git`, `make`, `gcc`, `libssl-dev`.

Usage:
```bash
python3 -m eap_test_suite.cli --eap PEAP
python3 -m eap_test_suite.cli  # Runs all configured EAP tests
python3 -m eap_test_suite.cli --debug  # Enables debug logging
eap-test-suite --debug  # After installation
```

Author: [Your Name]
Date: [Date]
License: MIT
"""

import argparse
import json
import logging
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# Paths
PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = SRC_ROOT.parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOG_DIR = PROJECT_ROOT / "logs"
CONFIG_FILE = CONFIG_DIR / "config.json"  # Path to the configuration file containing EAP test details
LOG_FILE = LOG_DIR / "eap_test.log"  # Log file location
MAX_LOG_SIZE = 5 * 1024 * 1024  # Maximum log file size (5MB) before rotation
LOG_RETENTION_COUNT = 5  # Number of log files to retain
DEPENDENCIES = ["jq", "wpa_supplicant", "git", "make", "gcc", "libssl-dev"]  # Required system dependencies
EAPOL_TEST_PATH = Path("/usr/local/bin/eapol_test")  # Path to the compiled eapol_test binary
HOSTAPD_REPO = "https://w1.fi/hostap.git"  # Git repository for hostapd source code
HOSTAP_SOURCE_DIR = PROJECT_ROOT / "hostap"


@dataclass(frozen=True)
class RadiusConfig:
    server: str
    port: int
    secret: str


@dataclass(frozen=True)
class EAPTypeConfig:
    name: str
    settings: dict[str, Any]

    @property
    def conf_path(self) -> Path:
        return CONFIG_DIR / f"{self.name}.conf"


@dataclass(frozen=True)
class TestConfig:
    radius: RadiusConfig
    eap_types: dict[str, EAPTypeConfig]


def setup_logging(log_file):
    """
    Configures logging with file rotation and console output.

    This function sets up the logging configuration to log messages to a file with rotation and
    to the console. It ensures that the log directory exists, configures a rotating file handler,
    and sets the logging format and level.

    Args:
        log_file (Path): The path to the log file.

    Logging:
        - Logs are saved to the specified file with rotation.
        - Logs are also printed to the console.
    """
    # Ensure the log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure a rotating file handler for logging
    handler = RotatingFileHandler(log_file, maxBytes=MAX_LOG_SIZE, backupCount=LOG_RETENTION_COUNT)

    # Set up basic logging configuration with file rotation and console output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            handler,
            logging.StreamHandler(sys.stdout)
        ]
    )


def detect_package_manager():
    """
    Detects the system's package manager and returns its command name.

    This function checks for the presence of common package managers such as apt, dnf, pacman, and brew.
    If a supported package manager is found, its command name is returned. If no supported package manager
    is found, an error is logged and the script exits.

    Returns:
        str: The command name of the detected package manager.

    Logs:
        - Error if no supported package manager is found.
    """
    for manager in ["apt", "dnf", "pacman", "brew"]:
        if shutil.which(manager):
            return manager
    logging.error("No supported package manager found. Install dependencies manually.")
    sys.exit(1)


def is_package_installed(package_name):
    """
    Checks if a given package is installed on the system.

    This function uses the shutil.which() method to determine if the specified package is available
    on the system's PATH.

    Args:
        package_name (str): The name of the package to check.

    Returns:
        bool: True if the package is installed, False otherwise.
    """
    return shutil.which(package_name) is not None


def install_dependencies():
    """
    Installs required dependencies for building hostapd and eapol_test.

    This function detects the system's package manager and installs the necessary packages for building
    hostapd and eapol_test. It first checks if the required packages are already installed and only installs
    the missing ones.

    Logs:
        - Info messages for installation steps.
        - Error messages if dependency installation fails.
    """
    package_manager = detect_package_manager()

    packages = []
    if package_manager == "apt":
        packages = ["libnl-3-dev", "libnl-genl-3-dev"]
    elif package_manager == "dnf":
        packages = ["libnl3-devel"]
    elif package_manager == "pacman":
        packages = ["libnl"]
    elif package_manager == "brew":
        packages = ["pkg-config", "autoconf", "automake", "libtool", "openssl"]

    packages_to_install = []
    for p in packages:
        base_package = p.split('-')[0]  # Split to remove -dev or -devel
        if not is_package_installed(base_package):
            packages_to_install.append(p)

    if packages_to_install:
        try:
            if package_manager == "apt":
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", *packages_to_install], check=True)
            elif package_manager == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", *packages_to_install], check=True)
            elif package_manager == "pacman":
                subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", *packages_to_install], check=True)
            elif package_manager == "brew":
                subprocess.run(["brew", "install", *packages_to_install], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Dependency installation failed: {e}")
            sys.exit(1)

    # Install Xcode Command Line Tools on macOS if needed
    if sys.platform == 'darwin':
        try:
            # Check if Xcode Command Line Tools are already installed
            if subprocess.run(["xcode-select", "--print-path"], capture_output=True).returncode != 0:
                subprocess.run(["xcode-select", "--install"], check=True)
            else:
                logging.info("Xcode Command Line Tools are already installed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Xcode Command Line Tools installation failed: {e}")
            sys.exit(1)


def build_eapol_test():
    """
    Clones and builds `eapol_test` from the Hostapd repository if it is not already available.
    Ensures macOS-specific configurations and OpenSSL paths are correctly set.
    """
    if EAPOL_TEST_PATH.exists():
        logging.info("eapol_test already exists. Skipping build.")
        return

    logging.info("Installing Dependencies to build eapol_test")
    install_dependencies()

    # Clean previous build artifacts
    logging.info("Cleaning previous build artifacts...")
    if HOSTAP_SOURCE_DIR.exists():
        shutil.rmtree(HOSTAP_SOURCE_DIR)

    logging.info("Cloning and building eapol_test from source...")

    try:
        subprocess.run(
            ["git", "clone", HOSTAPD_REPO, str(HOSTAP_SOURCE_DIR)],
            check=True,
            cwd=PROJECT_ROOT,
        )
        hostapd_dir = HOSTAP_SOURCE_DIR / "wpa_supplicant"

        if hostapd_dir.exists():
            config_path = hostapd_dir / ".config"
            defconfig_path = hostapd_dir / "defconfig"

            # Copy defconfig to .config
            shutil.copy(defconfig_path, config_path)

            # Modify the .config file
            with config_path.open("r") as config_file:
                config_lines = config_file.readlines()

            with config_path.open("w") as config_file:
                for line in config_lines:
                    if line.strip() == "CONFIG_LIBNL32=y":
                        config_file.write("# CONFIG_LIBNL32=y\n")
                    elif "CFLAGS += -I/usr/local/openssl/include" in line:
                        config_file.write("CFLAGS += -I/opt/homebrew/opt/openssl/include/openssl\n")
                    elif "LIBS += -L/usr/local/openssl/lib" in line:
                        config_file.write("LIBS += -L/opt/homebrew/opt/openssl/lib -lssl -lcrypto\n")
                    else:
                        config_file.write(line)

                # Ensure necessary options are set
                required_configs = [
                    "CONFIG_EAPOL_TEST=y\n",
                    "CONFIG_TLS=openssl\n",
                    "CONFIG_TLSV11=y\n",
                    "CONFIG_TLSV12=y\n",
                    "CONFIG_TLSV13=y\n",  # Ensure TLS 1.3 support
                    "CONFIG_TLS_FUNCS=y\n",
                    "CONFIG_OSX=y\n"  # Ensure macOS build compatibility
                ]

                for config in required_configs:
                    if config not in config_lines:
                        config_file.write(config)

            logging.info("Updated .config file:")
            with config_path.open("r") as config_file:
                logging.info(config_file.read())

            # Modify ieee802_1x_kay.c to include OSByteOrder.h for macOS compatibility
            src_file = hostapd_dir / "../src/pae/ieee802_1x_kay.c"
            with src_file.open("r") as file:
                lines = file.readlines()
            with src_file.open("w") as file:
                for line in lines:
                    if line.strip() == "#include <stddef.h>":
                        file.write(
                            "#ifdef __APPLE__\n#include <libkern/OSByteOrder.h>\n#define bswap_64(x) OSSwapInt64(x)\n#else\n#include <byteswap.h>\n#endif\n")
                    file.write(line)

            env = os.environ.copy()
            env.setdefault("PKG_CONFIG_PATH", "/opt/homebrew/opt/openssl/lib/pkgconfig")

            # Build eapol_test
            subprocess.run(["make", "eapol_test"], cwd=hostapd_dir, env=env, check=True)
            shutil.move(str(hostapd_dir / "eapol_test"), str(EAPOL_TEST_PATH))
            logging.info("eapol_test successfully built and installed.")
        else:
            logging.error("hostap/wpa_supplicant directory not found. Cannot build eapol_test.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Build failed: {e}")
        sys.exit(1)


def validate_radius_config(data):
    """
    Validates the radius configuration dictionary.

    This function checks if the given data is a dictionary and contains the required keys
    ("server", "port", "secret"). It also verifies that the values for these keys are of
    the correct data types.

    Args:
        data (dict): The radius configuration data to validate.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    if not isinstance(data, dict):
        return False
    if not all(key in data for key in ["server", "port", "secret"]):
        return False
    if not isinstance(data["server"], str) or not isinstance(data["port"], int) or not isinstance(data["secret"], str):
        return False
    return True


def validate_eap_types_config(data):
    """
    Validates the eap_types configuration dictionary.

    This function checks if the given data is a dictionary and ensures that each EAP type
    configuration within it is also a dictionary (which may be empty in some cases).

    Args:
        data (dict): The eap_types configuration data to validate.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    if not isinstance(data, dict):
        return False
    for eap_type, eap_data in data.items():
        if not isinstance(eap_data, dict):  # In the case of no EAP-specific config, this will be an empty dictionary.
            return False
    return True


def load_config() -> TestConfig:
    """
    Loads and validates the configuration file.

    This function reads the configuration data from a JSON file, validates the structure and content,
    and returns the validated configuration. It raises an error and exits the script if the configuration
    is invalid or if any required keys are missing.

    Raises:
        ValueError: If the configuration structure or content is invalid.
        FileNotFoundError: If the configuration file is not found.
        json.JSONDecodeError: If there is an error parsing the configuration file.
    """
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
            data = json.load(config_file)

        if not isinstance(data, dict) or "radius" not in data or "eap_types" not in data:
            raise ValueError("Invalid configuration structure.")

        if not validate_radius_config(data["radius"]):
            raise ValueError("Invalid radius configuration.")

        if not validate_eap_types_config(data["eap_types"]):
            raise ValueError("Invalid eap_types configuration.")

        radius_config = RadiusConfig(**data["radius"])
        eap_types = {
            eap_type: EAPTypeConfig(name=eap_type, settings=dict(eap_data))
            for eap_type, eap_data in data["eap_types"].items()
        }

        logging.info("Configuration loaded successfully.")
        return TestConfig(radius=radius_config, eap_types=eap_types)

    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)


def execute_eapol_test(config: TestConfig, eap_type: str) -> None:
    """
    Executes eapol_test for the specified EAP type.

    This function runs the eapol_test command for a given EAP type using the configuration
    parameters from the provided config dictionary. It logs the results of the test.

    Args:
        config (TestConfig): The configuration data loaded from the JSON file.
        eap_type (str): The EAP type to test.

    Logs:
        - Info messages indicating whether the test passed.
        - Error messages if the test failed or if the EAP type is not configured.
    """
    eap_config = config.eap_types.get(eap_type)
    if eap_config is None:
        logging.error(f"EAP type {eap_type} is not configured.")
        return

    config_file = eap_config.conf_path
    if not config_file.exists():
        logging.error("Configuration file %s not found for EAP type %s.", config_file, eap_type)
        return

    radius = config.radius

    logging.debug("Executing eapol_test for %s using settings: %s", eap_type, eap_config.settings)

    # Prepare eapol_test command
    command = [
        str(EAPOL_TEST_PATH),
        f"-a{radius.server}",
        f"-p{radius.port}",
        f"-s{radius.secret}",
        f"-c{config_file}",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("EAP type %s test passed.", eap_type)
            if result.stdout:
                logging.debug(result.stdout)
        else:
            logging.error(
                "EAP type %s test failed with return code: %s", eap_type, result.returncode
            )
            if result.stderr:
                logging.error(result.stderr)
    except OSError as e:
        logging.error("EAP type %s test failed to execute: %s", eap_type, e)


def parse_args():
    """
    Parses command-line arguments.

    This function sets up an argument parser for the script and defines the available
    command-line options.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="EAP Authentication Test Script")
    parser.add_argument("-e", "--eap", type=str, nargs='*', help="Test specific EAP types from the configuration file")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def is_radius_server_reachable(server: str, port: int) -> bool:
    """
    Checks if the RADIUS server is reachable.

    This function attempts to establish a connection to the specified RADIUS server and port
    within a timeout period to determine if the server is reachable.

    Args:
        server (str): The RADIUS server address.
        port (int): The RADIUS server port.

    Returns:
        bool: True if the server is reachable, False otherwise.
    """
    try:
        with socket.create_connection((server, port), timeout=5):
            return True
    except (OSError, TimeoutError):
        return False


def cleanup() -> None:
    """
    Cleans up temporary files and directories.

    This function removes the temporary hostap directory if it exists and logs the action.
    """
    if HOSTAP_SOURCE_DIR.exists():
        shutil.rmtree(HOSTAP_SOURCE_DIR)
        logging.info("Temporary hostap directory removed.")


def main():
    """
    Main execution function.

    This function serves as the entry point of the EAP Authentication Test Script. It performs the following tasks:
    1. Parses command-line arguments.
    2. Sets up logging with file rotation and console output.
    3. Builds the eapol_test tool if it is not already available.
    4. Loads the configuration data from the specified JSON file.
    5. Checks if the RADIUS server is reachable before proceeding.
    6. Enables debug-level logging if the debug flag is specified.
    7. Executes EAP tests for specified EAP types or all configured EAP types if none are specified.

    Command-line arguments:
    -e, --eap    : List of specific EAP types to test. If not provided, tests all configured EAP types.
    -d, --debug  : Enable debug-level logging for more detailed output.

    Exits with a non-zero status code if an error occurs during execution.
    """
    # Parse command-line arguments
    args = parse_args()

    # Set up logging
    setup_logging(LOG_FILE)

    try:
        # Build eapol_test if not already available
        build_eapol_test()

        # Load configuration data
        config = load_config()

        # Check if the RADIUS server is reachable
        radius = config.radius
        if not is_radius_server_reachable(radius.server, radius.port):
            logging.error("Radius server %s:%s is not reachable.", radius.server, radius.port)
            sys.exit(1)

        # Enable debug-level logging if the debug flag is specified
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Execute EAP tests for specified EAP types or all configured EAP types if none are specified
        if args.eap:
            for eap_type in args.eap:
                if eap_type in config.eap_types:
                    execute_eapol_test(config, eap_type)
                else:
                    logging.error("EAP type '%s' is not configured.", eap_type)
                    sys.exit(1)
            return

        for eap_type in config.eap_types:
            execute_eapol_test(config, eap_type)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
