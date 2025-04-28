#!/usr/bin/env python3
"""
Pre-commit hook to check for flake8 issues.
Install this by copying to .git/hooks/pre-commit and making it executable.
"""

import os
import subprocess
import sys


def main():
    """Run flake8 on all staged Python files."""
    # Get list of staged files
    try:
        staged_files_output = subprocess.check_output(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
            universal_newlines=True
        )
    except subprocess.CalledProcessError:
        print("Error: Failed to get list of staged files")
        return 1
    
    staged_files = [f for f in staged_files_output.split('\n') if f.endswith('.py')]
    
    if not staged_files:
        print("No Python files to check")
        return 0
    
    # Check if flake8 is installed
    try:
        subprocess.check_call(['flake8', '--version'], stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: flake8 is not installed or not working")
        print("Please install flake8: pip install flake8")
        return 1
    
    # Run flake8 on staged files
    error_count = 0
    for file_path in staged_files:
        if not os.path.exists(file_path):
            continue
        
        print(f"Checking {file_path}...")
        try:
            output = subprocess.check_output(
                ['flake8', file_path],
                universal_newlines=True,
                stderr=subprocess.STDOUT
            )
            if output:
                print(output)
                error_count += 1
        except subprocess.CalledProcessError as e:
            print(e.output)
            error_count += 1
    
    if error_count > 0:
        print("\nFlake8 found issues in your code. Please fix them before committing.")
        print("You can run one of these scripts to automatically fix some issues:")
        print("  - python fix_flake8_issues.py <file_or_directory>")
        print("  - python fix_ifc4x3_add1.py  # For IFC-specific fixes")
        return 1
    
    print("All Python files passed flake8 checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())