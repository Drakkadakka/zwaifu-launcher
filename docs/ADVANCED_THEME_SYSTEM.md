# Advanced Theme System & Plugin Window Styling

## Overview

The Z-Waifu Launcher now features an **advanced theme system** that provides seamless theme propagation to all plugin windows, advanced styling features, and dynamic theme updates.

## 🎨 **Advanced Styling Features**

### 1. **Dynamic Theme Propagation**
- **Automatic Registration**: All plugin windows automatically register with the main GUI for theme updates
- **Real-time Updates**: Theme changes in the main GUI instantly propagate to all open plugin windows
- **Fallback Support**: Windows without custom theme methods fall back to basic theme application

### 2. **Custom ttk Styles**
Each plugin window uses unique style prefixes to avoid conflicts:
- **Plugin Marketplace**: `ZWaifuMarketplace.*`
- **Installed Plugins**: `ZWaifuInstalled.*`
- **Custom Buttons**: `ZWaifuMarketplace.TButton.Hover`

### 3. **Advanced Widget Styling**
- **Hover Effects**: Buttons change appearance on mouse hover
- **Smooth Transitions**: Visual feedback for user interactions
- **Theme-aware Colors**: All colors automatically adapt to dark/light themes

### 4. **Enhanced Visual Elements**
- **Plugin Cards**: Styled containers with borders and padding
- **Status Messages**: Color-coded feedback (success, error, warning, info)
- **Progress Indicators**: Theme-aware progress bars
- **Tooltips**: Contextual help with theme-appropriate styling

## 🔄 **Theme Propagation System**

### Main GUI Integration
```python
# Enhanced theme update method
def update_registered_windows_theme(self):
    """Update theme for all registered windows with advanced plugin support"""
    if hasattr(self, 'theme_windows'):
        valid_windows = []
        for window in self.theme_windows:
            try:
                if window.winfo_exists():
                    valid_windows.append(window)
                    # Try to call refresh_theme method first (for plugin windows)
                    if hasattr(window, 'refresh_theme'):
                        window.refresh_theme()
                    elif hasattr(window, 'refresh_plugin_theme'):
                        window.refresh_plugin_theme()
                    else:
                        # Fallback to basic theme application
                        self._theme_popup_window(window)
            except Exception as e:
                self.log(f"Failed to update theme for window: {e}")
        
        # Update the theme_windows list with only valid windows
        self.theme_windows = valid_windows
```

### Plugin Window Registration
```python
# Automatic registration in plugin windows
def show(self):
    # ... window creation code ...
    
    # Register with launcher GUI for theme updates
    if hasattr(self.marketplace.launcher_gui, 'register_theme_window'):
        self.marketplace.launcher_gui.register_theme_window(self.window)
    
    # Set up advanced styling features
    self._setup_advanced_styling()
```

## 🎯 **Plugin-Specific Features**

### Plugin Marketplace Window
- **Advanced Search**: Real-time filtering with theme-aware styling
- **Plugin Cards**: Rich visual representation of plugins
- **Category Filtering**: Dropdown with theme-appropriate styling
- **Install Progress**: Visual feedback during plugin installation
- **Status Messages**: Color-coded feedback system

### Installed Plugins Window
- **Plugin List**: Treeview with alternating row colors
- **Dependency Display**: Visual representation of plugin dependencies
- **Installation Dates**: Formatted timestamps
- **Quick Actions**: Theme-aware action buttons

## 🛠 **Implementation Details**

### Theme Color Mapping
The system uses the main GUI's `TAB_THEMES` and `LIGHT_TAB_THEMES` dictionaries:

