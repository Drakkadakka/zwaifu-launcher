#!/usr/bin/env python3
"""
Fix for process startup issues in Z-Waifu Launcher
"""

import os
import sys
import subprocess
import psutil
import time
import threading

def test_batch_file_directly(batch_path, process_type):
    """Test running batch file directly to see what happens"""
    print(f"\n=== Testing {process_type} Batch File Directly ===")
    
    if not batch_path or not os.path.exists(batch_path):
        print(f"❌ Batch file not found: {batch_path}")
        return False
    
    print(f"📁 Batch file: {batch_path}")
    print(f"📂 Working directory: {os.path.dirname(batch_path)}")
    
    try:
        # Run batch file directly (this will show any GUI dialogs or prompts)
        print("🔄 Running batch file directly...")
        result = subprocess.run(
            batch_path,  # Use the path directly, not in a list
            cwd=os.path.dirname(batch_path),
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        print(f"📤 Return code: {result.returncode}")
        print(f"📤 STDOUT: {result.stdout}")
        print(f"📤 STDERR: {result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Batch file timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running batch file: {e}")
        return False

def create_simple_test_batch(batch_path, process_type):
    """Create a simple test batch file to verify the environment"""
    test_batch = f"test_{process_type.lower()}.bat"
    
    if process_type == "Oobabooga":
        content = f"""@echo off
echo Testing Oobabooga environment...
echo Current directory: %CD%
echo Python version:
python --version
echo Checking for text-generation-webui-main directory...
if exist "text-generation-webui-main" (
    echo Found text-generation-webui-main directory
    cd text-generation-webui-main
    echo Checking for server.py...
    if exist "server.py" (
        echo Found server.py
        echo Testing Python import...
        python -c "import sys; print('Python path:', sys.executable)"
    ) else (
        echo server.py not found
        exit /b 1
    )
) else (
    echo text-generation-webui-main directory not found
    exit /b 1
)
echo Test completed successfully
"""
    elif process_type == "Z-Waifu":
        content = f"""@echo off
echo Testing Z-Waifu environment...
echo Current directory: %CD%
echo Python version:
python --version
echo Checking for z-waif-1.14-R4 directory...
if exist "z-waif-1.14-R4" (
    echo Found z-waif-1.14-R4 directory
    cd z-waif-1.14-R4
    echo Checking for main.py...
    if exist "main.py" (
        echo Found main.py
        echo Testing Python import...
        python -c "import sys; print('Python path:', sys.executable)"
    ) else (
        echo main.py not found
        exit /b 1
    )
) else (
    echo z-waif-1.14-R4 directory not found
    exit /b 1
)
echo Test completed successfully
"""
    
    with open(test_batch, 'w') as f:
        f.write(content)
    
    return test_batch

def test_environment():
    """Test the Python environment"""
    print("\n=== Environment Test ===")
    
    try:
        # Test Python version
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"🐍 Python version: {result.stdout.strip()}")
        
        # Test pip
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True)
        print(f"📦 Pip version: {result.stdout.strip()}")
        
        # Test if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Running in virtual environment")
        else:
            print("⚠️  Not running in virtual environment")
        
        # Test current working directory
        print(f"📂 Current directory: {os.getcwd()}")
        
        # Test if key directories exist
        if os.path.exists("text-generation-webui-main"):
            print("✅ text-generation-webui-main directory exists")
        else:
            print("❌ text-generation-webui-main directory not found")
        
        if os.path.exists("z-waif-1.14-R4"):
            print("✅ z-waif-1.14-R4 directory exists")
        else:
            print("❌ z-waif-1.14-R4 directory not found")
        
    except Exception as e:
        print(f"❌ Error testing environment: {e}")

def main():
    """Main function"""
    print("🔧 Z-Waifu Launcher Process Startup Fix")
    print("=" * 50)
    
    # Test environment
    test_environment()
    
    # Test batch files directly
    batch_files = {
        "Oobabooga": "text-generation-webui-main/start_windows.bat",
        "Z-Waifu": "z-waif-1.14-R4/startup.bat"
    }
    
    for process_type, batch_path in batch_files.items():
        if os.path.exists(batch_path):
            test_batch_file_directly(batch_path, process_type)
            
            # Create and test simple batch file
            test_batch = create_simple_test_batch(batch_path, process_type)
            print(f"\n🔄 Testing simple {process_type} batch file...")
            test_batch_file_directly(test_batch, f"{process_type}_Simple")
            
            # Clean up test file
            if os.path.exists(test_batch):
                os.remove(test_batch)
    
    print("\n" + "=" * 50)
    print("✅ Analysis complete")

if __name__ == "__main__":
    main() 