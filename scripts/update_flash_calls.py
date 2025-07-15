#!/usr/bin/env python3
"""
Script to update all flash_tab calls in zwaifu_launcher_gui.py
This script adds proper error handling to flash_tab calls.
"""

import re
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_flash_calls():
    """Update flash_tab calls with proper error handling"""
    
    # Path to the main launcher file (in parent directory)
    launcher_file = os.path.join(os.path.dirname(__file__), '..', 'zwaifu_launcher_gui.py')
    
    if not os.path.exists(launcher_file):
        print(f"Error: Launcher file not found at {launcher_file}")
        return False
    
    print(f"Updating flash calls in: {launcher_file}")
    
    # Read the file
    with open(launcher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all flash_tab calls and add error handling
    pattern = r'(self\.flash_tab\([^)]+\))'
    
    def add_error_handling(match):
        call = match.group(1)
        return f"try:\n                {call}\nexcept Exception as e:\n                self.log(f'Failed to flash tab: {{e}}')"
    
    updated_content = re.sub(pattern, add_error_handling, content)
    
    # Write back to file
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Flash calls updated successfully!")
    return True

if __name__ == "__main__":
    update_flash_calls() 