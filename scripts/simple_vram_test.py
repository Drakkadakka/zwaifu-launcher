#!/usr/bin/env python3
"""
Simple VRAM test without GUI
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vram_monitor():
    """Test VRAM monitor functionality"""
    print("Testing VRAM Monitor System...")
    print("=" * 50)
    
    try:
        from utils.vram_monitor import VRAMMonitor
        
        # Create VRAM monitor
        print("1. Creating VRAM monitor...")
        vram_monitor = VRAMMonitor()
        print(f"   ✅ VRAM monitor created successfully")
        print(f"   Available sources: {vram_monitor.vram_sources}")
        
        # Test VRAM info retrieval
        print("\n2. Testing VRAM info retrieval...")
        vram_info = vram_monitor.get_vram_info()
        print(f"   Source: {vram_info.get('source', 'none')}")
        print(f"   Total VRAM: {vram_info.get('total_vram_gb', 0):.1f}GB")
        print(f"   Used VRAM: {vram_info.get('used_vram_gb', 0):.1f}GB")
        print(f"   Free VRAM: {vram_info.get('free_vram_gb', 0):.1f}GB")
        print(f"   Usage: {vram_info.get('vram_usage_percent', 0):.1f}%")
        
        # Test system health
        print("\n3. Testing system health...")
        health_data = vram_monitor.get_latest_system_health()
        if health_data:
            print(f"   Health Score: {health_data.get('health_score', 0)}/100")
            print(f"   Status: {health_data.get('status', 'Unknown')}")
        else:
            print("   ⚠️  System health data not available")
        
        # Test model compatibility
        print("\n4. Testing model compatibility...")
        test_models = [
            ("7B Model", 7),
            ("13B Model", 13),
            ("30B Model", 30),
            ("70B Model", 70)
        ]
        
        for model_name, size_gb in test_models:
            result = vram_monitor.get_model_compatibility(model_name, size_gb)
            if "error" not in result:
                status = "✅" if result['compatible'] else "❌"
                print(f"   {status} {model_name}: {result['recommendation']}")
            else:
                print(f"   ⚠️  {model_name}: {result['error']}")
        
        # Test VRAM summary
        print("\n5. Testing VRAM summary...")
        summary = vram_monitor.get_vram_summary()
        print(f"   Monitoring: {summary.get('monitoring', False)}")
        print(f"   Current Source: {summary.get('current_source', 'none')}")
        print(f"   Usage: {summary.get('usage_percent', 0):.1f}%")
        
        # Test analytics
        print("\n6. Testing VRAM analytics...")
        analytics = vram_monitor.get_vram_analytics()
        if "error" not in analytics:
            print("   ✅ Analytics available")
            summary_analytics = analytics.get("summary", {})
            if "error" not in summary_analytics:
                print(f"   Total Readings: {summary_analytics.get('total_readings', 0)}")
                print(f"   Average Usage: {summary_analytics.get('average_usage', 0):.1f}%")
        else:
            print(f"   ⚠️  Analytics: {analytics.get('error', 'Unknown error')}")
        
        # Test cleanup
        print("\n7. Testing gentle cleanup...")
        try:
            result = vram_monitor._gentle_cleanup()
            freed_gb = result.get("total_vram_freed_gb", 0)
            print(f"   Cleanup completed: {freed_gb:.2f}GB freed")
        except Exception as e:
            print(f"   ⚠️  Cleanup failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ VRAM Monitor System Test Completed Successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VRAM Monitor System Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Simple VRAM System Test")
    print("=" * 40)
    
    # Test VRAM monitor
    success = test_vram_monitor()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 VRAM system test passed!")
    else:
        print("⚠️  VRAM system test failed!") 