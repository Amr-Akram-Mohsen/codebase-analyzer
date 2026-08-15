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
)


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
    
    # If the current file is not an __init__.py, the first dot resolves to its package
    # (i.e. we drop the module's own name). If it is an __init__.py, it represents the package itself.
    if not is_init and parts:
        parts.pop()
        
    # Apply higher level dots (e.g. '..' removes one more package level)
    for _ in range(level - 1):
        if parts:
            parts.pop()
        else:
            # Attempting to import beyond top-level package
            break
            
    base = ".".join(parts)
    if base and module:
        return f"{base}.{module}"
    elif base:
        return base
    return module or ""


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

    classes: list[ClassDef] = []
    functions: list[FunctionDef] = []
    imports: list[ImportRef] = []
    
    is_init = file_path.name == "__init__.py"

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(
                        FunctionDef(
                            name=item.name,
                            line_number=item.lineno,
                            end_line_number=getattr(item, "end_lineno", None),
                        )
                    )
            classes.append(
                ClassDef(
                    name=node.name,
                    line_number=node.lineno,
                    methods=methods,
                    end_line_number=getattr(node, "end_lineno", None),
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(
                FunctionDef(
                    name=node.name,
                    line_number=node.lineno,
                    end_line_number=getattr(node, "end_lineno", None),
                )
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    ImportRef(
                        source_module=qualified_name,
                        target_module=alias.name,
                        line_number=node.lineno,
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            level = node.level
            module = node.module
            
            if level > 0:
                base_module = _resolve_relative_import(level, module, qualified_name, is_init)
            else:
                base_module = module or ""
                
            for alias in node.names:
                if base_module:
                    target_module = f"{base_module}.{alias.name}"
                else:
                    target_module = alias.name
                    
                imports.append(
                    ImportRef(
                        source_module=qualified_name,
                        target_module=target_module,
                        line_number=node.lineno,
                    )
                )

    return Module(
        path=rel_path_str,
        qualified_name=qualified_name,
        classes=classes,
        functions=functions,
        imports=imports,
    )
