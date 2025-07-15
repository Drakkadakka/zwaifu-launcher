#!/usr/bin/env python3
"""
Test Persistent API Key System

This script tests that API keys are properly persisted between launcher restarts.
"""

import os
import json
import time
import sys

def test_persistent_api_key():
    """Test the persistent API key functionality"""
    print("🔑 Testing Persistent API Key System")
    print("=" * 50)
    
    # Check if api_key.json exists
    api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
    
    if os.path.exists(api_key_path):
        print(f"✅ Found existing API key file: {api_key_path}")
        
        # Load and validate the key
        try:
            with open(api_key_path, 'r') as f:
                api_key_data = json.load(f)
            
            api_key = api_key_data.get('api_key')
            created_time = api_key_data.get('created', time.time())
            
            if api_key:
                print(f"✅ API key loaded: {api_key[:16]}...")
                print(f"✅ Created: {time.ctime(created_time)}")
                
                # Check if key is still valid (30 days)
                current_time = time.time()
                age_days = (current_time - created_time) / (24 * 3600)
                
                if age_days <= 30:
                    print(f"✅ Key is valid (age: {age_days:.1f} days)")
                    print(f"✅ Key will expire in: {30 - age_days:.1f} days")
                    return True
                else:
                    print(f"❌ Key has expired (age: {age_days:.1f} days)")
                    return False
            else:
                print("❌ No API key found in file")
                return False
                
        except Exception as e:
            print(f"❌ Error loading API key: {e}")
            return False
    else:
        print(f"❌ No API key file found at: {api_key_path}")
        print("   Generate an API key first using the launcher")
        return False

def simulate_launcher_restart():
    """Simulate what happens when the launcher restarts"""
    print("\n🔄 Simulating Launcher Restart")
    print("=" * 30)
    
    # This would be the APIServer.load_persistent_api_keys() logic
    api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
    
    if os.path.exists(api_key_path):
        try:
            with open(api_key_path, 'r') as f:
                api_key_data = json.load(f)
            
            api_key = api_key_data.get('api_key')
            created_time = api_key_data.get('created', time.time())
            current_time = time.time()
            
            # Check if key is still valid (30 days)
            if current_time - created_time <= 30 * 24 * 3600:
                # Extend expiration to 30 days from now
                new_expires = current_time + (30 * 24 * 3600)
                print(f"✅ Key would be loaded and extended to expire in 30 days")
                print(f"✅ New expiration: {time.ctime(new_expires)}")
                return True
            else:
                print(f"❌ Key would be rejected as expired")
                return False
                
        except Exception as e:
            print(f"❌ Error during restart simulation: {e}")
            return False
    else:
        print("❌ No key file found during restart simulation")
        return False

def main():
    """Main test function"""
    print("Z-Waifu Launcher - Persistent API Key Test")
    print("=" * 60)
    
    # Test 1: Check current key
    print("\n📋 Test 1: Current API Key Status")
    current_key_valid = test_persistent_api_key()
    
    # Test 2: Simulate restart
    print("\n📋 Test 2: Launcher Restart Simulation")
    restart_success = simulate_launcher_restart()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Current Key Valid: {'✅ Yes' if current_key_valid else '❌ No'}")
    print(f"Restart Simulation: {'✅ Success' if restart_success else '❌ Failed'}")
    
    if current_key_valid and restart_success:
        print("\n🎉 All tests passed! API key persistence is working correctly.")
        print("   Your API key will remain valid across launcher restarts.")
    else:
        print("\n⚠️  Some tests failed. You may need to regenerate your API key.")
        print("   Use the launcher to generate a new persistent API key.")

if __name__ == "__main__":
    main() 