```python
def _get_current_theme(self) -> Dict[str, str]:
    """Get current theme from launcher GUI using TAB_THEMES/LIGHT_TAB_THEMES['plugin_manager']"""
    if hasattr(self.launcher_gui, '_dark_mode') and hasattr(self.launcher_gui, 'current_theme'):
        if self.launcher_gui._dark_mode:
            theme_dict = getattr(self.launcher_gui, 'TAB_THEMES', None)
        else:
            theme_dict = getattr(self.launcher_gui, 'LIGHT_TAB_THEMES', None)
        if theme_dict and 'plugin_manager' in theme_dict:
            gui_theme = theme_dict['plugin_manager']
            return {
                'bg': gui_theme.get('bg', '#1a1a1a'),
                'fg': gui_theme.get('fg', '#ffffff'),
                'button_bg': gui_theme.get('button_bg', '#333333'),
                'button_fg': gui_theme.get('button_fg', '#ffffff'),
                'entry_bg': gui_theme.get('entry_bg', '#2d2d2d'),
                'entry_fg': gui_theme.get('entry_fg', '#ffffff'),
                'accent': gui_theme.get('accent', '#009966'),
                'tree_bg': gui_theme.get('tree_bg', '#2d2d2d'),
                'tree_fg': gui_theme.get('tree_fg', '#ffffff'),
                'tree_select_bg': gui_theme.get('tree_select_bg', '#0078d4'),
                'tree_select_fg': gui_theme.get('tree_select_fg', '#ffffff'),
                'card_bg': gui_theme.get('card_bg', '#333333'),
                'border_color': gui_theme.get('border_color', '#555555'),
                'success_color': gui_theme.get('success_color', '#28a745'),
                'error_color': gui_theme.get('error_color', '#dc3545'),
                'warning_color': gui_theme.get('warning_color', '#ffc107'),
                'info_color': gui_theme.get('info_color', '#17a2b8')
            }
```

### Advanced Styling Methods
```python
def _setup_advanced_styling(self):
    """Set up advanced styling features for the window"""
    theme = self.marketplace.current_theme
    
    # Add hover effects to buttons
    for widget in self.window.winfo_children():
        if isinstance(widget, ttk.Button):
            widget.bind('<Enter>', lambda e, w=widget: self._on_button_hover(w, True))
            widget.bind('<Leave>', lambda e, w=widget: self._on_button_hover(w, False))
    
    # Add smooth transitions (if supported)
    try:
        self.window.after(100, self._apply_smooth_transitions)
    except:
        pass
```

## 🎨 **Customization Options**

### Adding New Plugin Windows
1. **Inherit from base classes** or implement theme methods
2. **Register with main GUI** using `register_theme_window()`
3. **Implement refresh_theme()** method for custom styling
4. **Use theme color mapping** for consistent appearance

### Extending Theme Colors
Add new color keys to the main GUI's theme dictionaries:
```python
# In TAB_THEMES['plugin_manager']
'custom_color': '#your_color_here',
'highlight_color': '#your_highlight_color'
```

### Custom Widget Styling
```python
# Create custom ttk styles
self.style.configure('Custom.TButton', 
    background=theme['custom_color'],
    foreground=theme['button_fg']
)
```

## 🔧 **Troubleshooting**

### Common Issues
1. **Windows not updating**: Ensure `refresh_theme()` method is implemented
2. **Style conflicts**: Use unique style prefixes for each window
3. **Color mismatches**: Check theme color mapping in `_get_current_theme()`

### Debug Mode
Enable debug logging to track theme updates:
```python
self.log(f"Updating theme for window: {window}")
self.log(f"Applied theme colors: {theme}")
```

## 🚀 **Future Enhancements**

### Planned Features
- **Animation Support**: Smooth transitions between theme states
- **Custom Themes**: User-defined theme creation
- **Plugin Theme API**: Standardized theme interface for plugins
- **Accessibility**: High contrast and accessibility themes

### Performance Optimizations
- **Lazy Loading**: Theme updates only when windows are visible
- **Batch Updates**: Group theme changes for better performance
- **Memory Management**: Clean up unused theme resources

---

## 📋 **Summary**

The advanced theme system provides:
- ✅ **Seamless theme propagation** to all plugin windows
- ✅ **Advanced styling features** with hover effects and transitions
- ✅ **Custom ttk styles** with unique prefixes
- ✅ **Real-time theme updates** when main GUI theme changes
- ✅ **Fallback support** for basic theme application
- ✅ **Comprehensive documentation** and troubleshooting guides

All plugin windows now automatically inherit the main GUI's theme system and update dynamically when themes change, providing a consistent and professional user experience across the entire application. 