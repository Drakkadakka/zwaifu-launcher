#!/usr/bin/env python3
"""
Security and Performance Audit System for Z-Waifu Launcher GUI
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import datetime
import sqlite3
import re
from pathlib import Path
from collections import defaultdict

class SecurityAuditor:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.audit_db = self.project_root / "data" / "audit.db"
        self.audit_log = self.project_root / "logs" / "audit.log"
        self.reports_dir = self.project_root / "reports"
        
        # Ensure directories exist
        self.audit_db.parent.mkdir(exist_ok=True)
        self.audit_log.parent.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Security check patterns
        self.security_patterns = {
            "hardcoded_passwords": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"passwd\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][^'\"]+['\"]"
            ],
            "sql_injection": [
                r"execute\s*\(\s*[\"'].*\+.*[\"']",
                r"cursor\.execute\s*\(\s*[\"'].*\+.*[\"']",
                r"f\"SELECT.*{.*}\"",
                r"f\"INSERT.*{.*}\"",
                r"f\"UPDATE.*{.*}\"",
                r"f\"DELETE.*{.*}\""
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"~",
                r"//",
                r"\\\\"
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"subprocess\.Popen\s*\(",
                r"eval\s*\(",
                r"exec\s*\("
            ],
            "weak_crypto": [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"hashlib\.md5\s*\(",
                r"hashlib\.sha1\s*\("
            ]
        }
        
        # Performance check patterns
        self.performance_patterns = {
            "memory_leaks": [
                r"while\s+True:",
                r"for\s+.*\s+in\s+.*:",
                r"\.append\s*\(",
                r"\.extend\s*\("
            ],
            "inefficient_loops": [
                r"for\s+.*\s+in\s+range\s*\(\s*len\s*\(",
                r"for\s+.*\s+in\s+enumerate\s*\(",
                r"\.keys\s*\(\s*\)",
                r"\.values\s*\(\s*\)"
            ],
            "file_operations": [
                r"open\s*\(",
                r"with\s+open\s*\(",
                r"read\s*\(\s*\)",
                r"write\s*\(\s*\)"
            ]
        }
    
    def log(self, message, level="INFO"):
        """Log audit messages"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def init_database(self):
        """Initialize audit database"""
        try:
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            # Create audit tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    line_number INTEGER,
                    issue_type TEXT,
                    severity TEXT,
                    description TEXT,
                    code_snippet TEXT,
                    status TEXT DEFAULT 'open'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    line_number INTEGER,
                    issue_type TEXT,
                    severity TEXT,
                    description TEXT,
                    code_snippet TEXT,
                    status TEXT DEFAULT 'open'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    report_type TEXT,
                    summary TEXT,
                    details TEXT,
                    recommendations TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            self.log("Audit database initialized")
            
        except Exception as e:
            self.log(f"ERROR: Failed to initialize audit database: {e}", "ERROR")
    
    def scan_file_security(self, file_path):
        """Scan a file for security issues"""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for issue_type, patterns in self.security_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                "file_path": str(file_path),
                                "line_number": line_num,
                                "issue_type": issue_type,
                                "severity": self.get_severity(issue_type),
                                "description": self.get_description(issue_type),
                                "code_snippet": line.strip()
                            })
            
        except Exception as e:
            self.log(f"ERROR: Failed to scan {file_path}: {e}", "ERROR")
        
        return issues
    
    def scan_file_performance(self, file_path):
        """Scan a file for performance issues"""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for issue_type, patterns in self.performance_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                "file_path": str(file_path),
                                "line_number": line_num,
                                "issue_type": issue_type,
                                "severity": "MEDIUM",  # Performance issues are typically medium
                                "description": self.get_performance_description(issue_type),
                                "code_snippet": line.strip()
                            })
            
        except Exception as e:
            self.log(f"ERROR: Failed to scan {file_path}: {e}", "ERROR")
        
        return issues
    
    def get_severity(self, issue_type):
        """Get severity level for security issue"""
        severity_map = {
            "hardcoded_passwords": "HIGH",
            "sql_injection": "CRITICAL",
            "path_traversal": "HIGH",
            "command_injection": "CRITICAL",
            "weak_crypto": "MEDIUM"
        }
        return severity_map.get(issue_type, "MEDIUM")
    
    def get_description(self, issue_type):
        """Get description for security issue"""
        descriptions = {
            "hardcoded_passwords": "Hardcoded credentials found - security risk",
            "sql_injection": "Potential SQL injection vulnerability",
            "path_traversal": "Potential path traversal vulnerability",
            "command_injection": "Potential command injection vulnerability",
            "weak_crypto": "Weak cryptographic algorithm used"
        }
        return descriptions.get(issue_type, "Security issue detected")
    
    def get_performance_description(self, issue_type):
        """Get description for performance issue"""
        descriptions = {
            "memory_leaks": "Potential memory leak detected",
            "inefficient_loops": "Inefficient loop structure",
            "file_operations": "File operation that could be optimized"
        }
        return descriptions.get(issue_type, "Performance issue detected")
    
    def scan_dependencies(self):
        """Scan for vulnerable dependencies"""
        try:
            self.log("Scanning dependencies for vulnerabilities...")
            
            # Check if safety is available
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "list", "--format=freeze"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    packages = result.stdout.strip().split('\n')
                    
                    # Store dependency information
                    conn = sqlite3.connect(self.audit_db)
                    cursor = conn.cursor()
                    
                    for package in packages:
                        if package:
                            name, version = package.split('==')
                            cursor.execute('''
                                INSERT INTO audit_reports 
                                (report_type, summary, details)
                                VALUES (?, ?, ?)
                            ''', ("dependency_scan", f"Package: {name}", f"Version: {version}"))
                    
                    conn.commit()
                    conn.close()
                    
                    self.log(f"Scanned {len(packages)} packages")
                    return len(packages)
                    
            except Exception as e:
                self.log(f"ERROR: Failed to scan dependencies: {e}", "ERROR")
                return 0
                
        except Exception as e:
            self.log(f"ERROR: Dependency scan failed: {e}", "ERROR")
            return 0
    
    def check_file_permissions(self):
        """Check file permissions for security"""
        try:
            self.log("Checking file permissions...")
            
            critical_files = [
                "zwaifu_launcher_gui.py",
                "config/launcher_config.json",
                "data/launcher_log.txt"
            ]
            
            permission_issues = []
            
            for file_path in critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    # Check if file is world-readable
                    stat = full_path.stat()
                    if stat.st_mode & 0o777 == 0o666 or stat.st_mode & 0o777 == 0o777:
                        permission_issues.append({
                            "file": str(full_path),
                            "permission": oct(stat.st_mode & 0o777),
                            "issue": "File is world-readable/writable"
                        })
            
            return permission_issues
            
        except Exception as e:
            self.log(f"ERROR: Failed to check file permissions: {e}", "ERROR")
            return []
    
    def analyze_code_complexity(self):
        """Analyze code complexity"""
        try:
            self.log("Analyzing code complexity...")
            
            complexity_issues = []
            
            # Simple complexity analysis
            with open(self.project_root / "zwaifu_launcher_gui.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Count functions and classes
            function_count = len(re.findall(r'def\s+\w+', ''.join(lines)))
            class_count = len(re.findall(r'class\s+\w+', ''.join(lines)))
            
            # Check for long functions (more than 50 lines)
            current_function = None
            function_start = 0
            
            for line_num, line in enumerate(lines, 1):
                if re.match(r'def\s+\w+', line):
                    if current_function:
                        function_length = line_num - function_start
                        if function_length > 50:
                            complexity_issues.append({
                                "type": "long_function",
                                "function": current_function,
                                "length": function_length,
                                "line": function_start
                            })
                    current_function = line.split('def')[1].split('(')[0].strip()
                    function_start = line_num
            
            # Check last function
            if current_function:
                function_length = len(lines) - function_start
                if function_length > 50:
                    complexity_issues.append({
                        "type": "long_function",
                        "function": current_function,
                        "length": function_length,
                        "line": function_start
                    })
            
            return {
                "function_count": function_count,
                "class_count": class_count,
                "total_lines": len(lines),
                "complexity_issues": complexity_issues
            }
            
        except Exception as e:
            self.log(f"ERROR: Failed to analyze code complexity: {e}", "ERROR")
            return {}
    
    def run_security_scan(self):
        """Run comprehensive security scan"""
        self.log("Starting security scan...")
        
        # Files to scan
        files_to_scan = [
            "zwaifu_launcher_gui.py",
            "test_fixes.py",
            "deploy_fixes.py",
            "monitor_regressions.py"
        ]
        
        all_security_issues = []
        
        for file_name in files_to_scan:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log(f"Scanning {file_name} for security issues...")
                issues = self.scan_file_security(file_path)
                all_security_issues.extend(issues)
                
                # Store in database
                conn = sqlite3.connect(self.audit_db)
                cursor = conn.cursor()
                
                for issue in issues:
                    cursor.execute('''
                        INSERT INTO security_issues 
                        (file_path, line_number, issue_type, severity, description, code_snippet)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        issue["file_path"], issue["line_number"], issue["issue_type"],
                        issue["severity"], issue["description"], issue["code_snippet"]
                    ))
                
                conn.commit()
                conn.close()
        
        self.log(f"Security scan completed. Found {len(all_security_issues)} issues.")
        return all_security_issues
    
    def run_performance_scan(self):
        """Run comprehensive performance scan"""
        self.log("Starting performance scan...")
        
        # Files to scan
        files_to_scan = [
            "zwaifu_launcher_gui.py",
            "test_fixes.py",
            "deploy_fixes.py",
            "monitor_regressions.py"
        ]
        
        all_performance_issues = []
        
        for file_name in files_to_scan:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log(f"Scanning {file_name} for performance issues...")
                issues = self.scan_file_performance(file_path)
                all_performance_issues.extend(issues)
                
                # Store in database
                conn = sqlite3.connect(self.audit_db)
                cursor = conn.cursor()
                
                for issue in issues:
                    cursor.execute('''
                        INSERT INTO performance_issues 
                        (file_path, line_number, issue_type, severity, description, code_snippet)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        issue["file_path"], issue["line_number"], issue["issue_type"],
                        issue["severity"], issue["description"], issue["code_snippet"]
                    ))
                
                conn.commit()
                conn.close()
        
        self.log(f"Performance scan completed. Found {len(all_performance_issues)} issues.")
        return all_performance_issues
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        try:
            self.log("Generating audit report...")
            
            # Get data from database
            conn = sqlite3.connect(self.audit_db)
            cursor = conn.cursor()
            
            # Security issues
            cursor.execute('SELECT * FROM security_issues ORDER BY severity DESC')
            security_issues = cursor.fetchall()
            
            # Performance issues
            cursor.execute('SELECT * FROM performance_issues ORDER BY severity DESC')
            performance_issues = cursor.fetchall()
            
            conn.close()
            
            # Additional checks
            permission_issues = self.check_file_permissions()
            complexity_analysis = self.analyze_code_complexity()
            dependency_count = self.scan_dependencies()
            
            # Generate report
            report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "summary": {
                    "security_issues": len(security_issues),
                    "performance_issues": len(performance_issues),
                    "permission_issues": len(permission_issues),
                    "dependency_count": dependency_count
                },
                "security_issues": [
                    {
                        "file": row[2],
                        "line": row[3],
                        "type": row[4],
                        "severity": row[5],
                        "description": row[6],
                        "code": row[7]
                    } for row in security_issues
                ],
                "performance_issues": [
                    {
                        "file": row[2],
                        "line": row[3],
                        "type": row[4],
                        "severity": row[5],
                        "description": row[6],
                        "code": row[7]
                    } for row in performance_issues
                ],
                "permission_issues": permission_issues,
                "complexity_analysis": complexity_analysis,
                "recommendations": self.generate_recommendations(
                    security_issues, performance_issues, permission_issues
                )
            }
            
            # Save report
            report_file = self.reports_dir / f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            self.log(f"Audit report generated: {report_file}")
            return report
            
        except Exception as e:
            self.log(f"ERROR: Failed to generate audit report: {e}", "ERROR")
            return None
    
    def generate_recommendations(self, security_issues, performance_issues, permission_issues):
        """Generate recommendations based on audit findings"""
        recommendations = []
        
        # Security recommendations
        if security_issues:
            recommendations.append({
                "category": "Security",
                "priority": "HIGH",
                "recommendation": "Address security vulnerabilities found in code",
                "details": f"Found {len(security_issues)} security issues that need immediate attention"
            })
        
        # Performance recommendations
        if performance_issues:
            recommendations.append({
                "category": "Performance",
                "priority": "MEDIUM",
                "recommendation": "Optimize code for better performance",
                "details": f"Found {len(performance_issues)} performance issues that could be improved"
            })
        
        # Permission recommendations
        if permission_issues:
            recommendations.append({
                "category": "Security",
                "priority": "HIGH",
                "recommendation": "Fix file permissions",
                "details": f"Found {len(permission_issues)} files with insecure permissions"
            })
        
        # General recommendations
        recommendations.extend([
            {
                "category": "Best Practices",
                "priority": "MEDIUM",
                "recommendation": "Implement regular security audits",
                "details": "Schedule monthly security and performance audits"
            },
            {
                "category": "Monitoring",
                "priority": "MEDIUM",
                "recommendation": "Set up continuous monitoring",
                "details": "Implement automated monitoring for security and performance issues"
            }
        ])
        
        return recommendations

