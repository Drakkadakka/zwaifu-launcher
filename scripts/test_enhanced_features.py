#!/usr/bin/env python3
"""
Test script for enhanced error handling and VRAM monitoring features
"""

import os
import sys
import time
import traceback

def test_error_handler():
    """Test the enhanced error handler"""
    print("Testing Enhanced Error Handler...")
    
    try:
        from utils.error_handler import setup_error_handler
        from utils.config_manager import ConfigManager
        
        # Initialize error handler
        config_file = os.path.join("config", "test_config.json")
        config_manager = ConfigManager(config_file)
        error_handler = setup_error_handler(config_manager)
        
        print("✅ Error handler initialized successfully")
        
        # Test error handling
        try:
            raise ValueError("Test error for enhanced error handler")
        except Exception as e:
            result = error_handler.handle_error(e, "test_error_handler", show_dialog=False)
            print(f"✅ Error handled: {result.get('success', False)}")
        
        # Test error summary
        summary = error_handler.get_error_summary()
        print(f"✅ Error summary: {summary.get('total_errors', 0)} total errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handler test failed: {e}")
        traceback.print_exc()
        return False

def test_vram_monitor():
    """Test the VRAM monitoring system"""
    print("\nTesting VRAM Monitor...")
    
    try:
        from utils.vram_monitor import setup_vram_monitor
        from utils.config_manager import ConfigManager
        
        # Initialize VRAM monitor
        config_file = os.path.join("config", "test_config.json")
        config_manager = ConfigManager(config_file)
        vram_monitor = setup_vram_monitor(config_manager)
        
        print("✅ VRAM monitor initialized successfully")
        
        # Test VRAM info
        vram_info = vram_monitor.get_vram_info()
        print(f"✅ VRAM info: {vram_info.get('source', 'none')} source")
        print(f"   Total VRAM: {vram_info.get('total_vram_gb', 0):.1f}GB")
        print(f"   Used VRAM: {vram_info.get('used_vram_gb', 0):.1f}GB")
        print(f"   Usage: {vram_info.get('vram_usage_percent', 0):.1f}%")
        
        # Test VRAM summary
        summary = vram_monitor.get_vram_summary()
        print(f"✅ VRAM summary: monitoring={summary.get('monitoring', False)}")
        
        # Test cleanup
        cleanup_result = vram_monitor.force_cleanup()
        print(f"✅ VRAM cleanup: {len(cleanup_result.get('methods_successful', []))} methods successful")
        
        return True
        
    except Exception as e:
        print(f"❌ VRAM monitor test failed: {e}")
        traceback.print_exc()
        return False

def test_config_manager():
    """Test the configuration manager"""
    print("\nTesting Config Manager...")
    
    try:
        from utils.config_manager import ConfigManager
        
        # Initialize config manager
        config_file = os.path.join("config", "test_config.json")
        config_manager = ConfigManager(config_file)
        
        print("✅ Config manager initialized successfully")
        
        # Test setting and getting values
        config_manager.set("test_key", "test_value")
        value = config_manager.get("test_key")
        print(f"✅ Config get/set: {value}")
        
        # Test sections
        config_manager.set_section("test_section", {"key1": "value1", "key2": "value2"})
        section = config_manager.get_section("test_section")
        print(f"✅ Config sections: {section}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between systems"""
    print("\nTesting Integration...")
    
    try:
        from utils.error_handler import get_error_handler
        from utils.vram_monitor import get_vram_monitor
        from utils.config_manager import ConfigManager
        
        # Test that systems can work together
        config_file = os.path.join("config", "test_config.json")
        config_manager = ConfigManager(config_file)
        
        error_handler = get_error_handler()
        vram_monitor = get_vram_monitor()
        
        print("✅ Integration test: All systems accessible")
        
        # Test error callback integration
        def test_callback(error_info):
            print(f"   Error callback triggered: {error_info.get('error_type', 'Unknown')}")
        
        error_handler.register_error_callback(test_callback)
        
        # Test VRAM callback integration
        def test_vram_callback(vram_info):
            print(f"   VRAM callback triggered: {vram_info.get('type', 'Unknown')}")
        
        vram_monitor.register_vram_callback(test_vram_callback)
        
        print("✅ Integration test: Callbacks registered")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Enhanced Features Test Suite")
    print("=" * 50)
    
    # Ensure we're in the right directory
    if not os.path.exists("utils"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Create test config directory
    os.makedirs("config", exist_ok=True)
    
    tests = [
        ("Config Manager", test_config_manager),
        ("Error Handler", test_error_handler),
        ("VRAM Monitor", test_vram_monitor),
        ("Integration", test_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 