#!/usr/bin/env python3
"""
Static Analysis Tools Setup for Z-Waifu Launcher GUI
"""

import os
import sys
import subprocess
import json
import datetime
from pathlib import Path

class StaticAnalysisSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.reports_dir = self.project_root / "reports"
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Tools to install
        self.tools = {
            "bandit": {
                "package": "bandit",
                "description": "Security linter for Python",
                "config_file": ".bandit",
                "command": ["bandit", "-r", "zwaifu_launcher_gui.py"]
            },
            "pylint": {
                "package": "pylint",
                "description": "Code quality and error detection",
                "config_file": ".pylintrc",
                "command": ["pylint", "zwaifu_launcher_gui.py"]
            },
            "flake8": {
                "package": "flake8",
                "description": "Style guide enforcement",
                "config_file": ".flake8",
                "command": ["flake8", "zwaifu_launcher_gui.py"]
            },
            "mypy": {
                "package": "mypy",
                "description": "Static type checking",
                "config_file": "mypy.ini",
                "command": ["mypy", "zwaifu_launcher_gui.py"]
            },
            "black": {
                "package": "black",
                "description": "Code formatter",
                "config_file": "pyproject.toml",
                "command": ["black", "--check", "zwaifu_launcher_gui.py"]
            }
        }
    
    def log(self, message):
        """Log setup messages"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def install_tool(self, tool_name, tool_info):
        """Install a specific tool"""
        try:
            self.log(f"Installing {tool_name}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", tool_info["package"]
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"✅ {tool_name} installed successfully")
                return True
            else:
                self.log(f"❌ Failed to install {tool_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error installing {tool_name}: {e}")
            return False
    
    def create_bandit_config(self):
        """Create Bandit configuration file"""
        config = {
            "exclude_dirs": ["venv", "__pycache__", "backups", "logs"],
            "skips": ["B101", "B601"],  # Skip some false positives
            "severity": "medium",
            "confidence": "medium"
        }
        
        config_file = self.project_root / ".bandit"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        self.log("Created .bandit configuration file")
    
    def create_pylint_config(self):
        """Create Pylint configuration file"""
        config = """[MASTER]
# Python code to execute before analysis
init-hook='import sys; sys.path.append(".")'

[MESSAGES CONTROL]
# Disable specific warnings
disable=C0114,C0115,C0116,R0903,R0913,W0621,W0703

[REPORTS]
# Set the output format
output-format=text

# Include a brief explanation of each error
msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}

[BASIC]
# Regular expression which should only match function or class names
good-names=i,j,k,ex,Run,_

[FORMAT]
# Maximum number of characters on a single line
max-line-length=120

[MISCELLANEOUS]
# List of note tags to take into consideration
notes=
"""
        
        config_file = self.project_root / ".pylintrc"
        with open(config_file, "w") as f:
            f.write(config)
        
        self.log("Created .pylintrc configuration file")
    
    def create_flake8_config(self):
        """Create Flake8 configuration file"""
        config = """[flake8]
max-line-length = 120
exclude = venv,__pycache__,backups,logs
ignore = E203,W503,E501
"""
        
        config_file = self.project_root / ".flake8"
        with open(config_file, "w") as f:
            f.write(config)
        
        self.log("Created .flake8 configuration file")
    
    def create_mypy_config(self):
        """Create MyPy configuration file"""
        config = """[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-zwaifu_launcher_gui.*]
ignore_missing_imports = True
"""
        
        config_file = self.project_root / "mypy.ini"
        with open(config_file, "w") as f:
            f.write(config)
        
        self.log("Created mypy.ini configuration file")
    
    def create_black_config(self):
        """Create Black configuration file"""
        config = """[tool.black]
line-length = 120
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''
"""
        
        config_file = self.project_root / "pyproject.toml"
        with open(config_file, "w") as f:
            f.write(config)
        
        self.log("Created pyproject.toml configuration file")
    
    def run_analysis(self, tool_name, tool_info):
        """Run static analysis with a specific tool"""
        try:
            self.log(f"Running {tool_name}...")
            
            # Create output file
            output_file = self.reports_dir / f"{tool_name}_report.txt"
            
            # Run the tool
            result = subprocess.run(
                tool_info["command"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            # Save output
            with open(output_file, "w") as f:
                f.write(f"{tool_name} Analysis Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Command: {' '.join(tool_info['command'])}\n")
                f.write(f"Return Code: {result.returncode}\n")
                f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n\n")
                
                if result.stdout:
                    f.write("STDOUT:\n")
                    f.write(result.stdout)
                    f.write("\n")
                
                if result.stderr:
                    f.write("STDERR:\n")
                    f.write(result.stderr)
                    f.write("\n")
            
            if result.returncode == 0:
                self.log(f"✅ {tool_name} completed successfully")
            else:
                self.log(f"⚠️ {tool_name} found issues (see report)")
            
            return {
                "success": result.returncode == 0,
                "output_file": str(output_file),
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            self.log(f"❌ Error running {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def install_all_tools(self):
        """Install all static analysis tools"""
        self.log("Installing static analysis tools...")
        
        results = {}
        for tool_name, tool_info in self.tools.items():
            success = self.install_tool(tool_name, tool_info)
            results[tool_name] = {"installed": success}
        
        return results
    
    def create_config_files(self):
        """Create configuration files for all tools"""
        self.log("Creating configuration files...")
        
        self.create_bandit_config()
        self.create_pylint_config()
        self.create_flake8_config()
        self.create_mypy_config()
        self.create_black_config()
    
    def run_all_analysis(self):
        """Run all static analysis tools"""
        self.log("Running static analysis...")
        
        results = {}
        for tool_name, tool_info in self.tools.items():
            result = self.run_analysis(tool_name, tool_info)
            results[tool_name] = result
        
        return results
    
    def generate_summary_report(self, install_results, analysis_results):
        """Generate a summary report"""
        timestamp = datetime.datetime.now().isoformat()
        
        summary = {
            "timestamp": timestamp,
            "installation": install_results,
            "analysis": analysis_results,
            "summary": {
                "tools_installed": sum(1 for r in install_results.values() if r["installed"]),
                "tools_total": len(install_results),
                "analysis_passed": sum(1 for r in analysis_results.values() if r["success"]),
                "analysis_total": len(analysis_results)
            }
        }
        
        # Save summary report
        summary_file = self.reports_dir / f"static_analysis_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"Summary report saved: {summary_file}")
        return summary
    
    def setup_ci_config(self):
        """Create CI/CD configuration files"""
        self.log("Creating CI/CD configuration...")
        
        # GitHub Actions workflow
        workflow_content = """name: Static Analysis
