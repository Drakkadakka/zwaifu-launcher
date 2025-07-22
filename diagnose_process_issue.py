#!/usr/bin/env python3
"""
Diagnostic script to check process startup and monitoring issues
"""

import os
import sys
import subprocess
import psutil
import time
import json

def check_batch_files():
    """Check if batch files exist and are accessible"""
    print("=== Batch File Check ===")
    
    # Common batch file names
    batch_files = {
        "Oobabooga": ["start_windows.bat", "start_oobabooga.bat", "oobabooga.bat"],
        "Z-Waifu": ["startup.bat", "start_zwaifu.bat", "zwaifu.bat"],
        "Ollama": ["ollama.bat", "start_ollama.bat"],
        "RVC": ["rvc.bat", "start_rvc.bat"]
    }
    
    found_files = {}
    
    for process_type, filenames in batch_files.items():
        print(f"\n{process_type}:")
        for filename in filenames:
            # Search in current directory and subdirectories
            for root, dirs, files in os.walk("."):
                if filename in files:
                    full_path = os.path.join(root, filename)
                    print(f"  ✓ Found: {full_path}")
                    found_files[process_type] = full_path
                    break
            else:
                print(f"  ✗ Not found: {filename}")
    
    return found_files

def test_process_creation(batch_path, process_type):
    """Test creating a process and monitoring it"""
    print(f"\n=== Testing {process_type} Process Creation ===")
    
    if not batch_path or not os.path.exists(batch_path):
        print(f"❌ Batch file not found: {batch_path}")
        return False
    
    print(f"📁 Batch file: {batch_path}")
    print(f"📂 Working directory: {os.path.dirname(batch_path)}")
    
    try:
        # Create process with same parameters as launcher
        proc = subprocess.Popen(
            [batch_path],
            cwd=os.path.dirname(batch_path),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"✅ Process created with PID: {proc.pid}")
        
        # Monitor process for a few seconds
        start_time = time.time()
        output_lines = []
        
        for i in range(10):  # Monitor for 10 seconds
            time.sleep(1)
            
            # Check if process is still running
            if proc.poll() is not None:
                print(f"❌ Process terminated after {i+1} seconds with exit code: {proc.returncode}")
                break
            
            # Try to get CPU and memory usage
            try:
                psutil_proc = psutil.Process(proc.pid)
                cpu_percent = psutil_proc.cpu_percent()
                memory_mb = psutil_proc.memory_info().rss / (1024 * 1024)
                print(f"⏱️  {i+1}s: CPU {cpu_percent:.1f}%, Memory {memory_mb:.1f}MB")
            except Exception as e:
                print(f"❌ Error getting process stats: {e}")
            
            # Try to read output
            try:
                if proc.stdout:
                    line = proc.stdout.readline()
                    if line:
                        output_lines.append(line.strip())
                        print(f"📤 Output: {line.strip()}")
            except Exception as e:
                print(f"❌ Error reading output: {e}")
        
        # Check final status
        if proc.poll() is None:
            print("✅ Process is still running after 10 seconds")
            
            # Try to terminate gracefully
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print("✅ Process terminated gracefully")
            except subprocess.TimeoutExpired:
                proc.kill()
                print("⚠️  Process force killed")
        else:
            print(f"❌ Process terminated with exit code: {proc.returncode}")
        
        # Show collected output
        if output_lines:
            print(f"\n📋 Collected {len(output_lines)} lines of output:")
            for line in output_lines:
                print(f"  {line}")
        else:
            print("\n❌ No output collected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating process: {e}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\n=== System Resources ===")
    
    try:
        # CPU info
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"🖥️  CPU: {cpu_count} cores, {cpu_percent:.1f}% usage")
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_mb = memory.total / (1024 * 1024)
        memory_percent = memory.percent
        print(f"💾 Memory: {memory_mb:.0f}MB total, {memory_percent:.1f}% used")
        
        # Disk info
        disk = psutil.disk_usage('.')
        disk_gb = disk.total / (1024 * 1024 * 1024)
        disk_percent = disk.percent
        print(f"💿 Disk: {disk_gb:.1f}GB total, {disk_percent:.1f}% used")
        
    except Exception as e:
        print(f"❌ Error checking system resources: {e}")

def check_running_processes():
    """Check for already running processes"""
    print("\n=== Running Processes ===")
    
    target_processes = ["python", "cmd", "conhost"]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(target in proc.info['name'].lower() for target in target_processes):
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in ['oobabooga', 'zwaifu', 'ollama', 'rvc']):
                    print(f"🔍 Found: PID {proc.info['pid']} - {proc.info['name']}")
                    print(f"   Command: {cmdline}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def main():
    """Main diagnostic function"""
    print("🔍 Z-Waifu Launcher Process Diagnostic")
    print("=" * 50)
    
    # Check system resources
    check_system_resources()
    
    # Check for running processes
    check_running_processes()
    
    # Check batch files
    found_files = check_batch_files()
    
    # Test process creation for found files
    for process_type, batch_path in found_files.items():
        test_process_creation(batch_path, process_type)
    
    print("\n" + "=" * 50)
    print("✅ Diagnostic complete")

if __name__ == "__main__":
    main() 