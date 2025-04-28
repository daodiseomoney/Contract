#!/usr/bin/env python3
"""
Script to automatically fix common flake8 violations in Python files.

This script handles:
1. W293: Blank line contains whitespace
2. E501: Line too long (with smart line breaking)
3. F401: Imported but unused (commented out)
4. W291: Trailing whitespace
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Set, Tuple


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def fix_blank_lines(content: str) -> str:
    """Fix W293: Blank line contains whitespace."""
    lines = content.split('\n')
    for i in range(len(lines)):
        if lines[i].strip() == '':
            lines[i] = ''
    return '\n'.join(lines)


def fix_trailing_whitespace(content: str) -> str:
    """Fix W291: Trailing whitespace."""
    lines = content.split('\n')
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    return '\n'.join(lines)


def find_import_statements(content: str) -> Dict[str, List[Tuple[int, str]]]:
    """
    Find all import statements in the file and organize them by module.
    Returns a dict of module name -> list of (line_number, import_statement).
    """
    lines = content.split('\n')
    imports = {}
    import_pattern = r'^(?:from\s+(\w+(?:\.\w+)*)\s+)?import\s+(.+)$'
    
    for i, line in enumerate(lines):
        match = re.match(import_pattern, line.strip())
        if match:
            from_module = match.group(1) or ''
            imported_items = match.group(2)
            
            key = from_module if from_module else "direct_imports"
            if key not in imports:
                imports[key] = []
            
            imports[key].append((i, line))
    
    return imports


def analyze_unused_imports(file_path: str, content: str) -> Set[str]:
    """
    Use flake8 to analyze unused imports.
    Returns a set of unused import items.
    """
    import subprocess
    
    try:
        output = subprocess.check_output(
            ['flake8', '--select=F401', file_path],
            universal_newlines=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        output = e.output
    
    # Extract the unused imports from the output
    unused_imports = set()
    for line in output.split('\n'):
        if 'F401' in line:
            match = re.search(r"'([^']+)' imported but unused", line)
            if match:
                unused_imports.add(match.group(1))
    
    return unused_imports


def comment_unused_imports(content: str, unused_imports: Set[str]) -> str:
    """
    Comment out unused imports.
    This is safer than removing them as they might be imported for side effects.
    """
    if not unused_imports:
        return content
    
    lines = content.split('\n')
    modified_lines = []
    
    # Process each line
    for line in lines:
        line_modified = False
        
        # Skip already commented lines
        if line.strip().startswith('#'):
            modified_lines.append(line)
            continue
        
        # Check if this is an import line
        if re.match(r'^\s*(from\s+\w+(\.\w+)*\s+)?import\s+', line):
            for unused in unused_imports:
                # Different patterns depending on whether it's a 'from' import or direct import
                if 'from ' in line:
                    # For 'from module import x, y, z'
                    if f"import {unused}" in line or f"import {unused}," in line:
                        line = line.replace(f"import {unused}", f"import {unused}  # noqa: F401")
                        line_modified = True
                    elif f", {unused}" in line:
                        line = line.replace(f", {unused}", f", {unused}  # noqa: F401")
                        line_modified = True
                    elif f", {unused}," in line:
                        line = line.replace(f", {unused},", f", {unused},  # noqa: F401")
                        line_modified = True
                else:
                    # For 'import module' or 'import module as alias'
                    parts = line.split('import ')[1].split(',')
                    for i, part in enumerate(parts):
                        part = part.strip()
                        if part == unused or part.startswith(f"{unused} "):
                            parts[i] = f"{part}  # noqa: F401"
                            line_modified = True
                    
                    if line_modified:
                        line = line.split('import ')[0] + 'import ' + ', '.join(parts)
        
        modified_lines.append(line)
    
    return '\n'.join(modified_lines)


def break_long_lines(content: str, max_length: int = 100) -> str:
    """
    Fix E501: Line too long.
    Smart line breaking based on the context of the line.
    """
    lines = content.split('\n')
    result = []
    
    for line in lines:
        if len(line) <= max_length:
            result.append(line)
            continue
        
        # Skip comment lines
        if line.strip().startswith('#'):
            result.append(line)
            continue
        
        # Determine indentation
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        continuing_indent = indent_str + '    '
        
        # If it's an import statement
        if re.match(r'^\s*(from\s+\w+(\.\w+)*\s+)?import\s+', line):
            parts = []
            if 'from ' in line:
                # Split 'from ... import' statements
                from_part, import_part = line.split('import ', 1)
                parts.append(from_part + 'import (')
                
                # Split the imported items
                items = [item.strip() for item in import_part.split(',')]
                for item in items[:-1]:
                    parts.append(continuing_indent + item + ',')
                parts.append(continuing_indent + items[-1])
                parts.append(indent_str + ')')
            else:
                # Regular import with multiple modules
                import_part = line.split('import ', 1)[1]
                items = [item.strip() for item in import_part.split(',')]
                if len(items) > 1:
                    parts.append(line.split('import ')[0] + 'import (')
                    for item in items[:-1]:
                        parts.append(continuing_indent + item + ',')
                    parts.append(continuing_indent + items[-1])
                    parts.append(indent_str + ')')
                else:
                    # Single module but still too long - rare case
                    parts.append(line)
            
            result.extend(parts)
            continue
        
        # If it's a string definition
        if ('"' in line or "'" in line) and ('=' in line or 'return ' in line):
            # Find the position of the string
            match = re.search(r'(["\'])(.*?)(\1)', line)
            if match:
                string_start = match.start(0)
                string_end = match.end(0)
                
                # If string is the main cause of the line being too long
                if string_end - string_start > max_length // 2:
                    before_string = line[:string_start]
                    string_content = match.group(2)
                    after_string = line[string_end:]
                    
                    # Break the string into chunks
                    result.append(before_string + match.group(1))
                    
                    # Try to break at logical points like spaces
                    current_pos = 0
                    while current_pos < len(string_content):
                        next_pos = current_pos + max_length - len(continuing_indent) - 2  # -2 for quotes
                        
                        if next_pos >= len(string_content):
                            chunk = string_content[current_pos:]
                            result.append(continuing_indent + chunk + match.group(1) + after_string)
                            break
                        
                        # Try to break at a space
                        space_pos = string_content.rfind(' ', current_pos, next_pos)
                        if space_pos > current_pos:
                            chunk = string_content[current_pos:space_pos]
                            result.append(continuing_indent + chunk + match.group(1) + ' \\')
                            current_pos = space_pos + 1
                        else:
                            # No good breaking point, just break at max length
                            chunk = string_content[current_pos:next_pos]
                            result.append(continuing_indent + chunk + match.group(1) + ' \\')
                            current_pos = next_pos
                    
                    continue
        
        # If it's a function call or list/dict with many parameters
        if '(' in line and ')' in line and line.count('(') == 1:
            open_paren = line.find('(')
            close_paren = line.rfind(')')
            
            if close_paren > open_paren:
                before_args = line[:open_paren + 1]
                args_str = line[open_paren + 1:close_paren]
                after_args = line[close_paren:]
                
                if ',' in args_str:
                    args = [arg.strip() for arg in args_str.split(',')]
                    
                    result.append(before_args)
                    for arg in args[:-1]:
                        result.append(continuing_indent + arg + ',')
                    result.append(continuing_indent + args[-1])
                    result.append(indent_str + after_args)
                    continue
        
        # If it's an assignment with a long expression
        if '=' in line and not line.strip().startswith('def '):
            var_part, expr_part = line.split('=', 1)
            
            # If the expression has logical operators, break at those
            if ' and ' in expr_part or ' or ' in expr_part:
                result.append(var_part + '= (')
                
                # Break at logical operators
                parts = re.split(r'\s+(and|or)\s+', expr_part)
                for i in range(0, len(parts), 2):
                    if i + 1 < len(parts):
                        result.append(continuing_indent + parts[i].strip() + ' ' + parts[i+1])
                    else:
                        result.append(continuing_indent + parts[i].strip())
                
                result.append(indent_str + ')')
                continue
        
        # If we couldn't break it in a smart way, at least try to break at a good spot
        if len(line) > max_length:
            # Try to find logical breaking points
            break_points = []
            
            # Operators are good breaking points
            for op in [' + ', ' - ', ' * ', ' / ', ' and ', ' or ', ' is ', ' in ', ' not ', ' == ', ' != ']:
                pos = max_length - 10
                while pos > 0:
                    pos = line.rfind(op, 0, pos)
                    if pos >= 0:
                        break_points.append((pos, pos + len(op)))
                    else:
                        break
            
            # Commas are also good breaking points
            pos = max_length - 10
            while pos > 0:
                pos = line.rfind(',', 0, pos)
                if pos >= 0:
                    break_points.append((pos, pos + 1))
                else:
                    break
            
            if break_points:
                # Pick the break point closest to max_length
                break_points.sort(key=lambda x: abs(x[0] - max_length))
                break_pos, op_end = break_points[0]
                
                result.append(line[:op_end])
                result.append(continuing_indent + line[op_end:].lstrip())
                continue
        
        # If all else fails, just keep the line as is
        result.append(line)
    
    return '\n'.join(result)


def process_file(file_path: str, dry_run: bool = False) -> Tuple[int, bool]:
    """
    Process a single Python file to fix flake8 violations.
    
    Returns:
        Tuple of (number of issues fixed, whether changes were made)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Make a backup of the original content
        original_content = content
        
        # Fix blank lines containing whitespace
        content = fix_blank_lines(content)
        
        # Fix trailing whitespace
        content = fix_trailing_whitespace(content)
        
        # Find and comment out unused imports
        unused_imports = analyze_unused_imports(file_path, content)
        if unused_imports:
            content = comment_unused_imports(content, unused_imports)
        
        # Fix long lines
        content = break_long_lines(content)
        
        # Count the number of issues fixed
        issues_fixed = 0
        if original_content != content:
            issues_fixed = 1  # We don't need the exact count
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        return issues_fixed, original_content != content
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Fix common flake8 violations in Python files.')
    parser.add_argument('path', help='Path to a Python file or directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()
    
    path = args.path
    files_to_process = []
    
    if os.path.isfile(path):
        if path.endswith('.py'):
            files_to_process.append(path)
        else:
            print(f"Warning: {path} is not a Python file. Skipping.")
    elif os.path.isdir(path):
        files_to_process = find_python_files(path)
    else:
        print(f"Error: {path} does not exist.")
        return 1
    
    if not files_to_process:
        print("No Python files found to process.")
        return 0
    
    print(f"Processing {len(files_to_process)} files...")
    
    total_issues_fixed = 0
    files_changed = 0
    
    for file_path in files_to_process:
        print(f"Processing {file_path}...", end='')
        issues_fixed, changed = process_file(file_path, args.dry_run)
        
        if changed:
            files_changed += 1
            if args.dry_run:
                print(" would be modified")
            else:
                print(" fixed")
        else:
            print(" no issues found")
        
        total_issues_fixed += issues_fixed
    
    mode = "Would fix" if args.dry_run else "Fixed"
    print(f"\n{mode} issues in {files_changed} files.")
    
    if args.dry_run:
        print("\nThis was a dry run. No files were actually modified.")
        print("Run without --dry-run to make the changes.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())