#!/usr/bin/env python3
"""
Script to specifically fix flake8 issues in IFC4X3_ADD1.py file.
This script addresses the exact issues seen in the flake8 report:
1. E302: Expected 2 blank lines, found 1
2. E501: Lines too long (exceeding 100 characters)
"""

import os
import re
import sys


def find_ifc_file():
    """Find the path to IFC4X3_ADD1.py file."""
    # Try to find in the cache directory first
    for root, _, files in os.walk('./.cache'):
        for file in files:
            if file == 'IFC4X3_ADD1.py':
                return os.path.join(root, file)
    
    # If not found, scan the entire directory
    for root, _, files in os.walk('.'):
        for file in files:
            if file == 'IFC4X3_ADD1.py':
                return os.path.join(root, file)
    
    return None


def fix_blank_lines(content):
    """Fix E302 errors: expected 2 blank lines, found 1."""
    lines = content.split('\n')
    result = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Check if this is a line that needs proper spacing before the next definition
        if (line.strip() and not line.startswith(' ') and not line.startswith('#') and
            i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith(' ')):
            
            # Add proper blank lines
            result.append('')
            result.append('')
            i += 1  # Skip the existing blank line if there is one
        
        i += 1
    
    return '\n'.join(result)


def fix_long_lines(content):
    """Fix E501 errors: line too long."""
    lines = content.split('\n')
    result = []
    
    for line in lines:
        if len(line) <= 100:
            result.append(line)
            continue
        
        # Skip comments - these require manual intervention
        if line.strip().startswith('#'):
            result.append(line)
            continue
        
        # For IFC rules files, long lines are often either:
        # 1. Parameter lists in function definitions
        # 2. String constants
        # 3. Complex expressions
        
        # Check if it's a parameter list
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        
        if '(' in line and ')' in line:
            parts = break_parameter_list(line, indent_str)
            result.extend(parts)
        elif '"' in line or "'" in line:
            parts = break_string(line, indent_str)
            result.extend(parts)
        else:
            # For other types of long lines, we'll just insert a logical break
            # at an operator if possible
            operators = ['+', '-', '*', '/', '=', ' and ', ' or ', ',']
            best_op = None
            best_pos = -1
            
            for op in operators:
                pos = line.rfind(op, 0, 100)
                if pos > best_pos:
                    best_pos = pos
                    best_op = op
            
            if best_pos > 0:
                result.append(line[:best_pos + len(best_op)])
                result.append(indent_str + '    ' + line[best_pos + len(best_op):].lstrip())
            else:
                # If no good breaking point, keep as is
                result.append(line)
    
    return '\n'.join(result)


def break_parameter_list(line, indent_str):
    """Break a long parameter list into multiple lines."""
    # Find the opening and closing parentheses
    open_paren = line.find('(')
    close_paren = line.rfind(')')
    
    if open_paren == -1 or close_paren == -1:
        return [line]
    
    # Extract the parameter list
    params_str = line[open_paren + 1:close_paren]
    params = [p.strip() for p in params_str.split(',')]
    
    if len(params) <= 1:
        return [line]
    
    # Reconstruct with parameters on separate lines
    result = [line[:open_paren] + '(']
    for i, param in enumerate(params):
        if i < len(params) - 1:
            result.append(indent_str + '    ' + param + ',')
        else:
            result.append(indent_str + '    ' + param)
    
    result.append(indent_str + ')' + line[close_paren + 1:])
    return result


def break_string(line, indent_str):
    """Break a long string into multiple concatenated strings."""
    # Find string boundaries
    matches = list(re.finditer(r'(["\'])(.*?)(\1)', line))
    if not matches:
        return [line]
    
    # Pick the longest string to break
    longest_match = max(matches, key=lambda m: len(m.group(2)))
    
    # Break the string
    before = line[:longest_match.start()]
    string_content = longest_match.group(2)
    after = line[longest_match.end():]
    
    # If the string isn't that long, look for other breaking points
    if len(string_content) < 50:
        return [line]
    
    # Break into chunks of appropriate length
    chunks = []
    current_chunk = ""
    words = string_content.split()
    
    for word in words:
        if len(current_chunk) + len(word) + 1 > 80:  # Leave some margin
            chunks.append(current_chunk)
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Reconstruct with concatenated strings
    result = []
    result.append(before + longest_match.group(1) + chunks[0] + longest_match.group(1))
    
    for chunk in chunks[1:]:
        result.append(indent_str + '    + ' + longest_match.group(1) + chunk + longest_match.group(1))
    
    # Add the remainder of the line to the last part
    if after:
        result[-1] += after
    
    return result


def main():
    """Main function to find and fix the IFC4X3_ADD1.py file."""
    ifc_file = find_ifc_file()
    if not ifc_file:
        print("Error: Could not find IFC4X3_ADD1.py file.")
        return
    
    print(f"Found file: {ifc_file}")
    
    # Read the file
    with open(ifc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Make a backup
    backup_file = ifc_file + '.bak'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created backup at: {backup_file}")
    
    # Fix the issues
    fixed_content = fix_blank_lines(content)
    fixed_content = fix_long_lines(fixed_content)
    
    # Write the fixed content back
    with open(ifc_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed flake8 issues in {ifc_file}")
    print("You should run flake8 again to verify the fixes.")


if __name__ == "__main__":
    main()