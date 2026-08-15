"""
Tests for the safe fixer engine.
"""

from pathlib import Path

from codebase_analyzer.cli.main import main
from codebase_analyzer.core.analyzer import analyze
from codebase_analyzer.core.model import AnalysisConfig
from codebase_analyzer.fixer.safe_fixer import apply_safe_fixes


def test_fix_duplicate_identical_function(tmp_path: Path) -> None:
    # Set up file with duplicate identical functions
    code = (
        "def hello():\n"
        "    print('world')\n"
        "\n"
        "def some_other_func():\n"
        "    pass\n"
        "\n"
        "def hello():\n"
        "    print('world')\n"
    )
    
    file_path = tmp_path / "dup.py"
    file_path.write_text(code, encoding="utf-8")
    
    config = AnalysisConfig(layer_rules=[])
    result = analyze(tmp_path, config)
    
    apply_safe_fixes(result, [str(tmp_path)])
    
    fixed_code = file_path.read_text(encoding="utf-8")
    # One of the hello() should be deleted
    assert fixed_code.count("def hello():") == 1
    assert fixed_code.count("print('world')") == 1
    assert fixed_code.count("def some_other_func():") == 1


def test_no_fix_different_functions(tmp_path: Path) -> None:
    # Set up file with duplicate names but different bodies
    code = (
        "def hello():\n"
        "    print('world1')\n"
        "\n"
        "def hello():\n"
        "    print('world2')\n"
    )
    
    file_path = tmp_path / "dup.py"
    file_path.write_text(code, encoding="utf-8")
    
    config = AnalysisConfig(layer_rules=[])
    result = analyze(tmp_path, config)
    
    apply_safe_fixes(result, [str(tmp_path)])
    
    fixed_code = file_path.read_text(encoding="utf-8")
    # Neither should be deleted
    assert fixed_code.count("def hello():") == 2
    assert fixed_code.count("print('world1')") == 1
    assert fixed_code.count("print('world2')") == 1


def test_fix_commented_code(tmp_path: Path) -> None:
    # Set up file with commented out structural code
    code = (
        "def live_func():\n"
        "    pass\n"
        "\n"
        "# def commented_func():\n"
        "#     return 1\n"
        "\n"
        "# Just a normal comment\n"
        "x = 1\n"
    )
    
    file_path = tmp_path / "comment.py"
    file_path.write_text(code, encoding="utf-8")
    
    config = AnalysisConfig(layer_rules=[])
    result = analyze(tmp_path, config)
    
    apply_safe_fixes(result, [str(tmp_path)])
    
    fixed_code = file_path.read_text(encoding="utf-8")
    assert "def live_func():" in fixed_code
    assert "# Just a normal comment" in fixed_code
    assert "x = 1" in fixed_code
    assert "commented_func" not in fixed_code
