import pytest
from pathlib import Path
from codebase_analyzer.python.parser import parse_module
from codebase_analyzer.core.model import Module
from codebase_analyzer.analysis.metrics import detect_complex_functions

def test_cyclomatic_complexity(tmp_path: Path):
    """
    Verifies that the parser calculates complexity correctly
    and the metrics engine flags complex functions.
    """
    content = """
def simple_function():
    # Complexity 1
    pass
    
def complex_function(items):
    # Complexity: 1 (base) + 1 (for) + 1 (if) + 1 (except) = 4
    for i in items:
        if i > 0:
            try:
                print(i)
            except ValueError:
                pass
"""
    file_path = tmp_path / "complex.py"
    file_path.write_text(content)
    
    result = parse_module(file_path, tmp_path)
    assert isinstance(result, Module)
    
    funcs = {f.name: f.complexity for f in result.functions}
    assert funcs["simple_function"] == 1
    assert funcs["complex_function"] == 4
    
    # Run detect_complex_functions with threshold 2
    findings = detect_complex_functions([result], max_complexity=2)
    assert len(findings) == 1
    assert "'complex_function' (Complexity: 4)" in findings[0].message
    assert findings[0].location.module == "complex"


def test_advanced_complexity_constructs(tmp_path: Path):
    """
    Verifies that IfExp, Assert, and Comprehension `if` clauses contribute to complexity.
    """
    content = """
def ternary_and_assert(x):
    # 1 (base) + 1 (IfExp) + 1 (Assert) = 3
    y = 10 if x > 0 else 20
    assert y == 10
    return y

def comprehension_with_if(items):
    # 1 (base) + 2 (two if clauses) = 3
    return [x for x in items if x > 0 if x % 2 == 0]
"""
    file_path = tmp_path / "advanced.py"
    file_path.write_text(content)
    
    result = parse_module(file_path, tmp_path)
    assert isinstance(result, Module)
    
    funcs = {f.name: f.complexity for f in result.functions}
    assert funcs["ternary_and_assert"] == 3
    assert funcs["comprehension_with_if"] == 3
