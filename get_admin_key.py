#!/usr/bin/env python3
"""
Helper script to extract admin key from Z-Waifu Launcher logs
"""

import os
import re
import json
from datetime import datetime

def find_admin_key_in_logs():
    """Search for admin key in launcher logs"""
    log_file = os.path.join("data", "launcher_log.txt")
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        print("Make sure the launcher has been started at least once.")
        return None
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Look for admin key pattern
        pattern = r"Admin API key generated: ([a-f0-9]{64})"
        match = re.search(pattern, log_content)
        
        if match:
            admin_key = match.group(1)
            print(f"✅ Found admin key: {admin_key}")
            return admin_key
        else:
            print("❌ Admin key not found in logs")
            print("Make sure the API server has been started at least once.")
            return None
            
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return None

def check_api_server_status():
    """Check if API server is running"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8081))
        sock.close()
        
        if result == 0:
            print("✅ API server is running on port 8081")
            return True
        else:
            print("❌ API server is not running on port 8081")
            print("Start the launcher and enable the API server first.")
            return False
    except Exception as e:
        print(f"❌ Error checking API server: {e}")
        return False

def main():
    """Main function"""
    print("🔑 Z-Waifu Launcher Admin Key Extractor")
    print("=" * 50)
    print()
    
    # Check if API server is running
    if not check_api_server_status():
        print("\nTo start the API server:")
        print("1. Start the Z-Waifu Launcher")
        print("2. Go to the Advanced Features tab")
        print("3. Click 'Start API Server'")
        print("4. Check the logs for the admin key")
        return
    
    # Try to find admin key
    admin_key = find_admin_key_in_logs()
    
    if admin_key:
        print(f"\n📋 Admin Key: {admin_key}")
        print("\nYou can now use this key with the test script:")
        print("python test_api_authentication.py")
        
        # Save to file for convenience
        config = {
            "admin_key": admin_key,
            "extracted_at": datetime.now().isoformat(),
            "api_url": "http://localhost:8081"
        }
        
        with open("admin_key.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Admin key saved to: admin_key.json")
    else:
        print("\n💡 If you can't find the admin key:")
        print("1. Start the launcher")
        print("2. Go to Advanced Features tab")
        print("3. Start the API server")
        print("4. Check the launcher logs for 'Admin API key generated'")
        print("5. Run this script again")

if __name__ == "__main__":
    main() 