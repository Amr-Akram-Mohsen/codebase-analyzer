"""
Unit tests for analysis/naming.py.
"""

from codebase_analyzer.analysis.naming import detect_name_collisions
from codebase_analyzer.core.model import ClassDef, FindingKind, FunctionDef, Module


class TestNamingCollisions:
    def test_no_collisions(self) -> None:
        modules = [
            Module(
                path="a.py",
                qualified_name="myapp.a",
                classes=[ClassDef(name="AClass", line_number=1, methods=[])],
                functions=[FunctionDef(name="a_func", line_number=2)],
                imports=[],
            ),
            Module(
                path="b.py",
                qualified_name="myapp.b",
                classes=[ClassDef(name="BClass", line_number=1, methods=[])],
                functions=[FunctionDef(name="b_func", line_number=2)],
                imports=[],
            ),
        ]
        
        findings = detect_name_collisions(modules)
        assert len(findings) == 0

    def test_cross_file_collisions_are_ignored(self) -> None:
        modules = [
            Module(
                path="api/utils.py", 
                qualified_name="myapp.api.utils", 
                classes=[ClassDef(name="Helper", line_number=1, methods=[])], 
                functions=[FunctionDef(name="setup", line_number=5)], 
                imports=[]
            ),
            Module(
                path="db/utils.py", 
                qualified_name="myapp.db.utils", 
                classes=[ClassDef(name="Helper", line_number=1, methods=[])], 
                functions=[FunctionDef(name="setup", line_number=5)], 
                imports=[]
            ),
        ]
        
        # Modules have same name, classes have same name, functions have same name, but they are in different files!
        findings = detect_name_collisions(modules)
        assert len(findings) == 0

    def test_intra_file_function_collision(self) -> None:
        modules = [
            Module(
                path="c.py",
                qualified_name="myapp.c",
                classes=[],
                functions=[
                    FunctionDef(name="setup", line_number=5), 
                    FunctionDef(name="setup", line_number=10),
                    FunctionDef(name="teardown", line_number=20),
                    FunctionDef(name="teardown", line_number=25),
                ],
                imports=[],
            ),
        ]
        
        findings = detect_name_collisions(modules)
        assert len(findings) == 2
        
        assert findings[0].kind == FindingKind.NAME_COLLISION
        assert "Multiple function name collisions in c.py:\n  - 'setup' at lines 5, 10" in findings[0].message
        
        assert findings[1].kind == FindingKind.NAME_COLLISION
        assert "Multiple function name collisions in c.py:\n  - 'teardown' at lines 20, 25" in findings[1].message

    def test_intra_file_class_collision(self) -> None:
        modules = [
            Module(
                path="d.py",
                qualified_name="myapp.d",
                classes=[
                    ClassDef(name="User", line_number=5, methods=[]),
                    ClassDef(name="User", line_number=20, methods=[]),
                ],
                functions=[],
                imports=[],
            ),
        ]
        
        findings = detect_name_collisions(modules)
        assert len(findings) == 1
        
        assert findings[0].kind == FindingKind.NAME_COLLISION
        assert "Multiple class name collisions in d.py:\n  - 'User' at lines 5, 20" in findings[0].message
