"""
Command-line interface entry point.
"""

import argparse
import sys
from pathlib import Path

from codebase_analyzer.core.analyzer import analyze
from codebase_analyzer.core.model import AnalysisConfig, LayerRule, Severity
from codebase_analyzer.reporting.json_reporter import format_json
from codebase_analyzer.reporting.terminal import format_terminal


def main() -> int:
    """
    Parses arguments, configures the analysis, runs it, formats the output,
    and returns the appropriate exit code.
    """
    # Ensure stdout supports UTF-8 characters like ✖, ⚠, ℹ
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(
        description="Analyze Python codebases for structural and architectural findings."
    )
    parser.add_argument(
        "command",
        type=str,
        nargs="?",
        default="analyze",
        help="Command to run: 'analyze' (default), 'fix', or 'graph'",
    )
    parser.add_argument(
        "paths",
        type=str,
        nargs="+",
        help="Path(s) to the project directory to analyze, or files to fix/graph.",
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write output to file instead of stdout",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (TOML format)",
    )
    
    args = parser.parse_args()
    
    # If user ran `codebase-analyzer .`, command='.', paths=[]
    # Wait, because command is nargs="?", it might capture the path!
    # Let's fix argument parsing manually for backward compatibility.
    if args.command not in ["analyze", "fix", "graph"]:
        # The user just typed `codebase-analyzer path`
        args.paths.insert(0, args.command)
        args.command = "analyze"
        
    target_path = Path(args.paths[0])
    if not target_path.exists() or not target_path.is_dir():
        print(f"Error: Target path '{target_path}' does not exist or is not a directory.", file=sys.stderr)
        return 2
        
    config = AnalysisConfig(layer_rules=[])
    
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file '{args.config}' not found.", file=sys.stderr)
            return 2
            
        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
                
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
                
            tool_data = data.get("tool", {}).get("codebase-analyzer", {})
            layers_data = tool_data.get("layers", {})
            
            layer_rules = []
            for layer_name, prefixes in layers_data.items():
                if isinstance(prefixes, list):
                    layer_rules.append(LayerRule(name=layer_name, prefixes=prefixes))
                    
            encapsulation_data = tool_data.get("encapsulation", {})
            boundaries = encapsulation_data.get("boundaries", [])
            if not isinstance(boundaries, list):
                boundaries = []
                
            public_apis = encapsulation_data.get("public_apis", {})
            if not isinstance(public_apis, dict):
                public_apis = {}
                    
            dead_code_data = tool_data.get("dead_code", {})
            metrics_data = tool_data.get("metrics", {})
            
            max_fan_out = metrics_data.get("max_fan_out", 15)
            if not isinstance(max_fan_out, int):
                max_fan_out = 15
                
            max_complexity = metrics_data.get("max_complexity", 10)
            if not isinstance(max_complexity, int):
                max_complexity = 10
                    
            layer_rules = [LayerRule(name=n, prefixes=p) for n, p in layers_data.items() if isinstance(p, list)]
            
            config = AnalysisConfig(
                layer_rules=layer_rules, 
                encapsulation_boundaries=encapsulation_data.get("boundaries", []),
                encapsulation_public_apis=encapsulation_data.get("public_apis", {}),
                dead_code_entry_points=dead_code_data.get("entry_points", []),
                metrics_max_fan_out=max_fan_out,
                metrics_max_complexity=max_complexity
            )
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            return 2
    
    try:
        result = analyze(target_path, config)
        if args.command == "fix":
            from codebase_analyzer.fixer.safe_fixer import apply_safe_fixes
            apply_safe_fixes(result, args.paths)
            print("Auto-fixing complete. Re-running analysis...")
            # Re-run analysis to get clean output
            result = analyze(target_path, config)
        elif args.command == "graph":
            from codebase_analyzer.analysis.dependencies import build_dependency_graph
            graph = build_dependency_graph(result.modules)
            from codebase_analyzer.reporting.mermaid import generate_mermaid_diagram
            out_file = args.output if args.output else "architecture.md"
            generate_mermaid_diagram(result, graph, out_file)
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Internal error during analysis: {e}", file=sys.stderr)
        return 2
        
    use_color = sys.stdout.isatty() if not args.output else False
    
    if args.format == "json":
        output_text = format_json(result)
    else:
        output_text = format_terminal(result, use_color=use_color)
    
    if args.output:
        try:
            Path(args.output).write_text(output_text, encoding="utf-8")
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            return 2
    else:
        print(output_text)
        
    has_errors = any(f.severity == Severity.ERROR for f in result.findings)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
