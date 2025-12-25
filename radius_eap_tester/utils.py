#!/usr/bin/env python3
"""
Project Title: EAPTestor

EAP Testing Framework for FreeRADIUS

Author: Kris Armstrong
__version__ = "4.1.1"
"""

import logging


def setup_logging(log_file: str = "eaptestor.log", verbose: bool = False):
    """Configure logging to file and console."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
    logger.addHandler(console_handler)
