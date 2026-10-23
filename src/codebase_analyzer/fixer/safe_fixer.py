"""
Applies targeted, deterministic fixes to the codebase.
"""

from pathlib import Path

from codebase_analyzer.core.model import AnalysisResult, FindingKind, FunctionDef, Module


def apply_safe_fixes(
    result: AnalysisResult,
    target_paths: list[str],
    delete_dead_code: bool = False,
) -> None:
    """
    Applies fixes to specific files or directories.
    1. Deletes exactly identical duplicate functions in the same file.
    2. Deletes detected commented-out structural code.
    3. Deletes orphaned dead code modules ONLY if delete_dead_code is True.
    """
    project_root = Path(result.project_root)
    resolved_targets = [Path(p).resolve() for p in target_paths]
    
    # Organize findings
    commented_findings: dict[str, list[tuple[int, int]]] = {}
    dead_code_modules: set[str] = set()
    
    for f in result.findings:
        if f.kind == FindingKind.COMMENTED_CODE and f.location and f.location.end_line is not None:
            if f.location.module not in commented_findings:
                commented_findings[f.location.module] = []
            commented_findings[f.location.module].append((f.location.line, f.location.end_line))
        elif f.kind == FindingKind.DEAD_CODE and f.location:
            dead_code_modules.add(f.location.module)

    for m in result.modules:
        file_path = (project_root / m.path).resolve()
        
        # Check if this module is targeted for fixing
        is_targeted = False
        for target in resolved_targets:
            try:
                # If file_path is relative to target, or equal
                file_path.relative_to(target)
                is_targeted = True
                break
            except ValueError:
                if file_path == target:
                    is_targeted = True
                    break
                    
        if not is_targeted:
            continue
            
        # 0. Delete Dead Code (Orphaned Modules) - ONLY if explicitly requested
        if delete_dead_code and m.qualified_name in dead_code_modules:
            try:
                file_path.unlink()
                print(f"Deleted dead code file: {m.path}")
            except OSError as e:
                print(f"Failed to delete {m.path}: {e}")
            continue
            
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
            
        lines_to_delete: set[int] = set()
        
        # 1. Delete Commented Code
        if m.qualified_name in commented_findings:
            for start, end in commented_findings[m.qualified_name]:
                # line numbers are 1-based
                for i in range(start - 1, end):
                    lines_to_delete.add(i)
                    
        # 2. Delete Identical Duplicate Functions
        # Helper to process a list of functions (m.functions contains scoped names for all funcs & methods)
        def process_functions(funcs: list[FunctionDef]):
            seen_funcs: dict[str, tuple[int, int, str]] = {}
            for fn in funcs:
                if fn.end_line_number is None:
                    continue
                start_idx = fn.line_number - 1
                end_idx = fn.end_line_number
                
                # Extract raw text
                raw_text = "\n".join(lines[start_idx:end_idx])
                
                if fn.name in seen_funcs:
                    prev_start, prev_end, prev_text = seen_funcs[fn.name]
                    if raw_text == prev_text:
                        # 100% Identical! Delete the duplicate.
                        for i in range(start_idx, end_idx):
                            lines_to_delete.add(i)
                        continue
                
                seen_funcs[fn.name] = (start_idx, end_idx, raw_text)

        process_functions(m.functions)
            
        if lines_to_delete:
            new_lines = []
            for i, line in enumerate(lines):
                if i not in lines_to_delete:
                    new_lines.append(line)
            file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            print(f"Fixed {len(lines_to_delete)} lines in {m.path}")
