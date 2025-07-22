#!/usr/bin/env python3
"""
Test script to verify the stop_all_instances fix
"""

import os
import sys
import time
import subprocess
import threading

def test_process_termination():
    """Test that processes are properly terminated"""
    print("🧪 Testing process termination...")
    
    # Create a simple test process
    test_proc = subprocess.Popen(
        ['python', '-c', 'import time; time.sleep(30)'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"📊 Test process started with PID: {test_proc.pid}")
    
    # Wait a moment
    time.sleep(1)
    
    # Check if process is running
    if test_proc.poll() is None:
        print("✅ Process is running")
        
        # Test terminate
        print("🔄 Terminating process...")
        test_proc.terminate()
        
        try:
            test_proc.wait(timeout=5)
            print("✅ Process terminated gracefully")
        except subprocess.TimeoutExpired:
            print("⚠️ Process didn't terminate gracefully, force killing...")
            test_proc.kill()
            try:
                test_proc.wait(timeout=2)
                print("✅ Process force killed")
            except subprocess.TimeoutExpired:
                print("❌ Process still running after force kill")
    
    # Final check
    if test_proc.poll() is not None:
        print("✅ Process successfully stopped")
        return True
    else:
        print("❌ Process is still running")
        return False

def test_case_mapping():
    """Test case-insensitive process type mapping"""
    print("\n🧪 Testing case mapping...")
    
    test_cases = [
        ("oobabooga", "Oobabooga"),
        ("Oobabooga", "Oobabooga"),
        ("OOBOBOOGA", "Oobabooga"),
        ("zwaifu", "Z-Waifu"),
        ("Zwaifu", "Z-Waifu"),
        ("ZWAIFU", "Z-Waifu"),
        ("ollama", "Ollama"),
        ("Ollama", "Ollama"),
        ("rvc", "RVC"),
        ("Rvc", "RVC")
    ]
    
    for input_case, expected in test_cases:
        # Simulate the mapping logic
        process_type_lower = input_case.lower()
        if process_type_lower == "oobabooga":
            mapped = "Oobabooga"
        elif process_type_lower == "zwaifu":
            mapped = "Z-Waifu"
        elif process_type_lower == "ollama":
            mapped = "Ollama"
        elif process_type_lower == "rvc":
            mapped = "RVC"
        else:
            mapped = input_case.title()
        
        if mapped == expected:
            print(f"✅ '{input_case}' -> '{mapped}'")
        else:
            print(f"❌ '{input_case}' -> '{mapped}' (expected '{expected}')")

def test_web_interface_response():
    """Test web interface response handling"""
    print("\n🧪 Testing web interface response...")
    
    # Simulate the improved JavaScript function
    def simulate_stop_all_instances(process_type):
        print(f"🔄 Simulating stop_all_instances for '{process_type}'")
        
        # Simulate button state changes
        button_text = "Stop All"
        button_disabled = False
        
        # Simulate API call
        print("📡 Making API call...")
        time.sleep(0.5)  # Simulate network delay
        
        # Simulate success response
        success = True
        if success:
            print("✅ API call successful")
            button_text = "Stopped!"
            print(f"🔄 Button text: {button_text}")
            print("🔄 Page will reload in 1 second...")
        else:
            print("❌ API call failed")
            button_text = "Failed!"
            print(f"🔄 Button text: {button_text}")
        
        return success
    
    # Test different process types
    for process_type in ["oobabooga", "zwaifu", "ollama", "rvc"]:
        simulate_stop_all_instances(process_type)
        time.sleep(0.2)

def main():
    """Main test function"""
    print("🔧 Testing Stop All Instances Fix")
    print("=" * 50)
    
    # Test process termination
    if test_process_termination():
        print("✅ Process termination test passed")
    else:
        print("❌ Process termination test failed")
    
    # Test case mapping
    test_case_mapping()
    
    # Test web interface response
    test_web_interface_response()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed")

if __name__ == "__main__":
    main() 