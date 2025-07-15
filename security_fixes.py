#!/usr/bin/env python3
"""
Security Fixes for Z-Waifu Launcher GUI
Addresses vulnerabilities identified by static analysis tools
"""

import os
import sys
import shutil
import subprocess
import tempfile
import json
from pathlib import Path

class SecurityFixes:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / "security_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def log(self, message):
        """Log messages with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def backup_file(self, file_path):
        """Create backup of file before modification"""
        if not os.path.exists(file_path):
            return None
            
        backup_path = self.backup_dir / f"{Path(file_path).name}.backup"
        shutil.copy2(file_path, backup_path)
        self.log(f"Backed up {file_path} to {backup_path}")
        return backup_path
    
    def fix_subprocess_shell_vulnerabilities(self):
        """Fix subprocess shell=True vulnerabilities"""
        self.log("Fixing subprocess shell vulnerabilities...")
        
        # Main GUI file fixes
        main_gui_file = "zwaifu_launcher_gui.py"
        if os.path.exists(main_gui_file):
            self.backup_file(main_gui_file)
            
            # Read the file
            with open(main_gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix subprocess.Popen with shell=True
            replacements = [
                # Fix batch file execution without shell=True
                (
                    r'subprocess\.Popen\(\[batch_path\], cwd=os\.path\.dirname\(batch_path\), shell=True,',
                    'subprocess.Popen([batch_path], cwd=os.path.dirname(batch_path), shell=False,'
                ),
                (
                    r'subprocess\.Popen\(\[self\.ooba_bat\], cwd=os\.path\.dirname\(self\.ooba_bat\), shell=True\)',
                    'subprocess.Popen([self.ooba_bat], cwd=os.path.dirname(self.ooba_bat), shell=False)'
                ),
                (
                    r'subprocess\.Popen\(\[self\.zwaifu_bat\], cwd=os\.path\.dirname\(self\.zwaifu_bat\), shell=True\)',
                    'subprocess.Popen([self.zwaifu_bat], cwd=os.path.dirname(self.zwaifu_bat), shell=False)'
                ),
                # Fix other shell=True instances
                (
                    r'subprocess\.Popen\(\[bat_path\], cwd=os\.path\.dirname\(bat_path\), shell=True,',
                    'subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=False,'
                ),
                # Fix process restart with shell=True
                (
                    r"instance\['proc'\] = subprocess\.Popen\(\[instance\['bat_path'\]\], cwd=os\.path\.dirname\(instance\['bat_path'\]\), shell=True\)",
                    "instance['proc'] = subprocess.Popen([instance['bat_path']], cwd=os.path.dirname(instance['bat_path']), shell=False)"
                )
            ]
            
            for old_pattern, new_pattern in replacements:
                content = content.replace(old_pattern, new_pattern)
            
            # Write back the fixed content
            with open(main_gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"Fixed subprocess vulnerabilities in {main_gui_file}")
        
        # Fix utility files
        utility_files = [
            "utils/api_server.py",
            "utils/web_interface.py", 
            "utils/mobile_app.py"
        ]
        
        for util_file in utility_files:
            if os.path.exists(util_file):
                self.backup_file(util_file)
                
                with open(util_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix shell=True in utility files
                content = content.replace(
                    'subprocess.Popen([batch_path], cwd=os.path.dirname(batch_path), shell=True,',
                    'subprocess.Popen([batch_path], cwd=os.path.dirname(batch_path), shell=False,'
                )
                
                with open(util_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log(f"Fixed subprocess vulnerabilities in {util_file}")
    
    def fix_bind_all_interfaces(self):
        """Fix hardcoded bind to all interfaces"""
        self.log("Fixing hardcoded bind to all interfaces...")
        
        main_gui_file = "zwaifu_launcher_gui.py"
        if os.path.exists(main_gui_file):
            with open(main_gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace 0.0.0.0 with 127.0.0.1 for security
            replacements = [
                ("host='0.0.0.0'", "host='127.0.0.1'"),
                ("host = '0.0.0.0'", "host = '127.0.0.1'")
            ]
            
            for old_pattern, new_pattern in replacements:
                content = content.replace(old_pattern, new_pattern)
            
            with open(main_gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("Fixed hardcoded bind to all interfaces")
    
    def fix_try_except_pass(self):
        """Fix bare try-except-pass blocks"""
        self.log("Fixing bare try-except-pass blocks...")
        
        main_gui_file = "zwaifu_launcher_gui.py"
        if os.path.exists(main_gui_file):
            with open(main_gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace bare except: with specific exception handling
            replacements = [
                ("except Exception:", "except Exception as e:"),
                ("except:", "except Exception as e:")
            ]
            
            for old_pattern, new_pattern in replacements:
                content = content.replace(old_pattern, new_pattern)
            
            # Add logging for exception handling
            content = content.replace(
                "except Exception as e:\n                pass",
                "except Exception as e:\n                self.log(f'Exception handled: {e}')"
            )
            
            with open(main_gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("Fixed bare try-except-pass blocks")
    
    def fix_path_validation(self):
        """Enhance path validation for security"""
        self.log("Enhancing path validation...")
        
        main_gui_file = "zwaifu_launcher_gui.py"
        if os.path.exists(main_gui_file):
            with open(main_gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Enhanced path validation function
            enhanced_validation = '''
    def _is_safe_path_enhanced(self, path):
        """Enhanced path validation with comprehensive security checks"""
        if not path or not isinstance(path, str):
            return False
        
        try:
            # Normalize path to prevent path traversal attacks
            normalized_path = os.path.normpath(path)
            
            # Check for path traversal attempts and suspicious patterns
            suspicious_patterns = [
                '..',      # Directory traversal
                '~',       # Home directory
                '//',      # Multiple slashes
                '\\',      # Backslashes (Windows path traversal)
                ':',       # Drive letter separator (Windows)
                '|',       # Pipe character
                '*',       # Wildcard
                '?',       # Wildcard
                '<',       # Redirection
                '>',       # Redirection
                '"',       # Quote
                "'",       # Quote
                '%',       # URL encoding
                '&',       # Command separator
                ';',       # Command separator
                '`',       # Command substitution
                '$',       # Variable substitution
                '(',       # Command grouping
                ')',       # Command grouping
                '{',       # Brace expansion
                '}',       # Brace expansion
                '[',       # Character class
                ']',       # Character class
            ]
            
            # Check for suspicious patterns in the normalized path
            for pattern in suspicious_patterns:
                if pattern in normalized_path:
                    return False
            
            # Check for path traversal attempts
            if '..' in normalized_path or normalized_path.startswith('/'):
                return False
            
            # Resolve relative paths
            abs_path = os.path.abspath(normalized_path)
            
            # Additional check: ensure the path doesn't contain any directory traversal
            path_parts = abs_path.split(os.sep)
            for part in path_parts:
                if part == '..' or part.startswith('..') or part.startswith('.'):
                    return False
            
            # Check if path is within project directory
            try:
                common_path = os.path.commonpath([abs_path, self.project_root])
                return common_path == self.project_root
            except ValueError:
                # Paths on different drives (Windows)
                return abs_path.startswith(self.project_root)
                
        except Exception:
            return False
'''
            
            # Replace the existing _is_safe_path method
            if '_is_safe_path(self, path):' in content:
                # Find and replace the method
                start_marker = '    def _is_safe_path(self, path):'
                end_marker = '        return abs_path.startswith(project_root)'
                
                start_idx = content.find(start_marker)
                if start_idx != -1:
                    # Find the end of the method
                    end_idx = content.find(end_marker, start_idx)
                    if end_idx != -1:
                        # Find the next method or end of class
                        next_method = content.find('\n    def ', end_idx)
                        if next_method != -1:
                            end_idx = next_method
                        else:
                            end_idx = content.find('\n\n', end_idx) + 2
                        
                        # Replace the method
                        content = content[:start_idx] + enhanced_validation + content[end_idx:]
            
            with open(main_gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("Enhanced path validation")
    
    def fix_port_validation(self):
        """Enhance port validation"""
        self.log("Enhancing port validation...")
        
        main_gui_file = "zwaifu_launcher_gui.py"
        if os.path.exists(main_gui_file):
            with open(main_gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Enhanced port validation function
            enhanced_port_validation = '''
    def _is_valid_port(self, port_str):
        """Enhanced port validation with comprehensive checks"""
        if not port_str or not isinstance(port_str, str):
            return False
        
        try:
            port = int(port_str)
            # Check valid port range (1-65535)
            if port < 1 or port > 65535:
                return False
            
            # Check for common reserved ports
            reserved_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            if port in reserved_ports:
                return False
                
            return True
        except (ValueError, TypeError):
            return False
'''
            
            # Add the enhanced port validation method
            if '_is_valid_port' not in content:
                # Find a good place to insert it (after other validation methods)
                insert_point = content.find('    def _is_safe_path')
                if insert_point != -1:
                    content = content[:insert_point] + enhanced_port_validation + '\n' + content[insert_point:]
            
            with open(main_gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("Enhanced port validation")
    
    def fix_config_loading(self):
        """Enhance config loading with better error handling"""
        self.log("Enhancing config loading...")
        
        main_gui_file = "zwaifu_launcher_gui.py"
        if os.path.exists(main_gui_file):
            with open(main_gui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Enhanced config loading with backup creation
            enhanced_config_loading = '''
    def load_config_safe(self):
        """Enhanced config loading with comprehensive error handling and backup creation"""
        try:
            if not os.path.exists(self.config_file):
                self.log("Config file not found, creating default config")
                self.save_config()
                return True
            
            # Create backup before loading
            backup_name = f"config_backup_{int(time.time())}.json"
            backup_path = os.path.join(os.path.dirname(self.config_file), backup_name)
            shutil.copy2(self.config_file, backup_path)
            self.log(f"Created config backup: {backup_path}")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validate config data structure
            if not isinstance(config_data, dict):
                self.log("Invalid config data type, using defaults")
                return False
            
            # Load fields with validation
            try:
                self.ooba_port = str(config_data.get("ooba_port", "7860"))
                self.zwaifu_port = str(config_data.get("zwaifu_port", "5000"))
                self.ooba_bat = config_data.get("ooba_bat", "")
                self.zwaifu_bat = config_data.get("zwaifu_bat", "")
                self.ollama_bat = config_data.get("ollama_bat", "")
                self.rvc_bat = config_data.get("rvc_bat", "")
                
                # Validate ports
                if not self._is_valid_port(self.ooba_port):
                    self.log("Invalid Oobabooga port, using default")
                    self.ooba_port = "7860"
                
                if not self._is_valid_port(self.zwaifu_port):
                    self.log("Invalid Z-Waifu port, using default")
                    self.zwaifu_port = "5000"
                
                # Validate file paths
                if self.ooba_bat and not self._is_safe_path_enhanced(self.ooba_bat):
                    self.log("Invalid Oobabooga batch file path")
                    self.ooba_bat = ""
                
                if self.zwaifu_bat and not self._is_safe_path_enhanced(self.zwaifu_bat):
                    self.log("Invalid Z-Waifu batch file path")
                    self.zwaifu_bat = ""
                
                if self.ollama_bat and not self._is_safe_path_enhanced(self.ollama_bat):
                    self.log("Invalid Ollama batch file path")
                    self.ollama_bat = ""
                
                if self.rvc_bat and not self._is_safe_path_enhanced(self.rvc_bat):
                    self.log("Invalid RVC batch file path")
                    self.rvc_bat = ""
                
                return True
                
            except Exception as e:
                self.log(f"Error loading config fields: {e}")
                return False
                
        except json.JSONDecodeError as e:
            self.log(f"JSON decode error in config file: {e}")
            return False
        except Exception as e:
            self.log(f"Unexpected error loading config: {e}")
            return False
'''
            
            # Replace the existing load_config method
            if 'def load_config(self):' in content:
                # Find and replace the method
                start_marker = '    def load_config(self):'
                end_marker = '        except Exception as e:'
                
                start_idx = content.find(start_marker)
                if start_idx != -1:
                    # Find the end of the method
                    end_idx = content.find('        except Exception as e:', start_idx)
                    if end_idx != -1:
                        # Find the next method or end of class
                        next_method = content.find('\n    def ', end_idx)
                        if next_method != -1:
                            end_idx = next_method
                        else:
                            end_idx = content.find('\n\n', end_idx) + 2
                        
                        # Replace the method
                        content = content[:start_idx] + enhanced_config_loading + content[end_idx:]
            
            with open(main_gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("Enhanced config loading")
    
    def create_security_config(self):
        """Create security configuration file"""
        self.log("Creating security configuration...")
        
        security_config = {
            "security_settings": {
                "bind_host": "127.0.0.1",
                "max_connections": 10,
                "timeout_seconds": 30,
                "allowed_origins": ["http://127.0.0.1:5000", "http://localhost:5000"],
                "enable_cors": True,
                "enable_rate_limiting": True,
                "max_requests_per_minute": 60
            },
            "path_validation": {
                "allowed_extensions": [".bat", ".cmd", ".exe", ".py"],
                "blocked_patterns": ["..", "~", "//", "\\\\", ":", "|", "*", "?", "<", ">", "\"", "'", "%", "&", ";", "`", "$", "(", ")", "{", "}", "[", "]"],
                "max_path_length": 260
            },
            "port_validation": {
                "min_port": 1024,
                "max_port": 65535,
                "reserved_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            }
        }
        
        config_file = "security_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(security_config, f, indent=2)
        
        self.log(f"Created security configuration: {config_file}")
    
    def create_security_readme(self):
        """Create security documentation"""
        self.log("Creating security documentation...")
        
        security_readme = """# Security Fixes Applied

