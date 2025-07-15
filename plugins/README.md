# Plugin System

This directory contains plugins for the Z-Waifu Launcher.

## Creating a Plugin

1. Create a new Python file in this directory
2. Follow the plugin template structure
3. The launcher will automatically load plugins on startup

## Plugin Template

```python
class Plugin:
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.name = "My Plugin"
        self.description = "A custom plugin"
    
    def on_process_start(self, process_name):
        # Called when a process starts
        pass
    
    def on_process_stop(self, process_name):
        # Called when a process stops
        pass
```
