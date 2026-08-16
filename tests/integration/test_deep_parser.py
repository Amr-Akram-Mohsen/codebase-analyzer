import pytest
from pathlib import Path
from codebase_analyzer.python.parser import parse_module
from codebase_analyzer.core.model import Module

def test_deep_parsing(tmp_path: Path):
    """
    Verifies that the NodeVisitor correctly finds local imports,
    inner functions, and deeply nested classes.
    """
    content = """
def outer_function():
    from foo import bar # Local import
    
    class InnerClass:
        def inner_method(self):
            import sys # Nested local import
            pass
            
    def inner_func():
        pass
"""
    file_path = tmp_path / "deep.py"
    file_path.write_text(content)
    
    result = parse_module(file_path, tmp_path)
    assert isinstance(result, Module)
    
    # It should find all 3 functions: outer_function, outer_function.InnerClass.inner_method, outer_function.inner_func
    function_names = {f.name for f in result.functions}
    assert function_names == {"outer_function", "outer_function.InnerClass.inner_method", "outer_function.inner_func"}
    
    # It should find InnerClass
    class_names = {c.name for c in result.classes}
    assert class_names == {"InnerClass"}
    
    # It should find both imports
    import_targets = {i.target_module for i in result.imports}
    assert import_targets == {"foo.bar", "sys"}
