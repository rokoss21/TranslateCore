#!/usr/bin/env python3
"""
Docker wrapper for TranslateCore CLI

This script ensures proper module loading in Docker environment
"""

import sys
import os

# Add source paths for Docker environment
sys.path.insert(0, '/app/src')
sys.path.insert(0, '/app')

# Now import and run the CLI
try:
    from src.translatecore.cli import main
    main()
except ImportError:
    try:
        from translatecore.cli import main
        main()
    except ImportError as e:
        print(f"❌ Failed to import CLI: {e}")
        print("💡 Docker environment may need adjustment")
        sys.exit(1)
