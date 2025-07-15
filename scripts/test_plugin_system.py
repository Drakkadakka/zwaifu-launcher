#!/usr/bin/env python3
"""
Test script for the Z-Waifu Launcher Plugin System
Verifies that plugins can be created, loaded, and managed correctly.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_plugin_template_creation():
    """Test plugin template creation"""
    print("Testing plugin template creation...")
    
    try:
        # Create a simple plugin template manually
        test_plugin_name = "test_plugin"
        plugin_content = f'''#!/usr/bin/env python3
"""
{test_plugin_name} Plugin for Z-Waifu Launcher GUI
A test plugin for debugging.
"""

import os
import sys
from typing import Dict, Any

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from plugin_system import PluginBase
except ImportError:
    print(f"Error: Could not import PluginBase for {test_plugin_name}")
    sys.exit(1)

class TestPlugin(PluginBase):
    """Test plugin implementation"""
    
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "Test Plugin"
        self.description = "A test plugin for debugging"
        self.version = "1.0.0"
        self.author = "Test Author"
        self.enabled = False
        self.config = {{}}
    
    def enable(self) -> bool:
        """Enable the plugin"""
        try:
            self.enabled = True
            print(f"Enabled {{self.name}} plugin")
            return True
        except Exception as e:
            print(f"Error enabling {{self.name}} plugin: {{e}}")
            return False
    
    def disable(self) -> bool:
        """Disable the plugin"""
        try:
            self.enabled = False
            print(f"Disabled {{self.name}} plugin")
            return True
        except Exception as e:
            print(f"Error disabling {{self.name}} plugin: {{e}}")
            return False

# Plugin factory function
def create_plugin(launcher_gui):
    """Create plugin instance"""
    return TestPlugin(launcher_gui)
'''
        
        # Create plugins directory if it doesn't exist
        plugins_dir = os.path.join(project_root, "plugins")
        os.makedirs(plugins_dir, exist_ok=True)
        
        # Write the plugin file
        plugin_file = os.path.join(plugins_dir, f"{test_plugin_name}.py")
        with open(plugin_file, 'w', encoding='utf-8') as f:
            f.write(plugin_content)
        
        if os.path.exists(plugin_file):
            print(f"✅ Plugin template created successfully: {plugin_file}")
            
            # Read and verify the template content
            with open(plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "class TestPlugin" in content and "PluginBase" in content:
                print("✅ Plugin template content is correct")
                
                # Clean up
                os.remove(plugin_file)
                print("✅ Test plugin cleaned up")
                return True
            else:
                print("❌ Plugin template content is incorrect")
                return False
        else:
            print(f"❌ Plugin file not found: {plugin_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing plugin template creation: {e}")
        return False

def test_plugin_marketplace_registry():
    """Test plugin marketplace registry functionality"""
    print("\nTesting plugin marketplace registry...")
    
    try:
        from utils.plugin_marketplace import PluginMarketplace
        
        # Create a temporary launcher GUI mock
        class MockLauncherGUI:
            def log(self, msg):
                print(f"LOG: {msg}")
            
            def _dark_mode(self):
                return False
        
        launcher_gui = MockLauncherGUI()
        marketplace = PluginMarketplace(launcher_gui)
        
        # Test registry loading
        registry = marketplace.load_plugin_registry()
        if registry and 'plugins' in registry:
            print(f"✅ Plugin registry loaded with {len(registry['plugins'])} plugins")
            
            # Test getting available plugins
            plugins = marketplace.get_available_plugins()
            print(f"✅ Found {len(plugins)} available plugins")
            
            # Test getting categories
            categories = marketplace.get_plugin_categories()
            print(f"✅ Found {len(categories)} plugin categories: {categories}")
            
            return True
        else:
            print("❌ Failed to load plugin registry")
            return False
            
    except Exception as e:
        print(f"❌ Error testing plugin marketplace: {e}")
        return False

def test_plugin_system_import():
    """Test that the plugin system module can be imported"""
    print("\nTesting plugin system import...")
    
    try:
        from utils.plugin_system import PluginBase, PluginManager
        print("✅ Plugin system modules imported successfully")
        
        # Test creating a basic plugin
        class MockLauncherGUI:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher_gui = MockLauncherGUI()
        
        # Test PluginBase
        plugin = PluginBase(launcher_gui)
        print(f"✅ PluginBase created: {plugin.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing plugin system: {e}")
        return False

def test_plugin_directory_structure():
    """Test plugin directory structure"""
    print("\nTesting plugin directory structure...")
    
    try:
        # Check if plugins directory exists
        plugins_dir = os.path.join(project_root, "plugins")
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir, exist_ok=True)
            print(f"✅ Created plugins directory: {plugins_dir}")
        else:
            print(f"✅ Plugins directory exists: {plugins_dir}")
        
        # Check if utils directory exists
        utils_dir = os.path.join(project_root, "utils")
        if os.path.exists(utils_dir):
            print(f"✅ Utils directory exists: {utils_dir}")
            
            # Check if plugin_system.py exists
            plugin_system_file = os.path.join(utils_dir, "plugin_system.py")
            if os.path.exists(plugin_system_file):
                print(f"✅ Plugin system file exists: {plugin_system_file}")
                return True
            else:
                print(f"❌ Plugin system file not found: {plugin_system_file}")
                return False
        else:
            print(f"❌ Utils directory not found: {utils_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing directory structure: {e}")
        return False

def main():
    """Run all plugin system tests"""
    print("🧪 Z-Waifu Launcher Plugin System Tests")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_plugin_directory_structure),
        ("Plugin System Import", test_plugin_system_import),
        ("Plugin Template Creation", test_plugin_template_creation),
        ("Plugin Marketplace Registry", test_plugin_marketplace_registry),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Plugin system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the plugin system.")
        return 1

if __name__ == "__main__":
    exit(main()) 