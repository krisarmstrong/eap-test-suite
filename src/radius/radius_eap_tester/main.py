#!/usr/bin/env python3
"""
Project Title: EAPTestor

EAP Testing Framework for FreeRADIUS

Author: Kris Armstrong
__version__ = "4.1.1"
"""

from .config import load_config, generate_config_template
from .eap_tests import EAPTestor
from .utils import setup_logging
import argparse
import logging
import os


def main():
    parser = argparse.ArgumentParser(description="EAPTestor v4.1 - EAP Testing Framework for FreeRADIUS")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--config", default="conf/config.json", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate test execution without running tests")
    parser.add_argument("--generate-config", action="store_true", help="Generate a template config file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    if args.generate_config:
        generate_config_template(args.config)
        return

    try:
        config = load_config(args.config)
        eaptestor = EAPTestor(config, dry_run=args.dry_run)
        eaptestor.run_all_tests(parallel=args.parallel)
    except Exception as e:
        logger.error(f"EAPTestor execution failed: {e}")
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()