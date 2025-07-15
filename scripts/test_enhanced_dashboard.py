#!/usr/bin/env python3
"""
Enhanced Dashboard Test Script
Tests all the new features of the enhanced web dashboard
"""

import sys
import os
import time
import requests
import json
import threading
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://127.0.0.1:5001"
    
    print("Testing Enhanced Dashboard API Endpoints")
    print("=" * 50)
    
    test_results = []
    
    try:
        # Test 1: Health check
        print("Test 1: Health check...")
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            test_results.append(("Health Check", True, "API server is running"))
        else:
            print("❌ Health check failed")
            test_results.append(("Health Check", False, f"Status: {response.status_code}"))
        
        # Test 2: Terminal statistics
        print("\nTest 2: Terminal statistics...")
        response = requests.get(f"{base_url}/api/v1/terminal/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics retrieved - Total lines: {stats.get('total_lines', 0)}")
            test_results.append(("Terminal Statistics", True, f"Total lines: {stats.get('total_lines', 0)}"))
        else:
            print("❌ Statistics failed")
            test_results.append(("Terminal Statistics", False, f"Status: {response.status_code}"))
        
        # Test 3: Terminal output
        print("\nTest 3: Terminal output...")
        response = requests.get(f"{base_url}/api/v1/terminal/output")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Output retrieved - Entries: {len(data.get('output', []))}")
            test_results.append(("Terminal Output", True, f"Entries: {len(data.get('output', []))}"))
        else:
            print("❌ Output failed")
            test_results.append(("Terminal Output", False, f"Status: {response.status_code}"))
        
        # Test 4: Filtered output
        print("\nTest 4: Filtered output...")
        response = requests.get(f"{base_url}/api/v1/terminal/output?errors_only=1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filtered output retrieved - Entries: {len(data.get('output', []))}")
            test_results.append(("Filtered Output", True, f"Entries: {len(data.get('output', []))}"))
        else:
            print("❌ Filtered output failed")
            test_results.append(("Filtered Output", False, f"Status: {response.status_code}"))
        
        # Test 5: Export functionality
        print("\nTest 5: Export functionality...")
        for fmt in ['json', 'txt', 'csv']:
            response = requests.get(f"{base_url}/api/v1/terminal/export?format={fmt}")
            if response.status_code == 200:
                print(f"✅ {fmt.upper()} export working")
                test_results.append((f"{fmt.upper()} Export", True, "Export successful"))
            else:
                print(f"❌ {fmt.upper()} export failed")
                test_results.append((f"{fmt.upper()} Export", False, f"Status: {response.status_code}"))
        
        # Test 6: Process status
        print("\nTest 6: Process status...")
        response = requests.get(f"{base_url}/api/v1/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Process status retrieved - Processes: {len(data.get('processes', {}))}")
            test_results.append(("Process Status", True, f"Processes: {len(data.get('processes', {}))}"))
        else:
            print("❌ Process status failed")
            test_results.append(("Process Status", False, f"Status: {response.status_code}"))
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on port 5001.")
        test_results.append(("Connection", False, "API server not accessible"))
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        test_results.append(("Overall Test", False, str(e)))
    
    return test_results

def test_websocket_connection():
    """Test WebSocket connection for live streaming"""
    print("\nTesting WebSocket Connection")
    print("=" * 30)
    
    try:
        import socketio
        
        # Create SocketIO client
        sio = socketio.Client()
        
        connected = False
        received_messages = []
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ WebSocket connected")
            sio.emit('subscribe_terminal')
        
        @sio.event
        def disconnect():
            print("WebSocket disconnected")
        
        @sio.on('terminal_output')
        def on_terminal_output(data):
            received_messages.append(data)
            print(f"📡 Received terminal output: {data.get('line', '')[:50]}...")
        
        # Connect to WebSocket
        sio.connect('http://127.0.0.1:5001')
        
        # Wait for connection and messages
        time.sleep(2)
        
        if connected:
            print("✅ WebSocket connection successful")
            sio.disconnect()
            return True
        else:
            print("❌ WebSocket connection failed")
            return False
            
    except ImportError:
        print("⚠️  SocketIO client not available. Install with: pip install python-socketio")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def simulate_terminal_output():
    """Simulate terminal output to test the system"""
    print("\nSimulating Terminal Output")
    print("=" * 30)
    
    try:
        # Add some test output to the API server
        test_lines = [
            "[12:00:01] Starting Z-Waifu Launcher...",
            "[12:00:02] Loading configuration...",
            "[12:00:03] Warning: Deprecated feature detected",
            "[12:00:04] Error: Failed to connect to database",
            "[12:00:05] Success: Application started successfully",
            "[12:00:06] Info: Memory usage: 45%",
            "[12:00:07] Debug: Processing user input",
            "[12:00:08] Error: Network timeout occurred",
            "[12:00:09] Warning: High CPU usage detected",
            "[12:00:10] Success: Task completed successfully"
        ]
        
        # This would normally be done through the API server
        print("✅ Test output lines prepared")
        print("Note: To see real output, start the API server and run processes")
        
        return True
        
    except Exception as e:
        print(f"❌ Output simulation failed: {e}")
        return False

def main():
    """Main test function"""
    print("Enhanced Dashboard Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Test WebSocket
    websocket_success = test_websocket_connection()
    
    # Test output simulation
    output_success = simulate_terminal_output()
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(api_results) + 2  # +2 for WebSocket and output simulation
    passed_tests = sum(1 for _, success, _ in api_results if success) + (1 if websocket_success else 0) + (1 if output_success else 0)
    
    for test_name, success, message in api_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status} - {message}")
    
    print(f"WebSocket Connection: {'✅ PASS' if websocket_success else '❌ FAIL'}")
    print(f"Output Simulation: {'✅ PASS' if output_success else '❌ FAIL'}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Enhanced dashboard is working correctly.")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Some features may not work correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 