on: [push, pull_request]

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install bandit pylint flake8 mypy black
      
      - name: Run Bandit (Security)
        run: bandit -r zwaifu_launcher_gui.py
      
      - name: Run Pylint (Code Quality)
        run: pylint zwaifu_launcher_gui.py
      
      - name: Run Flake8 (Style)
        run: flake8 zwaifu_launcher_gui.py
      
      - name: Run MyPy (Type Checking)
        run: mypy zwaifu_launcher_gui.py
      
      - name: Run Black (Formatting)
        run: black --check zwaifu_launcher_gui.py
"""
        
        workflow_dir = self.project_root / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflow_dir / "static-analysis.yml"
        with open(workflow_file, "w") as f:
            f.write(workflow_content)
        
        self.log("Created GitHub Actions workflow")
    
    def create_pre_commit_hook(self):
        """Create pre-commit hook for local development"""
        hook_content = """#!/bin/bash
# Pre-commit hook for Z-Waifu Launcher GUI

echo "Running pre-commit checks..."

# Run static analysis tools
echo "Running Bandit (security)..."
bandit -r zwaifu_launcher_gui.py || exit 1

echo "Running Flake8 (style)..."
flake8 zwaifu_launcher_gui.py || exit 1

echo "Running Black (formatting)..."
black --check zwaifu_launcher_gui.py || exit 1

echo "All pre-commit checks passed!"
"""
        
        hook_dir = self.project_root / ".git" / "hooks"
        if hook_dir.exists():
            hook_file = hook_dir / "pre-commit"
            with open(hook_file, "w") as f:
                f.write(hook_content)
            
            # Make executable
            os.chmod(hook_file, 0o755)
            self.log("Created pre-commit hook")
        else:
            self.log("Git hooks directory not found, skipping pre-commit hook")

def main():
    """Main setup function"""
    setup = StaticAnalysisSetup()
    
    print("Z-Waifu Launcher GUI - Static Analysis Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            # Install tools
            install_results = setup.install_all_tools()
            setup.create_config_files()
            
            print("\nInstallation Summary:")
            for tool, result in install_results.items():
                status = "✅" if result["installed"] else "❌"
                print(f"  {status} {tool}")
        
        elif sys.argv[1] == "analyze":
            # Run analysis
            analysis_results = setup.run_all_analysis()
            
            print("\nAnalysis Summary:")
            for tool, result in analysis_results.items():
                status = "✅" if result["success"] else "⚠️"
                print(f"  {status} {tool}")
                if "output_file" in result:
                    print(f"    Report: {result['output_file']}")
        
        elif sys.argv[1] == "setup":
            # Complete setup
            print("Installing tools...")
            install_results = setup.install_all_tools()
            setup.create_config_files()
            
            print("Running analysis...")
            analysis_results = setup.run_all_analysis()
            
            print("Setting up CI/CD...")
            setup.setup_ci_config()
            setup.create_pre_commit_hook()
            
            # Generate summary
            summary = setup.generate_summary_report(install_results, analysis_results)
            
            print("\n" + "=" * 50)
            print("SETUP COMPLETE")
            print("=" * 50)
            print(f"Tools installed: {summary['summary']['tools_installed']}/{summary['summary']['tools_total']}")
            print(f"Analysis passed: {summary['summary']['analysis_passed']}/{summary['summary']['analysis_total']}")
            print("\nNext steps:")
            print("1. Review analysis reports in reports/ directory")
            print("2. Fix any critical issues found")
            print("3. Commit the configuration files")
            print("4. Set up GitHub Actions (if using GitHub)")
        
        else:
            print("Usage:")
            print("  python setup_static_analysis.py install  - Install tools only")
            print("  python setup_static_analysis.py analyze  - Run analysis only")
            print("  python setup_static_analysis.py setup    - Complete setup")
    else:
        print("Usage:")
        print("  python setup_static_analysis.py install  - Install tools only")
        print("  python setup_static_analysis.py analyze  - Run analysis only")
        print("  python setup_static_analysis.py setup    - Complete setup")

if __name__ == "__main__":
    main() 