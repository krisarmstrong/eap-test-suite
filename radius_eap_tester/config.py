#!/usr/bin/env python3
"""
Project Title: EAPTestor

EAP Testing Framework for FreeRADIUS

Author: Kris Armstrong
__version__ = "4.1.1"
"""

import json
import os
import logging
from jsonschema import validate, ValidationError
from typing import Dict

logger = logging.getLogger(__name__)

CONFIG_SCHEMA = {
    "type": "object",
    "required": ["server", "eap_methods"],
    "properties": {
        "server": {
            "type": "object",
            "required": [
                "ipaddress",
                "port",
                "secretkey",
                "private_key_password",
                "identity",
                "password",
            ],
            "properties": {
                "ipaddress": {"type": "string"},
                "port": {"type": "integer"},
                "secretkey": {"type": "string"},
                "private_key_password": {"type": "string"},
                "identity": {"type": "string"},
                "password": {"type": "string"},
            },
        },
        "eap_methods": {
            "type": "object",
            "required": [
                "tls",
                "ttls_tls",
                "peap_tls",
                "peap_mschapv2",
                "ttls_md5",
                "ttls_mschapv2",
                "eap_fast",
            ],
            "properties": {
                "tls": {"$ref": "#/definitions/eap_method"},
                "ttls_tls": {"$ref": "#/definitions/eap_method"},
                "peap_tls": {"$ref": "#/definitions/eap_method"},
                "peap_mschapv2": {"$ref": "#/definitions/eap_method"},
                "ttls_md5": {"$ref": "#/definitions/eap_method"},
                "ttls_mschapv2": {"$ref": "#/definitions/eap_method"},
                "eap_fast": {"$ref": "#/definitions/eap_method"},
            },
        },
    },
    "definitions": {
        "eap_method": {
            "type": "object",
            "required": ["enabled", "config"],
            "properties": {"enabled": {"type": "boolean"}, "config": {"type": "object"}},
        }
    },
}


def load_config(config_path: str) -> Dict:
    """Load and validate configuration from JSON."""
    if not os.path.exists(config_path):
        logger.error(
            f"Config file {config_path} not found. Create it using 'eaptestor --generate-config'."
        )
        raise FileNotFoundError(f"Config file {config_path} not found")

    with open(config_path, "r") as f:
        config = json.load(f)

    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        logger.error(f"Invalid configuration: {e.message}. Check {config_path} against the schema.")
        raise ValueError(f"Invalid configuration: {e.message}")

    # Override sensitive settings with environment variables if present
    server = config["server"]
    for key in ["secretkey", "private_key_password", "password"]:
        env_value = os.getenv(f"EAPTESTOR_{key.upper()}")
        if env_value:
            server[key] = env_value

    return config


def generate_config_template(output_path: str):
    """Generate a template config.json file."""
    template = {
        "server": {
            "ipaddress": "192.168.1.1",
            "port": 1812,
            "secretkey": "your_secret",
            "private_key_password": "your_key_password",
            "identity": "testuser",
            "password": "testpass",
        },
        "eap_methods": {
            "tls": {
                "enabled": False,
                "config": {
                    "certificate_file": "",
                    "private_key_file": "",
                    "private_key_passwd": "",
                    "ca_cert": "",
                },
            },
            "ttls_tls": {
                "enabled": False,
                "config": {
                    "certificate_file": "",
                    "private_key_file": "",
                    "private_key_passwd": "",
                    "ca_cert": "",
                },
            },
            "peap_tls": {
                "enabled": False,
                "config": {
                    "certificate_file": "",
                    "private_key_file": "",
                    "private_key_passwd": "",
                    "ca_cert": "",
                },
            },
            "peap_mschapv2": {"enabled": False, "config": {"mschapv2": True}},
            "ttls_md5": {"enabled": False, "config": {"md5": True}},
            "ttls_mschapv2": {"enabled": False, "config": {"mschapv2": True}},
            "eap_fast": {"enabled": False, "config": {"pac_file": ""}},
        },
    }
    try:
        with open(output_path, "w") as f:
            json.dump(template, f, indent=2)
        logger.info(f"Generated template config at {output_path}")
        print(f"Template config generated at {output_path}")
    except Exception as e:
        logger.error(f"Failed to generate config: {e}")
        raise
