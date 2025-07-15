#!/usr/bin/env python3
"""
Example API Usage Script
Demonstrates how to use the API utilities for making authenticated API calls
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.api_utils import (
        load_api_key, 
        make_authenticated_api_call, 
        test_api_connection,
        get_api_key_info
    )
except ImportError as e:
    print(f"Error importing API utilities: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def main():
    """Main function demonstrating API usage"""
    print("Z-Waifu Launcher API Usage Example")
    print("=" * 50)
    
    # 1. Load API key
    print("\n1. Loading API key...")
    api_key = load_api_key()
    if not api_key:
        print("❌ No API key found!")
        print("   Generate an API key first using the launcher:")
        print("   1. Start the Z-Waifu Launcher")
        print("   2. Go to Advanced Features tab")
        print("   3. Start API Server")
        print("   4. Click 'Generate API Key'")
        return
    
    print(f"✅ API key loaded: {api_key[:16]}...")
    
    # 2. Get API key info
    print("\n2. API Key Information:")
    key_info = get_api_key_info()
    if key_info:
        print(f"   File: {key_info['file_path']}")
        print(f"   Created: {key_info['created']}")
        print(f"   Key: {key_info['api_key']}")
    
    # 3. Test API connection
    print("\n3. Testing API connection...")
    if test_api_connection(api_key=api_key):
        print("✅ API connection successful!")
    else:
        print("❌ API connection failed!")
        print("   Make sure the API server is running on port 8081")
        return
    
    # 4. Make API calls
    print("\n4. Making API calls...")
    
    # Get server status
    print("\n   Getting server status...")
    status = make_authenticated_api_call('/api/status', api_key=api_key)
    if status:
        print(f"   ✅ Server status: {status.get('status', 'Unknown')}")
        print(f"   ✅ API server running: {status.get('api_server_running', False)}")
        print(f"   ✅ Web interface running: {status.get('web_interface_running', False)}")
    else:
        print("   ❌ Failed to get server status")
    
    # Get processes
    print("\n   Getting process information...")
    processes = make_authenticated_api_call('/api/processes', api_key=api_key)
    if processes:
        print("   ✅ Process information retrieved:")
        for process_type, instances in processes.items():
            print(f"      {process_type}: {len(instances)} instances")
            for instance in instances:
                print(f"        - Instance {instance.get('id', 'N/A')}: {instance.get('status', 'Unknown')}")
    else:
        print("   ❌ Failed to get process information")
    
    # 5. Example: Start a process (commented out for safety)
    print("\n5. Example: Starting a process (commented out for safety)")
    print("   Uncomment the following code to test process starting:")
    print("""
    # Start Oobabooga process
    result = make_authenticated_api_call(
        '/api/start/Oobabooga', 
        method='POST', 
        api_key=api_key
    )
    if result:
        print("   ✅ Oobabooga started successfully")
    else:
        print("   ❌ Failed to start Oobabooga")
    """)
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")
    print("\nYou can now use these functions in your own scripts:")
    print("  - load_api_key() - Load the API key from file")
    print("  - make_authenticated_api_call() - Make API calls")
    print("  - test_api_connection() - Test if API is accessible")
    print("  - get_api_key_info() - Get information about the API key")


if __name__ == "__main__":
    main() 