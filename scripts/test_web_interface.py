#!/usr/bin/env python3
"""
Test script for web interface debugging
"""

import requests
import json
import time

def test_web_interface():
    """Test the web interface endpoints"""
    base_url = "http://localhost:8080"
    
    print("Testing Z-Waifu Launcher Web Interface")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"✓ Server is running (Status: {response.status_code})")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status endpoint working")
            print(f"  - Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"  - Launcher running: {data.get('launcher_running', 'N/A')}")
            
            # Check processes
            processes = data.get('processes', {})
            print(f"  - Process types found: {list(processes.keys())}")
            
            for process_type, instances in processes.items():
                print(f"    - {process_type}: {len(instances)} instances")
                for i, instance in enumerate(instances):
                    print(f"      - Instance {i+1}: {instance.get('status', 'Unknown')} (PID: {instance.get('pid', 'N/A')})")
            
            # Check system info
            system_info = data.get('system_info', {})
            print(f"  - CPU Usage: {system_info.get('cpu_percent', 'N/A')}%")
            print(f"  - Memory Usage: {system_info.get('memory_percent', 'N/A')}%")
            
        else:
            print(f"✗ Status endpoint returned error: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to web interface. Is it running?")
        print("  Make sure to start the web interface from the launcher first.")
        return False
    except Exception as e:
        print(f"✗ Error testing status endpoint: {e}")
        return False
    
    # Test 2: Test process creation
    print("\nTesting process creation...")
    for process_type in ['Oobabooga', 'Z-Waifu']:
        try:
            print(f"  Creating {process_type} instance...")
            response = requests.post(
                f"{base_url}/api/process/{process_type}",
                json={},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"    ✓ {process_type} instance created successfully")
                else:
                    print(f"    ✗ Failed to create {process_type} instance: {result.get('error', 'Unknown error')}")
            else:
                print(f"    ✗ HTTP error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"    ✗ Error creating {process_type} instance: {e}")
    
    # Test 3: Check status again after creation
    print("\nChecking status after instance creation...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            processes = data.get('processes', {})
            
            for process_type, instances in processes.items():
                print(f"  - {process_type}: {len(instances)} instances")
                for i, instance in enumerate(instances):
                    print(f"    - Instance {i+1}: {instance.get('status', 'Unknown')} (PID: {instance.get('pid', 'N/A')})")
        else:
            print(f"✗ Failed to get status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error checking status: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    return True

if __name__ == "__main__":
    test_web_interface() 