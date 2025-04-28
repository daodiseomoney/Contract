#!/usr/bin/env python3
"""
Script to automatically fix common flake8 issues in IfcOpenShell files.
This script specifically focuses on:
1. E302 - Adding proper blank lines between top-level definitions
2. E501 - Breaking long lines to meet PEP 8 line length limit
"""

import os
import re
import sys
from typing import List, Tuple


def fix_blank_lines(content: str) -> str:
    """Fix E302 issues by ensuring 2 blank lines between top-level definitions."""
    # Pattern to match top-level function/class definitions
    pattern = r'(\n)(?=[^\s#])'
    
    # Replace single newlines before top-level definitions with double newlines
    fixed_content = re.sub(pattern, '\n\n', content)
    
    return fixed_content


def fix_long_lines(content: str, max_length: int = 100) -> str:
    """
    Fix E501 issues by breaking long lines.
    This is a simplified approach and may need manual review for complex cases.
    """
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) <= max_length:
            fixed_lines.append(line)
            continue
        
        # Skip comment lines - these need manual attention
        if line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Handle long strings by breaking them with concatenation
        if '"' in line or "'" in line:
            fixed_lines.extend(break_string_line(line, max_length))
            continue
        
        # Handle long lines with function calls or expressions
        if '(' in line:
            fixed_lines.extend(break_function_line(line, max_length))
            continue
        
        # If we can't automatically fix, keep as is
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def break_string_line(line: str, max_length: int) -> List[str]:
    """Break a long line containing strings into multiple lines."""
    # This is a simplified approach - real implementation would need more context
    indent = len(line) - len(line.lstrip())
    indent_str = ' ' * indent
    
    # Find the string boundaries
    match = re.search(r'(["\'])(.*?)(\1)', line)
    if not match:
        return [line]  # Can't identify the string
    
    string_content = match.group(2)
    # If string is short, some other part is making the line long
    if len(string_content) < max_length // 2:
        return [line]
    
    # Break the string into chunks
    parts = []
    current_part = line[:match.start(2)]
    for i, char in enumerate(string_content):
        current_part += char
        # Break at logical points if line would be too long
        if len(current_part) > max_length - 5:  # Leave room for quotes and continuation
            parts.append(current_part + '"')
            current_part = indent_str + '"'
    
    # Add the remaining part
    if current_part and not current_part.endswith('"'):
        current_part += match.group(3)
        if match.end(3) < len(line):
            current_part += line[match.end(3):]
        parts.append(current_part)
    
    return parts


def break_function_line(line: str, max_length: int) -> List[str]:
    """Break a long line containing function calls into multiple lines."""
    indent = len(line) - len(line.lstrip())
    indent_str = ' ' * indent
    
    # Find a good place to break (after a comma)
    if ',' not in line:
        return [line]
    
    parts = []
    current_part = line
    
    while len(current_part) > max_length:
        # Find the last comma before max_length
        last_comma_idx = current_part[:max_length].rfind(',')
        
        if last_comma_idx == -1:
            # No good place to break found
            break
        
        # Break after the comma
        parts.append(current_part[:last_comma_idx + 1])
        current_part = indent_str + '    ' + current_part[last_comma_idx + 1:].lstrip()
    
    if current_part:
        parts.append(current_part)
    
    return parts


def process_file(filepath: str) -> Tuple[int, int]:
    """
    Process a file to fix flake8 issues.
    
    Returns:
        Tuple of (blank_line_fixes, long_line_fixes)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count issues before fixing
        blank_line_issues = len(re.findall(r'(\n)(?=[^\s#])', content))
        long_line_issues = sum(1 for line in content.split('\n') if len(line) > 100)
        
        # Fix issues
        fixed_content = fix_blank_lines(content)
        fixed_content = fix_long_lines(fixed_content)
        
        # Write back the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return blank_line_issues, long_line_issues
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0, 0


def main():
    """Main function to find and fix flake8 issues."""
    if len(sys.argv) < 2:
        print("Usage: python fix_flake8_issues.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    total_blank_line_fixes = 0
    total_long_line_fixes = 0
    
    if os.path.isfile(target):
        blank_line_fixes, long_line_fixes = process_file(target)
        total_blank_line_fixes += blank_line_fixes
        total_long_line_fixes += long_line_fixes
        print(f"Processed {target}: {blank_line_fixes} blank line issues, {long_line_fixes} long line issues")
    
    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    blank_line_fixes, long_line_fixes = process_file(filepath)
                    total_blank_line_fixes += blank_line_fixes
                    total_long_line_fixes += long_line_fixes
                    print(f"Processed {filepath}: {blank_line_fixes} blank line issues, {long_line_fixes} long line issues")
    
    else:
        print(f"Error: {target} not found.")
        sys.exit(1)
    
    print(f"\nSummary: Fixed {total_blank_line_fixes} blank line issues and {total_long_line_fixes} long line issues.")


if __name__ == "__main__":
    main()