"""
Detects commented-out structural code (functions and classes).
"""

import ast
import textwrap
from pathlib import Path

from codebase_analyzer.core.model import Finding, FindingKind, Location, Module, Severity


def detect_commented_code(modules: list[Module], project_root: str) -> list[Finding]:
    """
    Scans raw source code of modules to detect contiguous blocks of comments
    that parse as valid Python AST containing FunctionDef or ClassDef.
    """
    findings = []
    
    for m in modules:
        path = Path(project_root) / m.path
        if not path.exists():
            continue
            
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
            
        i = 0
        while i < len(lines):
            line = lines[i].lstrip()
            if line.startswith("#"):
                start_line = i + 1
                comment_lines = []
                while i < len(lines) and lines[i].lstrip().startswith("#"):
                    # Extract the text after the first '#'
                    text_after_hash = lines[i].lstrip()[1:]
                    comment_lines.append(text_after_hash)
                    i += 1
                end_line = i
                
                block_text = textwrap.dedent("\n".join(comment_lines))
                
                try:
                    tree = ast.parse(block_text)
                    has_structural_code = False
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                            has_structural_code = True
                            break
                            
                    if has_structural_code:
                        findings.append(
                            Finding(
                                kind=FindingKind.COMMENTED_CODE,
                                severity=Severity.INFO,
                                message=f"Commented-out code detected (lines {start_line}-{end_line}).",
                                location=Location(module=m.qualified_name, line=start_line, end_line=end_line),
                            )
                        )
                except SyntaxError:
                    pass
            else:
                i += 1
                
    return findings
