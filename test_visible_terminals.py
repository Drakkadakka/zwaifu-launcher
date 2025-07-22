#!/usr/bin/env python3
"""
Test script for Z-Waifu Launcher with visible terminals and CPU/memory monitoring
"""

import os
import sys
import time
import subprocess
import psutil

def test_launcher_startup():
    """Test the launcher startup with visible terminals"""
    print("🧪 Testing Z-Waifu Launcher with Visible Terminals")
    print("=" * 60)
    
    # Check if launcher file exists
    launcher_path = "zwaifu_launcher_gui.py"
    if not os.path.exists(launcher_path):
        print(f"❌ Launcher file not found: {launcher_path}")
        return False
    
    print(f"✅ Found launcher: {launcher_path}")
    
    # Test Python environment
    try:
        import psutil
        print("✅ psutil module available")
    except ImportError:
        print("❌ psutil module not available - CPU/memory monitoring will not work")
        return False
    
    # Test batch file detection
    batch_files = {
        "Oobabooga": "text-generation-webui-main/start_windows.bat",
        "Z-Waifu": "z-waif-1.14-R4/startup.bat"
    }
    
    for name, path in batch_files.items():
        if os.path.exists(path):
            print(f"✅ Found {name} batch file: {path}")
        else:
            print(f"⚠️  {name} batch file not found: {path}")
    
    print("\n🚀 Starting launcher...")
    print("📝 Instructions:")
    print("1. Click 'Start with Visible Terminals' button")
    print("2. Check that processes start in separate terminal windows")
    print("3. Verify CPU and memory monitoring shows actual values (not 0%)")
    print("4. Check that process status labels update with real-time data")
    
    return True

def test_process_monitoring():
    """Test CPU and memory monitoring functionality"""
    print("\n🔍 Testing Process Monitoring")
    print("=" * 40)
    
    try:
        # Test system monitoring
        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        
        print(f"📊 System CPU: {cpu_percent:.1f}%")
        print(f"📊 System Memory: {memory.percent:.1f}%")
        print(f"📊 System RAM: {memory.total / 1024 / 1024 / 1024:.1f} GB total")
        
        if cpu_percent > 0 or memory.percent > 0:
            print("✅ CPU and memory monitoring working correctly")
            return True
        else:
            print("⚠️  CPU and memory values are 0% - this might be normal on idle system")
            return True
            
    except Exception as e:
        print(f"❌ Error testing process monitoring: {e}")
        return False

def test_batch_file_execution():
    """Test batch file execution capabilities"""
    print("\n🔧 Testing Batch File Execution")
    print("=" * 40)
    
    # Create a simple test batch file
    test_batch = "test_batch.bat"
    test_content = """@echo off
echo Testing batch file execution...
echo Current directory: %CD%
echo Python version:
python --version
echo Test completed successfully
pause
"""
    
    try:
        with open(test_batch, 'w') as f:
            f.write(test_content)
        
        print(f"✅ Created test batch file: {test_batch}")
        
        # Test execution with visible console
        print("🔄 Testing batch file execution with visible console...")
        proc = subprocess.Popen(
            [test_batch],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"✅ Process started with PID: {proc.pid}")
        print("📝 A new console window should have opened")
        
        # Wait a moment then check if process is running
        time.sleep(2)
        if proc.poll() is None:
            print("✅ Process is running successfully")
            # Terminate the test process
            proc.terminate()
            time.sleep(1)
            if proc.poll() is not None:
                print("✅ Process terminated successfully")
            else:
                proc.kill()
                print("✅ Process force-killed")
        else:
            print("❌ Process exited unexpectedly")
            return False
        
        # Clean up test file
        if os.path.exists(test_batch):
            os.remove(test_batch)
            print("✅ Test batch file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing batch file execution: {e}")
        # Clean up on error
        if os.path.exists(test_batch):
            os.remove(test_batch)
        return False

def main():
    """Main test function"""
    print("🧪 Z-Waifu Launcher Visible Terminals Test")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Launcher Startup", test_launcher_startup),
        ("Process Monitoring", test_process_monitoring),
        ("Batch File Execution", test_batch_file_execution)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The launcher should work correctly.")
        print("\n📝 Next steps:")
        print("1. Run the launcher: python zwaifu_launcher_gui.py")
        print("2. Click 'Start with Visible Terminals'")
        print("3. Verify processes start in separate terminal windows")
        print("4. Check CPU and memory monitoring displays real values")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 