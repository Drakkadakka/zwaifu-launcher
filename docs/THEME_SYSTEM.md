# Z-Waifu Launcher Theme System

## Overview

The Z-Waifu Launcher features a comprehensive theme system that provides both light and dark mode support, along with multiple theme variants and a custom theme editor. The theme system is designed to be extensible, user-friendly, and fully integrated with the launcher GUI.

## Features

### 🎨 Multiple Theme Variants
- **Light Theme**: Clean, bright interface for daytime use
- **Dark Theme**: Easy on the eyes for nighttime use
- **Dark Blue**: Professional dark theme with blue accents
- **Dark Green**: Nature-inspired dark theme with green accents
- **Dark Purple**: Elegant dark theme with purple accents
- **High Contrast**: Accessibility-focused theme with maximum contrast

### 🔧 Custom Theme Support
- Create and save custom themes
- Import/export themes as JSON files
- Visual theme editor with color picker
- Real-time theme preview

### 🌐 Comprehensive Widget Support
- All standard Tkinter widgets
- Ttk widgets with proper styling
- Text widgets with syntax highlighting support
- Listboxes and treeviews
- Buttons, entries, and form controls
- Canvas and custom widgets

### 💾 Theme Persistence
- Automatic theme preference saving
- Theme persistence across application restarts
- Configurable default themes

## Architecture

### ThemeManager Class

The core of the theme system is the `EnhancedThemeManager` class located in `utils/theme_manager.py`. This class provides:

```python
class EnhancedThemeManager:
    def __init__(self, launcher_gui)
    def apply_theme(self, theme_name: str) -> bool
    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]
    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool
    def save_theme_preference(self, theme_name: str) -> bool
    def load_theme_preference(self) -> str
    def create_theme_editor_window(self)
```

### Theme Color Properties

Each theme defines a comprehensive set of color properties:

```python
theme_colors = {
    'bg': '#f0f0f0',              # Main background
    'fg': '#000000',              # Main foreground/text
    'entry_bg': '#ffffff',        # Entry widget background
    'entry_fg': '#000000',        # Entry widget text
    'accent': '#007acc',          # Primary accent color
    'success': '#28a745',         # Success messages
    'warning': '#ffc107',         # Warning messages
    'error': '#dc3545',           # Error messages
    'info': '#17a2b8',            # Info messages
    'button_bg': '#e0e0e0',       # Button background
    'button_fg': '#000000',       # Button text
    'hover_bg': '#007acc',        # Hover state background
    'hover_fg': '#ffffff',        # Hover state text
    'border_color': '#cccccc',    # Border color
    'text_bg': '#ffffff',         # Text widget background
    'text_fg': '#000000',         # Text widget text
    'canvas_bg': '#ffffff',       # Canvas background
    'listbox_bg': '#ffffff',      # Listbox background
    'listbox_fg': '#000000',      # Listbox text
    'select_bg': '#007acc',       # Selection background
    'select_fg': '#ffffff'        # Selection text
}
```

## Usage

### Basic Theme Switching

```python
# Initialize theme manager
from utils import ThemeManager
theme_manager = ThemeManager(launcher_gui)

# Apply a theme
theme_manager.apply_theme('dark')

# Toggle between light and dark
if current_theme == 'light':
    theme_manager.apply_theme('dark')
else:
    theme_manager.apply_theme('light')
```

### Creating Custom Themes

```python
# Create a custom theme
custom_colors = {
    'bg': '#1a1a1a',
    'fg': '#ffffff',
    'entry_bg': '#2d2d30',
    'entry_fg': '#ffffff',
    'accent': '#00ff00',
    # ... other colors
}

theme_manager.create_custom_theme('my_custom_theme', custom_colors)
```

### Theme Editor

The theme editor provides a visual interface for creating and editing themes:

```python
# Open the theme editor
theme_manager.create_theme_editor_window()
```

## Integration with GUI

### Automatic Theme Application

The theme system automatically applies themes to all GUI components:

1. **Root Window**: Background color and ttk style configuration
2. **All Tabs**: Each tab gets themed according to its specific theme
3. **Widgets**: All widgets are recursively styled
4. **Terminal Emulators**: Terminal widgets get proper theming
5. **Advanced Features**: Web interface, mobile app, and analytics get themed

### Theme Toggle Button

The launcher includes a theme toggle button that:
- Shows sun/moon emoji based on current theme
- Toggles between light and dark modes
- Updates all GUI components immediately
- Saves theme preference automatically

## File Structure

```
utils/
├── theme_manager.py          # Main theme manager class
├── __init__.py              # Exports ThemeManager
themes/
├── custom_themes.json       # User-created themes
config/
├── launcher_config.json     # Theme preference storage
scripts/
├── test_theme_system.py     # Theme system tests
├── theme_demo.py           # Theme demonstration
docs/
├── THEME_SYSTEM.md         # This documentation
```

## Testing

### Running Theme Tests

```bash
cd scripts
python test_theme_system.py
```

### Theme Demo

```bash
cd scripts
python theme_demo.py
```

## Customization

### Adding New Default Themes

To add a new default theme, modify the `default_themes` dictionary in `utils/theme_manager.py`:

```python
'my_new_theme': {
    'name': 'My New Theme',
    'bg': '#custom_bg',
    'fg': '#custom_fg',
    # ... all required colors
}
```

### Extending Widget Support

To add support for new widget types, modify the `style_widgets` method in `zwaifu_launcher_gui.py`:

```python
elif cls == 'MyCustomWidget':
    try:
        child.config(
            bg=theme_colors.get('custom_bg', bg_color),
            fg=theme_colors.get('custom_fg', fg_color)
        )
    except Exception:
        pass
```

## Best Practices

### Color Selection

1. **Contrast**: Ensure sufficient contrast between text and background
2. **Accessibility**: Consider colorblind users when choosing colors
3. **Consistency**: Use consistent color schemes across related elements
4. **Readability**: Test themes with actual content

### Theme Development

1. **Test Thoroughly**: Test themes with all widget types
2. **Provide Fallbacks**: Always provide fallback colors
3. **Document Changes**: Document any theme system changes
4. **Backward Compatibility**: Maintain compatibility with existing themes

## Troubleshooting

### Common Issues

1. **Theme Not Applying**: Check if ThemeManager is properly initialized
2. **Widgets Not Themed**: Ensure widget type is handled in `style_widgets`
3. **Colors Not Loading**: Verify theme JSON format is correct
4. **Performance Issues**: Limit theme switching frequency

### Debug Mode

Enable debug logging to troubleshoot theme issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Theme Marketplace**: Online theme sharing and downloading
2. **Animation Support**: Smooth theme transitions
3. **System Theme Integration**: Automatic system theme detection
4. **Advanced Color Schemes**: HSL color space support
5. **Theme Templates**: Pre-built theme templates for common use cases

### Contributing

To contribute to the theme system:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

The theme system is part of the Z-Waifu Launcher project and follows the same license terms. 