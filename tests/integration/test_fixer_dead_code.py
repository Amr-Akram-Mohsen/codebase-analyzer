"""
Integration tests for the dead code auto-fixer.
"""

from pathlib import Path

from codebase_analyzer.core.model import AnalysisResult, Finding, FindingKind, Location, Module
from codebase_analyzer.fixer.safe_fixer import apply_safe_fixes


def test_fixer_deletes_dead_code(tmp_path: Path) -> None:
    # Set up a fake project root in the temp directory
    project_root = tmp_path / "project"
    project_root.mkdir()
    
    # Create an active file and a dead file
    active_file = project_root / "active.py"
    active_file.write_text("def run(): pass\n")
    
    dead_file = project_root / "dead.py"
    dead_file.write_text("def unused(): pass\n")
    
    # Construct an artificial analysis result
    result = AnalysisResult(
        project_root=str(project_root),
        modules=[
            Module(path="active.py", qualified_name="active", classes=[], functions=[], imports=[]),
            Module(path="dead.py", qualified_name="dead", classes=[], functions=[], imports=[]),
        ],
        findings=[
            Finding(
                kind=FindingKind.DEAD_CODE,
                severity=None,
                message="Orphaned Module",
                location=Location(module="dead", line=None),
            )
        ],
    )
    
    # Apply safe fixes targeting the whole project
    apply_safe_fixes(result, target_paths=[str(project_root)])
    
    # Verify the dead file was deleted
    assert not dead_file.exists(), "dead.py should have been deleted by the fixer"
    
    # Verify the active file remains untouched
    assert active_file.exists(), "active.py should not have been touched"
    assert active_file.read_text() == "def run(): pass\n"

def test_fixer_only_deletes_targeted_dead_code(tmp_path: Path) -> None:
    # Set up a fake project root in the temp directory
    project_root = tmp_path / "project"
    project_root.mkdir()
    
    # Create two dead files
    dead1 = project_root / "dead1.py"
    dead1.write_text("pass\n")
    
    dead2 = project_root / "dead2.py"
    dead2.write_text("pass\n")
    
    result = AnalysisResult(
        project_root=str(project_root),
        modules=[
            Module(path="dead1.py", qualified_name="dead1", classes=[], functions=[], imports=[]),
            Module(path="dead2.py", qualified_name="dead2", classes=[], functions=[], imports=[]),
        ],
        findings=[
            Finding(
                kind=FindingKind.DEAD_CODE,
                severity=None,
                message="",
                location=Location(module="dead1", line=None),
            ),
            Finding(
                kind=FindingKind.DEAD_CODE,
                severity=None,
                message="",
                location=Location(module="dead2", line=None),
            )
        ],
    )
    
    # Target only dead1
    apply_safe_fixes(result, target_paths=[str(dead1)])
    
    # dead1 should be deleted, dead2 should remain
    assert not dead1.exists()
    assert dead2.exists()
