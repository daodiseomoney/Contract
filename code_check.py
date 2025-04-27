#!/usr/bin/env python
"""
Code quality checker script for the Daodiseo Real Estate Tokenization Platform.
This script runs flake8 with a user-friendly output format.
"""

import os
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def run_flake8(path: Optional[str] = None) -> Tuple[int, str]:
    """Run flake8 and return exit code and output."""
    cmd = ["flake8", "--statistics", "--count"]
    if path:
        cmd.append(path)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def parse_flake8_output(output: str) -> Dict[str, List[Dict]]:
    """Parse flake8 output and group by file."""
    issues_by_file = defaultdict(list)
    for line in output.strip().split("\n"):
        if ":" not in line or line.strip() == "":
            continue
        
        try:
            parts = line.split(":", 3)
            if len(parts) < 3:
                continue
                
            filepath = parts[0]
            line_num = parts[1]
            rest = parts[2].strip()
            
            code = None
            message = rest
            
            # Extract error code if present
            if " " in rest:
                code_part, message = rest.split(" ", 1)
                if len(code_part) <= 5:  # Code like E501, W123
                    code = code_part
            
            issues_by_file[filepath].append({
                "line": line_num,
                "code": code,
                "message": message
            })
        except Exception:
            # Skip lines that don't match the expected format
            continue
    
    return issues_by_file


def display_issues(issues_by_file: Dict[str, List[Dict]]) -> None:
    """Display issues in a user-friendly format."""
    total_issues = sum(len(issues) for issues in issues_by_file.values())
    
    # Print header
    print("\n" + "=" * 80)
    print(f"FOUND {total_issues} ISSUES IN {len(issues_by_file)} FILES".center(80))
    print("=" * 80)
    
    # Group error codes
    error_counts = defaultdict(int)
    for issues in issues_by_file.values():
        for issue in issues:
            if issue["code"]:
                error_counts[issue["code"]] += 1
    
    # Print summary of error types
    if error_counts:
        print("\nERROR TYPES:")
        for code, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {code}: {count} occurrences")
    
    # Print issues by file
    for filepath, issues in sorted(issues_by_file.items()):
        if not issues:
            continue
            
        print(f"\n\n{filepath}")
        print("-" * len(filepath))
        
        for issue in sorted(issues, key=lambda x: int(x["line"])):
            line_num = issue["line"]
            code = issue["code"] or "???"
            message = issue["message"]
            print(f"  Line {line_num}: [{code}] {message}")


def main():
    """Main entry point."""
    # Check if a path argument was provided
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
        print(f"Running code quality check on: {path}")
    else:
        print("Running code quality check on the entire project...")
        print("Tip: To check a specific file or directory, use: python code_check.py <path>")
    
    exit_code, output = run_flake8(path)
    
    if exit_code == 0:
        print("\n✅ No issues found! Your code looks great!")
        return 0
    
    issues_by_file = parse_flake8_output(output)
    display_issues(issues_by_file)
    
    print("\n\nTo run this check again, use: python code_check.py")
    print("For a specific file: python code_check.py src/bim/bim_agent_openai.py")
    print("For detailed help on fixing these issues, see: https://flake8.pycqa.org/en/latest/")
    return 1


if __name__ == "__main__":
    sys.exit(main())