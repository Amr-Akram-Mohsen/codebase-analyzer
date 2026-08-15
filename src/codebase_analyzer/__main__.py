"""
Enables running the package via `python -m codebase_analyzer`.
"""

import sys
from codebase_analyzer.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
