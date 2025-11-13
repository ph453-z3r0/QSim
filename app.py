#!/usr/bin/env python
"""Convenience launcher for indiqsim_cli that automatically handles PYTHONPATH."""

import sys
from pathlib import Path

# Add src/ to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the CLI
from indiqsim_cli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

