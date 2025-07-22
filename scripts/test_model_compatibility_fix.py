#!/usr/bin/env python3
"""
Test the fixed model compatibility calculation
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_compatibility():
    """Test the fixed model compatibility calculation"""
    print("Testing Fixed Model Compatibility...")
    print("=" * 50)
    
    try:
        from utils.vram_monitor import VRAMMonitor
        
        # Create VRAM monitor
        vram_monitor = VRAMMonitor()
        
        # Get current VRAM info
        vram_info = vram_monitor.get_vram_info()
        print(f"Total VRAM: {vram_info.get('total_vram_gb', 0):.1f}GB")
        print(f"Free VRAM: {vram_info.get('free_vram_gb', 0):.1f}GB")
        print(f"Used VRAM: {vram_info.get('used_vram_gb', 0):.1f}GB")
        print()
        
        # Test model compatibility with explicit sizes
        test_models = [
            ("7B Model", 7),
            ("13B Model", 13),
            ("30B Model", 30),
            ("70B Model", 70)
        ]
        
        for model_name, size_gb in test_models:
            compatibility = vram_monitor.get_model_compatibility(model_name, size_gb)
            print(f"Testing {model_name}:")
            print(f"  Required VRAM: {compatibility.get('required_vram_gb', 0):.1f}GB")
            print(f"  Total VRAM: {compatibility.get('total_vram_gb', 0):.1f}GB")
            print(f"  Free VRAM: {compatibility.get('free_vram_gb', 0):.1f}GB")
            print(f"  Compatible: {compatibility.get('compatible', False)}")
            print(f"  Has Comfortable Space: {compatibility.get('has_comfortable_space', False)}")
            print(f"  Safety Margin: {compatibility.get('safety_margin_gb', 0):.1f}GB")
            print(f"  Recommendation: {compatibility.get('recommendation', 'Unknown')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_model_compatibility() 