#!/usr/bin/env python3
"""
Simple verification script for dark mode fix
"""

# Check the theme loops in the file
print("Checking dark mode fix...")
with open('zwaifu_launcher_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Check if advanced_features_tab is in TAB_THEMES
    if "'advanced_features_tab': {'bg': '#1a1a1a', 'fg': '#00ccff', 'entry_bg': '#222222', 'entry_fg': '#00ccff'}," in content:
        print("✅ advanced_features_tab found in TAB_THEMES")
    else:
        print("❌ advanced_features_tab missing from TAB_THEMES")
    
    # Check dark mode loop
    dark_mode_line = "for tab_attr in ['main_tab', 'settings_tab', 'about_tab', 'ollama_tab', 'rvc_tab', 'logs_tab', 'ooba_tab', 'zwaifu_tab', 'advanced_features_tab', 'instance_manager_tab']:"
    if dark_mode_line in content:
        print("✅ advanced_features_tab included in dark mode loop")
    else:
        print("❌ advanced_features_tab missing from dark mode loop")
    
    # Check light mode loop
    light_mode_line = "for tab_attr in ['main_tab', 'settings_tab', 'about_tab', 'ollama_tab', 'rvc_tab', 'logs_tab', 'ooba_tab', 'zwaifu_tab', 'advanced_features_tab', 'instance_manager_tab']:"
    if light_mode_line in content:
        print("✅ advanced_features_tab included in light mode loop")
    else:
        print("❌ advanced_features_tab missing from light mode loop")

    # Check if hardcoded styling was removed
    if "self.style_widgets(advanced_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')" in content:
        print("❌ Hardcoded styling still present")
    else:
        print("✅ Hardcoded styling removed")

print("\nDark mode fix verification complete!") 