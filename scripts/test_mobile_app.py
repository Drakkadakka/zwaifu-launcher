#!/usr/bin/env python3
"""
Test script for Z-Waifu Mobile App
"""

import requests
import json
import time
import sys
import os

def test_mobile_app():
    """Test the mobile app endpoints"""
    base_url = "http://localhost:8082"  # Updated to match running mobile app port
    
    print("🧪 Testing Z-Waifu Mobile App...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Check if mobile app is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Mobile app is running")
        else:
            print(f"❌ Mobile app returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to mobile app: {e}")
        print("💡 Make sure the mobile app is started in the main GUI")
        return False
    
    # Test 2: Check manifest.json
    try:
        response = requests.get(f"{base_url}/mobile/manifest.json", timeout=5)
        if response.status_code == 200:
            manifest = response.json()
            print(f"✅ Manifest loaded: {manifest.get('name', 'Unknown')}")
        else:
            print(f"❌ Manifest not found: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
    
    # Test 3: Check service worker
    try:
        response = requests.get(f"{base_url}/mobile/sw.js", timeout=5)
        if response.status_code == 200:
            print("✅ Service worker available")
        else:
            print(f"❌ Service worker not found: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading service worker: {e}")
    
    # Test 4: Check icons
    icon_sizes = [16, 32, 192, 512]
    for size in icon_sizes:
        try:
            response = requests.get(f"{base_url}/mobile/icon-{size}x{size}.png", timeout=5)
            if response.status_code == 200:
                print(f"✅ Icon {size}x{size} available")
            else:
                print(f"❌ Icon {size}x{size} not found: {response.status_code}")
        except Exception as e:
            print(f"❌ Error loading icon {size}x{size}: {e}")
    
    # Test 5: Check API endpoints
    try:
        response = requests.get(f"{base_url}/api/mobile/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ Status API working")
            print(f"   Processes: {list(status.keys())}")
        else:
            print(f"❌ Status API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error calling status API: {e}")
    
    # Test 6: Check theme API
    try:
        response = requests.get(f"{base_url}/api/mobile/theme", timeout=5)
        if response.status_code == 200:
            theme = response.json()
            print("✅ Theme API working")
            print(f"   Dark mode: {theme.get('dark_mode', 'Unknown')}")
        else:
            print(f"❌ Theme API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error calling theme API: {e}")
    
    print("-" * 50)
    print("🎉 Mobile app test completed!")
    print("\n📱 To use the mobile app:")
    print("1. Open the main Z-Waifu Launcher GUI")
    print("2. Go to the 'Advanced Features' tab")
    print("3. Click 'Start Mobile App'")
    print("4. Scan the QR code or visit the URL on your mobile device")
    print("5. Add to home screen for PWA functionality")
    
    return True

if __name__ == "__main__":
    test_mobile_app() 