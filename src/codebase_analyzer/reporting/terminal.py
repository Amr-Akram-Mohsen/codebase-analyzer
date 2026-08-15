"""
Formats analysis results for terminal output.
"""

from codebase_analyzer.core.model import AnalysisResult, Finding, Severity


class _Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"


def format_terminal(result: AnalysisResult, use_color: bool = False) -> str:
    """
    Formats the analysis result into a human-readable string suitable for a terminal.
    
    Includes a summary, a list of modules, and all findings grouped by severity.
    Does not print; returns the formatted string.
    """
    lines = []
    
    def _c(text: str, color_code: str) -> str:
        if not use_color:
            return text
        return f"{color_code}{text}{_Color.RESET}"
        
    # Categorize findings
    errors = [f for f in result.findings if f.severity == Severity.ERROR]
    warnings = [f for f in result.findings if f.severity == Severity.WARNING]
    infos = [f for f in result.findings if f.severity == Severity.INFO]
    
    # Header & Summary
    lines.append(_c("Codebase Analyzer Report", _Color.BOLD))
    lines.append(f"Project: {result.project_root}")
    lines.append("-" * 40)
    lines.append(f"Modules parsed: {len(result.modules)}")
    
    # List modules
    if result.modules:
        pass # We intentionally do not list all modules to reduce noise
            
    # Findings Summary
    lines.append("")
    lines.append("-" * 40)
    lines.append(_c("Findings Summary:", _Color.BOLD))
    
    err_text = _c(f"Errors: {len(errors)}", _Color.RED if errors else _Color.RESET)
    warn_text = _c(f"Warnings: {len(warnings)}", _Color.YELLOW if warnings else _Color.RESET)
    info_text = _c(f"Infos: {len(infos)}", _Color.BLUE if infos else _Color.RESET)
    
    lines.append(f"  {err_text} | {warn_text} | {info_text}")
    
    # List findings
    if result.findings:
        lines.append("")
        lines.append(_c("Detailed Findings:", _Color.BOLD))
        
        def _format_finding(f: Finding, color: str) -> str:
            loc = ""
            # Omit the location prefix for NAME_COLLISION since the message already contains all locations
            if f.location and f.kind.name != "NAME_COLLISION":
                line_info = f":{f.location.line}" if f.location.line else ""
                loc = f" [{f.location.module}{line_info}]"
                
            kind = _c(f.kind.name, color)
            
            # Properly indent multiline messages to align under the bullet point
            msg_lines = f.message.split("\n")
            formatted_msg = msg_lines[0]
            if len(msg_lines) > 1:
                # Indent subsequent lines by 4 spaces
                formatted_msg += "\n" + "\n".join("    " + line for line in msg_lines[1:])
                
            return f"  - {kind}{loc}: {formatted_msg}"

        for f in errors:
            lines.append(_format_finding(f, _Color.RED))
        for f in warnings:
            lines.append(_format_finding(f, _Color.YELLOW))
        for f in infos:
            lines.append(_format_finding(f, _Color.BLUE))
            
    return "\n".join(lines)
