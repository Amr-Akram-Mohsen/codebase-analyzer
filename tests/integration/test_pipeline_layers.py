"""
Integration tests for the analyzer pipeline regarding architecture layers.
"""

import subprocess
import sys
from pathlib import Path


def test_pipeline_detects_layer_violations() -> None:
    project_root = Path(__file__).parent.parent / "fixtures" / "layered_project"
    config_path = project_root / "pyproject.toml"
    
    # Run the CLI
    cmd = [sys.executable, "-m", "codebase_analyzer", str(project_root), "--config", str(config_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root.parent.parent.parent.parent))
    
    # It should fail with exit code 1 because there are errors
    assert result.returncode == 1
    
    output = result.stdout
    
    # Verify both violations were found
    assert "LAYER_VIOLATION" in output
    assert "'api.handlers' (layer 'api') imports 'cli.main' (layer 'cli')" in output
    assert "'core.model' (layer 'core') imports 'api.handlers' (layer 'api')" in output
    
    # Verify it correctly parsed the modules
    assert "Modules parsed: 4" in output  # __init__, cli.main, api.handlers, core.model
