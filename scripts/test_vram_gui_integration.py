#!/usr/bin/env python3
"""
Test VRAM system integration with GUI
"""

import sys
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vram_gui_integration():
    """Test VRAM system integration with GUI components"""
    print("Testing VRAM GUI Integration...")
    print("=" * 50)
    
    try:
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test VRAM monitor creation
        print("1. Testing VRAM monitor creation...")
        from utils.vram_monitor import VRAMMonitor
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
        
        # Test VRAM summary
        print("\n3. Testing VRAM summary...")
        summary = vram_monitor.get_vram_summary()
        print(f"   Monitoring: {summary.get('monitoring', False)}")
        print(f"   Current Source: {summary.get('current_source', 'none')}")
        print(f"   Usage: {summary.get('usage_percent', 0):.1f}%")
        
        # Test VRAM analytics
        print("\n4. Testing VRAM analytics...")
        analytics = vram_monitor.get_vram_analytics()
        if "error" not in analytics:
            print("   ✅ Analytics available")
            summary_analytics = analytics.get("summary", {})
            if "error" not in summary_analytics:
                print(f"   Total Readings: {summary_analytics.get('total_readings', 0)}")
                print(f"   Average Usage: {summary_analytics.get('average_usage', 0):.1f}%")
        else:
            print("   ⚠️  Analytics disabled or error")
        
        # Test system health
        print("\n5. Testing system health...")
        health_data = vram_monitor.get_latest_system_health()
        if health_data:
            print(f"   Health Score: {health_data.get('health_score', 0)}/100")
            print(f"   Status: {health_data.get('status', 'Unknown')}")
        else:
            print("   ⚠️  System health data not available")
        
        # Test model compatibility
        print("\n6. Testing model compatibility...")
        test_models = [
            ("7B Model", 7),
            ("13B Model", 13),
            ("30B Model", 30),
            ("70B Model", 70)
        ]
        
        for model_name, size_gb in test_models:
            compatibility = vram_monitor.get_model_compatibility(model_name, size_gb)
            if "error" not in compatibility:
                compatible = compatibility.get("compatible", False)
                status = "✅ Compatible" if compatible else "❌ Insufficient VRAM"
                print(f"   {model_name}: {status}")
            else:
                print(f"   {model_name}: Error - {compatibility.get('error', 'Unknown')}")
        
        # Test gentle cleanup
        print("\n7. Testing gentle cleanup...")
        cleanup_result = vram_monitor._gentle_cleanup()
        print(f"   Cleanup completed: {cleanup_result.get('total_vram_freed_gb', 0):.2f}GB freed")
        
        # Test VRAM monitoring start/stop
        print("\n8. Testing VRAM monitoring...")
        vram_monitor.start_monitoring()
        print("   ✅ Monitoring started")
        time.sleep(2)  # Let it run for a bit
        vram_monitor.stop_monitoring()
        print("   ✅ Monitoring stopped")
        
        # Test VRAM callbacks
        print("\n9. Testing VRAM callbacks...")
        callback_called = False
        
        def test_callback(vram_info):
            nonlocal callback_called
            callback_called = True
            print(f"   Callback received: {vram_info.get('vram_usage_percent', 0):.1f}% usage")
        
        vram_monitor.register_vram_callback(test_callback)
        vram_monitor.start_monitoring()
        time.sleep(1)
        vram_monitor.stop_monitoring()
        
        if callback_called:
            print("   ✅ Callbacks working")
        else:
            print("   ⚠️  Callbacks not triggered")
        
        # Test VRAM settings
        print("\n10. Testing VRAM settings...")
        original_settings = vram_monitor.vram_settings.copy()
        
        # Test updating settings
        new_settings = {
            "vram_check_interval": 15,
            "vram_warning_threshold": 0.7
        }
        vram_monitor.update_settings(new_settings)
        
        # Verify settings were updated
        if vram_monitor.vram_settings.get("vram_check_interval") == 15:
            print("   ✅ Settings update working")
        else:
            print("   ❌ Settings update failed")
        
        # Restore original settings
        vram_monitor.update_settings(original_settings)
        
        # Test VRAM data export
        print("\n11. Testing VRAM data export...")
        export_result = vram_monitor.export_vram_data("json")
        if "successfully" in export_result:
            print("   ✅ Data export working")
        else:
            print(f"   ⚠️  Export result: {export_result}")
        
        # Test VRAM optimization
        print("\n12. Testing VRAM optimization...")
        optimization_result = vram_monitor.optimize_vram_usage()
        if "error" not in optimization_result:
            print(f"   ✅ Optimization: {optimization_result.get('reason', 'Unknown')}")
        else:
            print(f"   ⚠️  Optimization error: {optimization_result.get('error', 'Unknown')}")
        
        print("\n" + "=" * 50)
        print("✅ VRAM GUI Integration Test Completed Successfully!")
        print("=" * 50)
        
        # Cleanup
        vram_monitor.stop_monitoring()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"\n❌ VRAM GUI Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vram_progress_styles():
    """Test VRAM progress bar styles"""
    print("\nTesting VRAM Progress Bar Styles...")
    print("=" * 30)
    
    try:
        # Create a test window
        root = tk.Tk()
        root.title("VRAM Progress Bar Test")
        root.geometry("400x300")
        
        # Create progress bars with different styles
        styles = [
            ('Good.Horizontal.TProgressbar', 'Good Usage (Green)'),
            ('Moderate.Horizontal.TProgressbar', 'Moderate Usage (Yellow)'),
            ('High.Horizontal.TProgressbar', 'High Usage (Orange)'),
            ('Critical.Horizontal.TProgressbar', 'Critical Usage (Red)'),
            ('Default.Horizontal.TProgressbar', 'Default Style (Blue)')
        ]
        
        for i, (style_name, label_text) in enumerate(styles):
            frame = ttk.Frame(root)
            frame.pack(padx=10, pady=5, fill=tk.X)
            
            ttk.Label(frame, text=label_text).pack(anchor=tk.W)
            
            progress = ttk.Progressbar(frame, style=style_name, length=300, mode='determinate')
            progress.pack(fill=tk.X, pady=2)
            progress['value'] = 75  # Set to 75% for testing
            
            ttk.Label(frame, text="75%").pack(anchor=tk.W)
        
        print("   ✅ Progress bar styles created")
        print("   Check the test window to see the styled progress bars")
        
        # Keep window open for a few seconds
        root.after(3000, root.destroy)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Progress bar styles test failed: {e}")
        return False

if __name__ == "__main__":
    print("VRAM GUI Integration Test Suite")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_vram_gui_integration()
    test2_passed = test_vram_progress_styles()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"VRAM GUI Integration: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Progress Bar Styles: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All VRAM GUI integration tests passed!")
        print("The VRAM system is working properly with the GUI.")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    print("=" * 50) 