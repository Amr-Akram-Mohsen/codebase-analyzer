"""
Integration tests for python/parser.py and python/discovery.py.
"""

from pathlib import Path
import pytest

from codebase_analyzer.core.model import Finding, FindingKind, Module
from codebase_analyzer.python.discovery import discover_python_files
from codebase_analyzer.python.parser import parse_module


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Fixture that provides a temporary directory for tests."""
    return tmp_path


def create_file(root: Path, relative_path: str, content: str) -> Path:
    """Helper to create a file with content inside the root directory."""
    file_path = root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path


class TestParser:
    
    def test_class_and_methods(self, temp_project: Path) -> None:
        source = """
class User:
    def get_name(self): pass
    def set_name(self, name): pass
"""
        file_path = create_file(temp_project, "myapp/models.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        assert result.qualified_name == "myapp.models"
        assert len(result.classes) == 1
        
        cls = result.classes[0]
        assert cls.name == "User"
        assert len(cls.methods) == 2
        assert cls.methods[0].name == "get_name"
        assert cls.methods[1].name == "set_name"

    def test_top_level_function(self, temp_project: Path) -> None:
        source = """
def helper_func():
    pass
"""
        file_path = create_file(temp_project, "myapp/utils.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        assert len(result.functions) == 1
        assert result.functions[0].name == "helper_func"
        assert len(result.classes) == 0

    def test_absolute_imports(self, temp_project: Path) -> None:
        source = """
import os
import sys as system
from pathlib import Path
from myapp.core import config
"""
        file_path = create_file(temp_project, "myapp/main.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        assert len(result.imports) == 4
        targets = {imp.target_module for imp in result.imports}
        assert targets == {"os", "sys", "pathlib.Path", "myapp.core.config"}
        for imp in result.imports:
            assert imp.source_module == "myapp.main"

    def test_relative_imports(self, temp_project: Path) -> None:
        source = """
from . import helpers
from .helpers import HelperClass
from ..core import model
from .. import common
"""
        file_path = create_file(temp_project, "myapp/utils/funcs.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        targets = {imp.target_module for imp in result.imports}
        assert "myapp.utils.helpers" in targets
        assert "myapp.utils.helpers.HelperClass" in targets
        assert "myapp.core.model" in targets
        assert "myapp.common" in targets

    def test_relative_imports_in_init(self, temp_project: Path) -> None:
        source = """
from . import funcs
from .. import core
"""
        file_path = create_file(temp_project, "myapp/utils/__init__.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        assert result.qualified_name == "myapp.utils"
        targets = {imp.target_module for imp in result.imports}
        assert "myapp.utils.funcs" in targets
        assert "myapp.core" in targets

    def test_syntax_error(self, temp_project: Path) -> None:
        source = """
def bad_func(
    missing_closing_paren
"""
        file_path = create_file(temp_project, "myapp/bad.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Finding)
        assert result.kind == FindingKind.PARSE_ERROR
        assert result.location is not None
        assert result.location.module == "myapp.bad"

    def test_empty_file(self, temp_project: Path) -> None:
        file_path = create_file(temp_project, "myapp/empty.py", "")
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        assert len(result.classes) == 0
        assert len(result.functions) == 0
        assert len(result.imports) == 0

    def test_only_imports(self, temp_project: Path) -> None:
        source = """
import os
from . import sibling
"""
        file_path = create_file(temp_project, "myapp/imports_only.py", source)
        result = parse_module(file_path, temp_project)
        
        assert isinstance(result, Module)
        assert len(result.classes) == 0
        assert len(result.functions) == 0
        assert len(result.imports) == 2


class TestDiscovery:
    
    def test_discovery_skips_directories(self, temp_project: Path) -> None:
        # Create some valid python files
        create_file(temp_project, "myapp/good1.py", "")
        create_file(temp_project, "myapp/nested/good2.py", "")
        
        # Create some python files in directories that should be skipped
        create_file(temp_project, ".git/hooks/pre-commit.py", "")
        create_file(temp_project, "myapp/__pycache__/compiled.py", "")
        create_file(temp_project, ".venv/lib/site-packages/pkg.py", "")
        create_file(temp_project, "venv/bin/activate_this.py", "")
        create_file(temp_project, "env/script.py", "")
        create_file(temp_project, "node_modules/pkg/index.py", "")
        
        files = discover_python_files(temp_project)
        
        # Should only find the good ones
        assert len(files) == 2
        file_names = {f.name for f in files}
        assert file_names == {"good1.py", "good2.py"}
