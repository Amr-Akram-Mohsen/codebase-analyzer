"""
Discovers Python source files in a project directory.
"""

import os
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "env", "node_modules"}


def discover_python_files(root_dir: str | Path) -> list[Path]:
    """
    Recursively discovers all .py files in the given directory.

    Skips common hidden/build directories like .git, __pycache__, and venvs.
    """
    root_path = Path(root_dir).resolve()
    python_files = []

    if not root_path.exists():
        return python_files

    if root_path.is_file():
        if root_path.suffix == ".py":
            python_files.append(root_path)
        return python_files

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Modify dirnames in-place to skip unwanted directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        
        current_dir = Path(dirpath)
        
        # Double check the current_dir just in case root_dir itself contained a skipped dir
        if any(part in SKIP_DIRS or part.startswith(".") for part in current_dir.parts):
            continue
            
        for filename in filenames:
            if filename.endswith(".py"):
                python_files.append(current_dir / filename)

    return python_files