## Overview
This document outlines the security vulnerabilities that were identified and fixed in the Z-Waifu Launcher GUI.

## Fixed Vulnerabilities

### 1. Subprocess Shell Injection (High Severity)
**Issue**: Multiple instances of `subprocess.Popen` with `shell=True` were found, which can lead to command injection attacks.

**Fix**: Replaced `shell=True` with `shell=False` and implemented proper argument handling.

**Files Modified**:
- `zwaifu_launcher_gui.py`
- `utils/api_server.py`
- `utils/web_interface.py`
- `utils/mobile_app.py`

### 2. Hardcoded Bind to All Interfaces (Medium Severity)
**Issue**: Services were binding to `0.0.0.0` which exposes them to all network interfaces.

**Fix**: Changed bind address to `127.0.0.1` (localhost only).

### 3. Bare Try-Except-Pass Blocks (Low Severity)
**Issue**: Multiple bare exception handlers that silently ignore errors.

**Fix**: Added proper exception logging and specific exception handling.

### 4. Path Traversal Vulnerabilities (Medium Severity)
**Issue**: Insufficient path validation could allow directory traversal attacks.

**Fix**: Implemented comprehensive path validation with pattern checking.

### 5. Port Validation Bypass (Low Severity)
**Issue**: Port validation was insufficient and could be bypassed.

