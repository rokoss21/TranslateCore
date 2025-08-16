#!/usr/bin/env python3
"""
TranslateCore CLI Entry Point

Simple entry point for the CLI tool.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from translatecore.cli import main

if __name__ == "__main__":
    main()
