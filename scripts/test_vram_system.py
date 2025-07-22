#!/usr/bin/env python3
"""
Test script to verify VRAM system functionality
"""

import sys
import os
import time

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
        
        print("\n" + "=" * 50)
        print("✅ VRAM Monitor System Test Completed Successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VRAM Monitor System Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vram_gui_integration():
    """Test VRAM GUI integration"""
    print("\nTesting VRAM GUI Integration...")
    print("=" * 50)
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create a simple test window
        root = tk.Tk()
        root.title("VRAM GUI Test")
        root.geometry("400x300")
        
        # Test VRAM monitor integration
        from utils.vram_monitor import VRAMMonitor
        
        vram_monitor = VRAMMonitor()
        
        # Create test widgets
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status label
        status_label = ttk.Label(frame, text="VRAM Status: Testing...")
        status_label.pack(anchor=tk.W, pady=2)
        
        # Usage label
        usage_label = ttk.Label(frame, text="VRAM Usage: Testing...")
        usage_label.pack(anchor=tk.W, pady=2)
        
        # Progress bar
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill=tk.X, pady=5)
        ttk.Label(progress_frame, text="VRAM Usage:").pack(side=tk.LEFT)
        progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        
        # Test buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def refresh_vram():
            try:
                vram_info = vram_monitor.get_vram_info()
                
                # Update status
                status_text = f"VRAM Status: Active ({vram_info.get('source', 'none')})"
                status_label.config(text=status_text)
                
                # Update usage
                if vram_info.get("total_vram_gb", 0) > 0:
                    usage_percent = vram_info['vram_usage_percent']
                    usage_text = f"VRAM Usage: {vram_info['used_vram_gb']:.1f}GB / {vram_info['total_vram_gb']:.1f}GB ({usage_percent:.1f}%)"
                    
                    if usage_percent > 90:
                        usage_text += " 🔴 CRITICAL"
                    elif usage_percent > 80:
                        usage_text += " 🟠 HIGH"
                    elif usage_percent > 60:
                        usage_text += " 🟡 MODERATE"
                    else:
                        usage_text += " 🟢 GOOD"
                    
                    usage_label.config(text=usage_text)
                    
                    # Update progress bar
                    progress_bar['value'] = usage_percent
                else:
                    usage_label.config(text="VRAM Usage: No GPU detected")
                    progress_bar['value'] = 0
                    
            except Exception as e:
                status_label.config(text=f"VRAM Status: Error - {e}")
                usage_label.config(text="VRAM Usage: Error")
        
        ttk.Button(button_frame, text="Refresh VRAM", command=refresh_vram).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="Test Cleanup", command=lambda: test_cleanup()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=root.destroy).pack(side=tk.RIGHT)
        
        def test_cleanup():
            try:
                result = vram_monitor._gentle_cleanup()
                freed_gb = result.get("total_vram_freed_gb", 0)
                if freed_gb > 0:
                    tk.messagebox.showinfo("Cleanup", f"Gentle cleanup completed!\nFreed: {freed_gb:.2f}GB")
                else:
                    tk.messagebox.showinfo("Cleanup", "Gentle cleanup completed, but no VRAM was freed.")
                refresh_vram()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Cleanup failed: {e}")
        
        # Initial refresh
        refresh_vram()
        
        print("   ✅ VRAM GUI test window created")
        print("   Click 'Refresh VRAM' to test functionality")
        print("   Click 'Test Cleanup' to test VRAM cleanup")
        print("   Click 'Close' to exit")
        
        # Run the GUI
        root.mainloop()
        
        print("   ✅ VRAM GUI Integration Test Completed!")
        return True
        
    except Exception as e:
        print(f"   ❌ VRAM GUI Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("VRAM System Test Suite")
    print("=" * 60)
    
    # Test VRAM monitor
    monitor_success = test_vram_monitor()
    
    # Test GUI integration
    gui_success = test_vram_gui_integration()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"VRAM Monitor: {'✅ PASS' if monitor_success else '❌ FAIL'}")
    print(f"GUI Integration: {'✅ PASS' if gui_success else '❌ FAIL'}")
    
    if monitor_success and gui_success:
        print("\n🎉 All tests passed! VRAM system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.") 