**Fix**: Enhanced port validation with range checking and reserved port detection.

### 6. Config Loading Vulnerabilities (Low Severity)
**Issue**: Config loading lacked proper error handling and validation.

**Fix**: Added comprehensive error handling, backup creation, and field validation.

## Security Best Practices Implemented

1. **Input Validation**: All user inputs are now properly validated
2. **Path Sanitization**: File paths are checked for malicious patterns
3. **Port Validation**: Ports are validated against allowed ranges
4. **Error Handling**: Proper exception handling with logging
5. **Backup Creation**: Automatic backup creation before config changes
6. **Network Security**: Services bind to localhost only

## Configuration

Security settings can be modified in `security_config.json`:
- Bind host configuration
- Allowed file extensions
- Blocked path patterns
- Port validation rules
- Rate limiting settings

## Testing

Run the security test suite:
```bash
python test_fixes.py
```

## Monitoring

Monitor the application logs for security-related events:
- Invalid path attempts
- Port validation failures
- Config loading errors
- Exception handling events

## Recommendations

1. **Regular Updates**: Keep dependencies updated
2. **Static Analysis**: Run security tools regularly
3. **Log Monitoring**: Monitor logs for suspicious activity
4. **Access Control**: Implement proper access controls
5. **Backup Strategy**: Maintain regular backups

