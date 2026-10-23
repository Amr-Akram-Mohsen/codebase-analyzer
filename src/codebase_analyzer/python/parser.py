"""
Parses Python source files and translates them into language-neutral IR objects.

This is the only module that imports `ast`. It acts as the language boundary.
"""

import ast
from pathlib import Path

from codebase_analyzer.core.model import (
    ClassDef,
    Finding,
    FindingKind,
    FunctionDef,
    ImportRef,
    Location,
    Module,
    Severity,
    VariableDef,
)


def _get_decorator_name(node: ast.expr) -> str:
    """Extracts a dotted decorator name from an AST node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        base = _get_decorator_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    elif isinstance(node, ast.Call):
        return _get_decorator_name(node.func)
    return ""


def _get_qualified_name(file_path: Path, package_root: Path) -> str:
    """Derives the qualified module name from its file path relative to the root."""
    try:
        rel_path = file_path.relative_to(package_root)
    except ValueError:
        # Fallback if not actually relative
        rel_path = Path(file_path.name)
    
    parts = list(rel_path.parts)
    if not parts:
        return ""
    
    # Remove .py extension from the last part
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
        
    # Handle __init__.py
    if parts[-1] == "__init__":
        parts.pop()
        
    # Support standard src/ layout
    if parts and parts[0] == "src":
        parts.pop(0)
        
    return ".".join(parts)


def _resolve_relative_import(
    level: int, module: str | None, current_qualified_name: str, is_init: bool
) -> str:
    """
    Resolves a relative import to an absolute qualified name.
    
    level: number of leading dots (e.g., 1 for '.', 2 for '..')
    module: the module name imported (can be None for 'from . import foo')
    current_qualified_name: the absolute qualified name of the importing module
    is_init: whether the importing module is an __init__.py file
    """
    parts = current_qualified_name.split(".") if current_qualified_name else []
    
    if not is_init and parts:
        parts.pop()
        
    for _ in range(level - 1):
        if parts:
            parts.pop()
        else:
            break
            
    base = ".".join(parts)
    if base and module:
        return f"{base}.{module}"
    elif base:
        return base
    return module or ""


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
        
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_AsyncFor(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_match_case(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_IfExp(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_Assert(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_comprehension(self, node):
        self.complexity += len(node.ifs)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        # Do not recurse into nested functions when calculating parent complexity!
        pass
        
    def visit_AsyncFunctionDef(self, node):
        pass


def calculate_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    visitor = ComplexityVisitor()
    for child in node.body:
        visitor.visit(child)
    return visitor.complexity


class ModuleVisitor(ast.NodeVisitor):
    def __init__(self, qualified_name: str, is_init: bool):
        self.qualified_name = qualified_name
        self.is_init = is_init
        
        self.classes: list[ClassDef] = []
        self.functions: list[FunctionDef] = []
        self.imports: list[ImportRef] = []
        self.has_main_block: bool = False
        self._current_scope: str | None = None
        self._in_class: bool = False
        self.string_literals: list[str] = []
        self.referenced_names: set[str] = set()
        self.exported_names: set[str] = set()
        self.variables: list[VariableDef] = []

    def visit_ClassDef(self, node):
        decorators = [_get_decorator_name(d) for d in node.decorator_list]
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_decorators = [_get_decorator_name(d) for d in item.decorator_list]
                methods.append(
                    FunctionDef(
                        name=item.name,
                        line_number=item.lineno,
                        end_line_number=getattr(item, "end_lineno", None),
                        complexity=calculate_complexity(item),
                        decorators=method_decorators,
                        is_method=True,
                    )
                )
        
        class_def = ClassDef(
            name=node.name,
            line_number=node.lineno,
            methods=methods,
            end_line_number=getattr(node, "end_lineno", None),
            decorators=decorators,
        )
        self.classes.append(class_def)
        
        prev_scope = self._current_scope
        prev_in_class = self._in_class
        self._current_scope = f"{self._current_scope}.{node.name}" if self._current_scope else node.name
        self._in_class = True
        self.generic_visit(node)
        self._in_class = prev_in_class
        self._current_scope = prev_scope
        
    def visit_FunctionDef(self, node):
        self._visit_func(node)
        
    def visit_AsyncFunctionDef(self, node):
        self._visit_func(node)
        
    def _visit_func(self, node):
        name = node.name
        if self._current_scope:
            name = f"{self._current_scope}.{name}"
            
        decorators = [_get_decorator_name(d) for d in node.decorator_list]
        self.functions.append(
            FunctionDef(
                name=name,
                line_number=node.lineno,
                end_line_number=getattr(node, "end_lineno", None),
                complexity=calculate_complexity(node),
                decorators=decorators,
                is_method=self._in_class,
            )
        )
        
        prev_scope = self._current_scope
        prev_in_class = self._in_class
        self._current_scope = name
        self._in_class = False
        self.generic_visit(node)
        self._in_class = prev_in_class
        self._current_scope = prev_scope

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == "__name__":
                self.has_main_block = True
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) > 2:
            self.string_literals.append(node.value)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.referenced_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load):
            self.referenced_names.add(node.attr)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if not self._current_scope:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    self.exported_names.add(elt.value)
                    elif not target.id.startswith("__"):
                        self.variables.append(VariableDef(name=target.id, line_number=node.lineno))
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if not self._current_scope:
            if isinstance(node.target, ast.Name):
                if node.target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                self.exported_names.add(elt.value)
                elif not node.target.id.startswith("__"):
                    self.variables.append(VariableDef(name=node.target.id, line_number=node.lineno))
        self.generic_visit(node)
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(
                ImportRef(
                    source_module=self.qualified_name,
                    target_module=alias.name,
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)
            
    def visit_ImportFrom(self, node):
        level = node.level
        module = node.module
        
        if level > 0:
            base_module = _resolve_relative_import(level, module, self.qualified_name, self.is_init)
        else:
            base_module = module or ""
            
        for alias in node.names:
            if base_module:
                target_module = f"{base_module}.{alias.name}"
            else:
                target_module = alias.name
                
            self.imports.append(
                ImportRef(
                    source_module=self.qualified_name,
                    target_module=target_module,
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)


def parse_module(file_path: Path, package_root: Path) -> Module | Finding:
    """
    Parses a single Python file into a Module IR object.
    
    On success, returns the populated Module.
    On failure (syntax error, file read error), returns a PARSE_ERROR Finding.
    """
    qualified_name = _get_qualified_name(file_path, package_root)
    
    try:
        rel_path_str = str(file_path.relative_to(package_root).as_posix())
    except ValueError:
        rel_path_str = file_path.name

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))
    except SyntaxError as e:
        return Finding(
            kind=FindingKind.PARSE_ERROR,
            severity=Severity.ERROR,
            message=f"Syntax error: {e}",
            location=Location(module=qualified_name, line=e.lineno),
        )
    except Exception as e:
        return Finding(
            kind=FindingKind.PARSE_ERROR,
            severity=Severity.ERROR,
            message=f"Could not read/parse file: {e}",
            location=Location(module=qualified_name, line=None),
        )

    is_init = file_path.name == "__init__.py"
    visitor = ModuleVisitor(qualified_name, is_init)
    visitor.visit(tree)

    return Module(
        path=rel_path_str,
        qualified_name=qualified_name,
        classes=visitor.classes,
        functions=visitor.functions,
        imports=visitor.imports,
        has_main_block=visitor.has_main_block,
        string_literals=visitor.string_literals,
        referenced_names=visitor.referenced_names,
        exported_names=visitor.exported_names,
        variables=visitor.variables,
    )