def main():
    """Main audit function"""
    auditor = SecurityAuditor()
    
    print("Z-Waifu Launcher GUI - Security & Performance Audit")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "security":
            print("Running security scan...")
            security_issues = auditor.run_security_scan()
            print(f"Found {len(security_issues)} security issues")
        
        elif sys.argv[1] == "performance":
            print("Running performance scan...")
            performance_issues = auditor.run_performance_scan()
            print(f"Found {len(performance_issues)} performance issues")
        
        elif sys.argv[1] == "full":
            print("Running full audit...")
            security_issues = auditor.run_security_scan()
            performance_issues = auditor.run_performance_scan()
            report = auditor.generate_audit_report()
            
            if report:
                print("\n" + "=" * 60)
                print("AUDIT COMPLETE")
                print("=" * 60)
                print(f"Security Issues: {report['summary']['security_issues']}")
                print(f"Performance Issues: {report['summary']['performance_issues']}")
                print(f"Permission Issues: {report['summary']['permission_issues']}")
                print(f"Dependencies Scanned: {report['summary']['dependency_count']}")
                
                print("\nTop Recommendations:")
                for rec in report['recommendations'][:3]:
                    print(f"  [{rec['priority']}] {rec['recommendation']}")
        
        else:
            print("Usage:")
            print("  python security_audit.py security   - Security scan only")
            print("  python security_audit.py performance - Performance scan only")
            print("  python security_audit.py full        - Full audit")
    else:
        print("Usage:")
        print("  python security_audit.py security   - Security scan only")
        print("  python security_audit.py performance - Performance scan only")
        print("  python security_audit.py full        - Full audit")

if __name__ == "__main__":
    main() 