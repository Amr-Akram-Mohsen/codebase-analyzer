"""
Formats analysis results for terminal output using rich.
"""

import os
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.text import Text

from codebase_analyzer.core.model import AnalysisResult, Finding, Severity


def format_terminal(result: AnalysisResult, use_color: bool = False) -> str:
    """
    Formats the analysis result into a human-readable string suitable for a terminal.
    
    Includes a summary and a file-first tabular list of findings.
    Does not print; returns the formatted string.
    """
    console = Console(color_system="auto" if use_color else None, width=120, force_terminal=use_color)
    
    with console.capture() as capture:
        # Categorize findings
        errors = [f for f in result.findings if f.severity == Severity.ERROR]
        warnings = [f for f in result.findings if f.severity == Severity.WARNING]
        infos = [f for f in result.findings if f.severity == Severity.INFO]
        
        # Header
        console.print(Text("Codebase Analyzer Report", style="bold"))
        console.print(f"Project: {result.project_root}")
        console.print("-" * 50)
        console.print()
        
        if not result.findings:
            console.print("[red]✖ 0 Errors[/] | [yellow]⚠ 0 Warnings[/] | [blue]ℹ 0 Infos[/]")
        else:
            # Build lookup table for module paths
            root = Path(result.project_root)
            module_paths = {m.qualified_name: str(root / m.path) for m in result.modules}
            
            # Group findings by file
            findings_by_file: dict[str, list[Finding]] = defaultdict(list)
            
            for f in result.findings:
                file_path = "<Global>"
                if f.location:
                    abs_path_str = module_paths.get(f.location.module)
                    if abs_path_str:
                        try:
                            file_path = os.path.relpath(abs_path_str, start=result.project_root)
                        except ValueError:
                            file_path = abs_path_str
                    else:
                        file_path = f.location.module # Fallback to module name if not found
                findings_by_file[file_path].append(f)
                
            for file_path in sorted(findings_by_file.keys()):
                file_findings = findings_by_file[file_path]
                
                # Sort findings by line number (None -> 0)
                file_findings.sort(key=lambda f: f.location.line if f.location and f.location.line is not None else 0)
                
                console.print(Text(file_path, style="cyan"))
                
                table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2))
                
                for f in file_findings:
                    # Line col
                    if f.location and f.location.line is not None:
                        line_col = str(f.location.line)
                        lc_text = Text(line_col)
                    else:
                        line_col = "--"
                        lc_text = Text(line_col, style="dim")
                    
                    # Severity
                    sev = f.severity.name.lower()
                    if f.severity == Severity.ERROR:
                        sev_text = Text(sev, style="red")
                    elif f.severity == Severity.WARNING:
                        sev_text = Text(sev, style="yellow")
                    else:
                        sev_text = Text(sev, style="blue")
                        
                    msg_text = Text(f.message.split("\n")[0])
                    kind_text = Text(f.kind.name, style="dim")
                    
                    table.add_row(lc_text, sev_text, msg_text, kind_text)
                    
                console.print(table)
                console.print() # Empty line between files
                
            # Summary at the bottom
            console.print("-" * 50)
            
            err_sym = "[red]✖[/]" if errors else "✖"
            warn_sym = "[yellow]⚠[/]" if warnings else "⚠"
            info_sym = "[blue]ℹ[/]" if infos else "ℹ"
            
            console.print(f"{err_sym} {len(errors)} Errors | {warn_sym} {len(warnings)} Warnings | {info_sym} {len(infos)} Infos")
            
    return capture.get().rstrip("\n") # Remove trailing newline from capture
