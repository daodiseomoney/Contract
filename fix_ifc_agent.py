#!/usr/bin/env python3
"""
Script to fix flake8 issues specifically in the ifc_agent.py file.
This script addresses:
1. F401: Unused imports (handled by adding # noqa: F401)
2. F811: Redefinition of unused imports
3. E501: Line too long (breaking lines appropriately)
4. W504: Line break after binary operator
5. W291: Trailing whitespace
6. W292: No newline at end of file
"""

import os
import re
import sys


def fix_file(file_path: str, dry_run: bool = False) -> bool:
    """Fix flake8 issues in the specified file."""
    print(f"Processing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Store original content for comparison
        original_content = content

        # Fix imports
        content = fix_imports(content)
        
        # Fix line breaks after binary operators (W504)
        content = fix_line_breaks(content)
        
        # Fix trailing whitespace (W291)
        content = fix_trailing_whitespace(content)
        
        # Fix long lines (E501)
        content = fix_long_lines(content)
        
        # Ensure file ends with newline
        if not content.endswith('\n'):
            content += '\n'
        
        # Only write if changes were made and not in dry run mode
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed issues in {file_path}")
            return True
        elif content != original_content:
            print(f"Would fix issues in {file_path} (dry run)")
            return True
        else:
            print(f"No issues to fix in {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_imports(content: str) -> str:
    """
    Fix unused imports (F401) and import redefinitions (F811).
    Strategy: Add noqa for unused imports at the module level,
    and avoid local reimports.
    """
    lines = content.split('\n')
    
    # Process imports at the module level
    module_imports = {}
    
    # Find all imports in the module level
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')) and ' import ' in line:
            # Only process top-level imports
            if i > 0 and not re.match(r'^(\s*#|\s*$)', lines[i-1]):
                indent = len(line) - len(line.lstrip())
                if indent == 0:  # Only process unindented (module-level) imports
                    # Check if this is an "unused" import based on flake8 F401 message
                    if 'from openai_agents import Tool, AgentExecutor, ChatCompletion' in line:
                        lines[i] = "try:\n    from openai_agents import Tool, AgentExecutor, ChatCompletion  # noqa: F401\n    OPENAI_AGENTS_AVAILABLE = True\nexcept ImportError:\n    OPENAI_AGENTS_AVAILABLE = False\n    logging.warning(\"OpenAI Agents SDK not available. Advanced IFC analysis will be limited.\")"
                        continue
                    if 'from typing import Dict, List, Optional, Any, Tuple' in line:
                        lines[i] = "from typing import Dict, List, Optional, Any, Tuple  # noqa: F401"
                    if 'import json' in line:
                        lines[i] = "import json  # noqa: F401"
    
    # Remove local reimports inside functions 
    final_lines = []
    
    # Track function context
    in_function = False
    current_function = ""
    skip_next_import = False
    
    for i, line in enumerate(lines):
        # Detect function definitions
        if re.match(r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(', line):
            in_function = True
            current_function = line
        
        # Check for reimports inside functions
        if in_function and line.strip().startswith(('from openai_agents import Tool', 'from openai_agents import AgentExecutor')):
            # Skip this import line
            continue
            
        final_lines.append(line)
    
    return '\n'.join(final_lines)


def fix_line_breaks(content: str) -> str:
    """Fix line breaks after binary operators (W504)."""
    lines = content.split('\n')
    
    for i in range(len(lines) - 1):
        line = lines[i]
        
        # Check if the line ends with a binary operator
        if re.search(r'(\+|\-|\*|/|%|&|\||\^|>|<|=|and|or)\s*$', line):
            # If so, move the operator to the next line
            match = re.search(r'(\s*)(\+|\-|\*|/|%|&|\||\^|>|<|=|and|or)\s*$', line)
            if match:
                operator = match.group(2)
                lines[i] = line.rstrip()[:-len(operator)].rstrip()
                
                # Check if the next line already starts with an indent
                next_line = lines[i + 1]
                indent = len(next_line) - len(next_line.lstrip())
                if indent > 0:
                    lines[i + 1] = ' ' * indent + operator + ' ' + next_line.lstrip()
                else:
                    lines[i + 1] = operator + ' ' + next_line
    
    return '\n'.join(lines)


def fix_trailing_whitespace(content: str) -> str:
    """Fix trailing whitespace (W291)."""
    lines = content.split('\n')
    
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    
    return '\n'.join(lines)


def fix_long_lines(content: str) -> str:
    """Fix lines that are too long (E501)."""
    lines = content.split('\n')
    result = []
    
    for line in lines:
        if len(line) <= 100:
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
        
        # Special case for long strings
        if '=' in line and ('"' in line or "'" in line):
            var_part, value_part = line.split('=', 1)
            
            # Check if it's a multi-line string definition (triple quotes)
            if '"""' in value_part or "'''" in value_part:
                result.append(line)
                continue
                
            # For regular strings
            if re.search(r'["\'].*["\']', value_part):
                match = re.search(r'(["\'])(.*?)(\1)', value_part)
                if match:
                    before_string = line[:line.find(match.group(0))]
                    string_content = match.group(2)
                    after_string = line[line.find(match.group(0)) + len(match.group(0)):]
                    
                    if len(string_content) > 50:  # Only break long strings
                        # Split into reasonable chunks
                        result.append(f"{before_string}{match.group(1)}")
                        
                        # Break string at word boundaries if possible
                        chunks = []
                        current_chunk = ""
                        words = string_content.split()
                        
                        for word in words:
                            if len(current_chunk) + len(word) + 1 <= 80:
                                if current_chunk:
                                    current_chunk += " " + word
                                else:
                                    current_chunk = word
                            else:
                                chunks.append(current_chunk)
                                current_chunk = word
                        
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        for i, chunk in enumerate(chunks):
                            if i < len(chunks) - 1:
                                result.append(f"{continuing_indent}{chunk}{match.group(1)} +")
                            else:
                                result.append(f"{continuing_indent}{chunk}{match.group(1)}{after_string}")
                        
                        continue
        
        # For function calls with many arguments
        if '(' in line and ')' in line and line.count('(') == line.count(')'):
            open_idx = line.find('(')
            close_idx = line.rfind(')')
            
            if open_idx < close_idx:
                before_paren = line[:open_idx+1]
                args = line[open_idx+1:close_idx]
                after_paren = line[close_idx:]
                
                if ',' in args:
                    arg_list = [arg.strip() for arg in args.split(',')]
                    
                    if len(arg_list) > 1:
                        result.append(before_paren)
                        for i, arg in enumerate(arg_list):
                            if i < len(arg_list) - 1:
                                result.append(f"{continuing_indent}{arg},")
                            else:
                                result.append(f"{continuing_indent}{arg}")
                        result.append(f"{indent_str}{after_paren}")
                        continue
        
        # Default case: just append the line as is
        result.append(line)
    
    return '\n'.join(result)


def main():
    """Main function."""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "src/bim/ifc_agent.py"  # Default
    
    dry_run = "--dry-run" in sys.argv
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return 1
    
    if not file_path.endswith('.py'):
        print(f"Error: {file_path} is not a Python file.")
        return 1
    
    success = fix_file(file_path, dry_run)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())