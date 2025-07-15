#!/usr/bin/env python3
"""
Start only the mobile app for testing
"""

import os
import sys
import threading
import time
from flask import Flask, send_from_directory, jsonify, request

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock launcher GUI for mobile app
class MockLauncherGUI:
    def __init__(self):
        self._dark_mode = False
        self.process_instance_tabs = {
            'Oobabooga': [],
            'Z-Waifu': [],
            'Ollama': [],
            'RVC': []
        }
    
    def log(self, msg):
        print(f"[Mobile] {msg}")
    
    def get_local_ip(self):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

# Import the MobileApp class
from zwaifu_launcher_gui import MobileApp

def main():
    print("🚀 Starting Z-Waifu Mobile App...")
    
    # Create mock launcher GUI
    mock_gui = MockLauncherGUI()
    
    # Create and start mobile app
    mobile_app = MobileApp(mock_gui)
    
    if mobile_app.start():
        print("✅ Mobile app started successfully!")
        print(f"📱 Access URL: http://{mobile_app.get_local_ip()}:8080")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            # Keep the app running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping mobile app...")
            mobile_app.stop()
            print("✅ Mobile app stopped")
    else:
        print("❌ Failed to start mobile app")

if __name__ == "__main__":
    main() 