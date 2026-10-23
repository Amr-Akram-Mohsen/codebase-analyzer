"""
Unit tests for symbol-level dead code detection.
"""

from pathlib import Path
from codebase_analyzer.analysis.dead_code import detect_dead_symbols
from codebase_analyzer.core.model import FindingKind, Module
from codebase_analyzer.python.parser import parse_module


class TestDeadSymbols:
    def test_detects_unused_function_class_variable(self, tmp_path: Path) -> None:
        code = """
UNUSED_CONST = 42
USED_CONST = 100

class UnusedClass:
    pass

class UsedClass:
    pass

def unused_func():
    pass

def used_func():
    return USED_CONST

def caller():
    obj = UsedClass()
    return used_func()
"""
        file_path = tmp_path / "mod.py"
        file_path.write_text(code, encoding="utf-8")

        # Second module that calls caller()
        code2 = """
from mod import caller
res = caller()
"""
        file_path2 = tmp_path / "main_app.py"
        file_path2.write_text(code2, encoding="utf-8")

        m1 = parse_module(file_path, tmp_path)
        m2 = parse_module(file_path2, tmp_path)
        assert isinstance(m1, Module)
        assert isinstance(m2, Module)

        findings = detect_dead_symbols([m1, m2])
        
        messages = [f.message for f in findings]
        assert "Unused variable 'UNUSED_CONST'" in messages
        assert "Unused class 'UnusedClass'" in messages
        assert "Unused function 'unused_func'" in messages
        
        # Verify used items are NOT flagged
        assert "Unused variable 'USED_CONST'" not in messages
        assert "Unused class 'UsedClass'" not in messages
        assert "Unused function 'used_func'" not in messages
        assert "Unused function 'caller'" not in messages

    def test_exempts_dunder_and_special_methods(self, tmp_path: Path) -> None:
        code = """
class MyModel:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return f"MyModel({self.x})"

    def __str__(self):
        return str(self.x)

    def _unused_private_method(self):
        pass
"""
        file_path = tmp_path / "model.py"
        file_path.write_text(code, encoding="utf-8")

        # Module that uses MyModel
        code2 = """
from model import MyModel
m = MyModel(1)
"""
        file_path2 = tmp_path / "app.py"
        file_path2.write_text(code2, encoding="utf-8")

        m1 = parse_module(file_path, tmp_path)
        m2 = parse_module(file_path2, tmp_path)

        findings = detect_dead_symbols([m1, m2])
        messages = [f.message for f in findings]

        assert not any("__init__" in m for m in messages)
        assert not any("__repr__" in m for m in messages)
        assert not any("__str__" in m for m in messages)
        assert "Unused method 'MyModel._unused_private_method'" in messages

    def test_exempts_framework_decorators(self, tmp_path: Path) -> None:
        code = """
@app.get("/health")
def health_check():
    return {"status": "ok"}

@pytest.fixture
def sample_data():
    return [1, 2, 3]

class MyService:
    @property
    def is_active(self):
        return True

    @classmethod
    def create(cls):
        return cls()
"""
        file_path = tmp_path / "routes.py"
        file_path.write_text(code, encoding="utf-8")

        m = parse_module(file_path, tmp_path)
        findings = detect_dead_symbols([m])
        messages = [f.message for f in findings]

        assert not any("health_check" in m for m in messages)
        assert not any("sample_data" in m for m in messages)
        assert not any("is_active" in m for m in messages)
        assert not any("create" in m for m in messages)

    def test_exempts_all_exports(self, tmp_path: Path) -> None:
        code = """
__all__ = ["public_api_func", "PublicClass"]

def public_api_func():
    pass

class PublicClass:
    pass

def truly_unused():
    pass
"""
        file_path = tmp_path / "exports.py"
        file_path.write_text(code, encoding="utf-8")

        m = parse_module(file_path, tmp_path)
        findings = detect_dead_symbols([m])
        messages = [f.message for f in findings]

        assert not any("public_api_func" in m for m in messages)
        assert not any("PublicClass" in m for m in messages)
        assert "Unused function 'truly_unused'" in messages
