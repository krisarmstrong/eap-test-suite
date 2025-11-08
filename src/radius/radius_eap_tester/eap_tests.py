#!/usr/bin/env python3
"""
Project Title: EAPTestor

EAP Testing Framework for FreeRADIUS

Author: Kris Armstrong
__version__ = "4.1.1"
"""

import subprocess
import logging
import os
import tempfile
import json
from dataclasses import dataclass
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class EAPTest:
    name: str
    config: Dict
    requires_password: bool
    enabled: bool

class EAPTestor:
    EAPOL_TEST_BIN = "eapol_test"  # Assumes in PATH or specify full path

    def __init__(self, config: Dict, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.tests = self.define_tests()

    def define_tests(self) -> List[EAPTest]:
        """Define EAP tests based on configuration."""
        eap_methods = self.config.get("eap_methods", {})
        return [
            EAPTest("tls", eap_methods["tls"]["config"], False, eap_methods["tls"]["enabled"]),
            EAPTest("ttls_tls", eap_methods["ttls_tls"]["config"], False, eap_methods["ttls_tls"]["enabled"]),
            EAPTest("peap_tls", eap_methods["peap_tls"]["config"], False, eap_methods["peap_tls"]["enabled"]),
            EAPTest("peap_mschapv2", eap_methods["peap_mschapv2"]["config"], True, eap_methods["peap_mschapv2"]["enabled"]),
            EAPTest("ttls_md5", eap_methods["ttls_md5"]["config"], True, eap_methods["ttls_md5"]["enabled"]),
            EAPTest("ttls_mschapv2", eap_methods["ttls_mschapv2"]["config"], True, eap_methods["ttls_mschapv2"]["enabled"]),
            EAPTest("eap_fast", eap_methods["eap_fast"]["config"], True, eap_methods["eap_fast"]["enabled"]),
        ]

    def show_config(self):
        """Display current configuration."""
        logger.info("Current configuration:")
        server = self.config.get("server", {})
        for key, value in server.items():
            if key not in ["private_key_password", "password", "secretkey"]:
                print(f"{key.capitalize()}: {value}")
        print("Sensitive data (keys, passwords) omitted for security.")
        enabled_methods = ", ".join(method for method, conf in self.config.get("eap_methods", {}).items() if conf["enabled"])
        logger.info(f"EAP methods enabled: {enabled_methods}")
        print(f"EAP methods enabled: {enabled_methods}")

    def update_key(self, config_data: Dict, config_file: str):
        """Update private key password in temporary config file."""
        logger.debug("Updating private key in %s", config_file)
        try:
            config_data["private_key_passwd"] = self.config["server"]["private_key_password"]
            with open(config_file, "w") as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update %s: {e}. Ensure write permissions.", config_file)
            raise

    def run_test(self, test: EAPTest) -> Dict:
        """Run a single EAP test and return result."""
        if not test.enabled:
            logger.info(f"Skipping {test.name} (disabled)")
            return {"name": test.name, "status": "skipped", "error": None}

        if self.dry_run:
            logger.info(f"Dry run: Would execute {test.name} test")
            return {"name": test.name, "status": "dry_run", "error": None}

        # Validate config paths
        for key in ["certificate_file", "private_key_file", "ca_cert", "pac_file"]:
            if key in test.config and test.config[key] and not os.path.exists(test.config[key]):
                logger.error(f"Invalid {key} for {test.name}: {test.config[key]} does not exist")
                return {"name": test.name, "status": "failed", "error": f"Invalid {key}: {test.config[key]} does not exist"}

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as temp_conf:
            temp_conf_path = temp_conf.name
            json.dump(test.config, temp_conf, indent=2)

        self.update_key(test.config, temp_conf_path)

        logger.info(f"Running {test.name} test")
        cmd = [
            self.EAPOL_TEST_BIN,
            "-c", temp_conf_path,
            "-a", self.config["server"]["ipaddress"],
            "-p", str(self.config["server"]["port"]),
            "-s", self.config["server"]["secretkey"],
            "-r", "0",
            "-M", self.config["server"]["identity"],
            "-o",
        ]
        if test.requires_password:
            cmd.extend(["-P", self.config["server"]["password"]])

        try:
            if not self.dry_run:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"{test.name} test completed successfully")
            status = {"name": test.name, "status": "success" if not self.dry_run else "dry_run", "error": None}
        except subprocess.CalledProcessError as e:
            logger.error(f"{test.name} test failed: {e.stderr}. Check FreeRADIUS server and config.")
            status = {"name": test.name, "status": "failed", "error": e.stderr}
        except FileNotFoundError:
            logger.error(f"{test.name} test failed: {self.EAPOL_TEST_BIN} not found. Ensure it is installed.")
            status = {"name": test.name, "status": "failed", "error": f"{self.EAPOL_TEST_BIN} not found"}
        finally:
            try:
                os.unlink(temp_conf_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_conf_path}: {e}")

        return status

    def run_all_tests(self, parallel: bool = False):
        """Run all enabled EAP tests, optionally in parallel."""
        self.show_config()
        results = []

        enabled_tests = [test for test in self.tests if test.enabled]
        if not enabled_tests:
            logger.warning("No EAP methods enabled. Update config.json to enable at least one method.")
            print("Warning: No EAP methods enabled.")
            return results

        if parallel:
            logger.info("Running tests in parallel")
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(self.run_test, enabled_tests))
        else:
            logger.info("Running tests sequentially")
            for test in tqdm(enabled_tests, desc="Testing EAP methods", unit="test"):
                results.append(self.run_test(test))

        # Export results
        results_json = {"tests": results, "timestamp": str(datetime.now())}
        try:
            with open("test_results.json", "w") as f:
                json.dump(results_json, f, indent=2)
            logger.info("Test results exported to test_results.json")
            print("Test results exported to test_results.json")
        except Exception as e:
            logger.warning(f"Failed to export results: {e}")

        logger.info("Test Summary:")
        print("\nTest Summary:")
        for result in results:
            status = result["status"].upper()
            msg = f"{result['name']}: {status}"
            if result["error"]:
                msg += f" (Error: {result['error']})"
            logger.info(msg)
            print(msg)

        return results