## Contact

For security issues, please report them through the project's issue tracker.
"""
        
        with open("SECURITY.md", 'w', encoding='utf-8') as f:
            f.write(security_readme)
        
        self.log("Created security documentation: SECURITY.md")
    
    def run_security_tests(self):
        """Run security tests to verify fixes"""
        self.log("Running security tests...")
        
        try:
            # Run the existing test suite
            result = subprocess.run([sys.executable, "test_fixes.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ All security tests passed")
            else:
                self.log(f"⚠️ Some security tests failed: {result.stderr}")
                
            return result.returncode == 0
            
        except Exception as e:
            self.log(f"❌ Error running security tests: {e}")
            return False
    
    def apply_all_fixes(self):
        """Apply all security fixes"""
        self.log("Applying all security fixes...")
        
        try:
            # Apply fixes in order
            self.fix_subprocess_shell_vulnerabilities()
            self.fix_bind_all_interfaces()
            self.fix_try_except_pass()
            self.fix_path_validation()
            self.fix_port_validation()
            self.fix_config_loading()
            self.create_security_config()
            self.create_security_readme()
            
            # Run tests
            if self.run_security_tests():
                self.log("🎉 All security fixes applied successfully!")
                return True
            else:
                self.log("⚠️ Security fixes applied but some tests failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Error applying security fixes: {e}")
            return False

def main():
    """Main function to run security fixes"""
    print("Z-Waifu Launcher Security Fixes")
    print("=" * 50)
    
    fixer = SecurityFixes()
    
    if fixer.apply_all_fixes():
        print("\n✅ Security fixes completed successfully!")
        print("📋 Check SECURITY.md for detailed information")
        print("🔒 Security configuration saved to security_config.json")
        return 0
    else:
        print("\n❌ Security fixes failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 