#!/usr/bin/env python3
"""
Enhanced Theme Manager for Z-Waifu Launcher GUI
Supports custom themes, multiple dark mode variants, and user-defined color schemes.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, List, Any, Optional
import shutil
from datetime import datetime

class EnhancedThemeManager:
    """Enhanced theme manager with custom themes and multiple variants"""
    
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.themes_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
        self.custom_themes_file = os.path.join(self.themes_dir, 'custom_themes.json')
        
        # Create themes directory
        os.makedirs(self.themes_dir, exist_ok=True)
        
        # Default theme variants - Enhanced with more comprehensive color schemes
        self.default_themes = {
            'light': {
                'name': 'Light',
                'bg': '#fafafa',
                'fg': '#2d3748',
                'entry_bg': '#ffffff',
                'entry_fg': '#2d3748',
                'accent': '#3182ce',
                'success': '#38a169',
                'warning': '#d69e2e',
                'error': '#e53e3e',
                'info': '#3182ce',
                'button_bg': '#f7fafc',
                'button_fg': '#2d3748',
                'hover_bg': '#3182ce',
                'hover_fg': '#ffffff',
                'border_color': '#e2e8f0',
                'text_bg': '#ffffff',
                'text_fg': '#2d3748',
                'canvas_bg': '#ffffff',
                'listbox_bg': '#ffffff',
                'listbox_fg': '#2d3748',
                'select_bg': '#3182ce',
                'select_fg': '#ffffff'
            },
            'dark': {
                'name': 'Dark',
                'bg': '#1e1e2e',
                'fg': '#cdd6f4',
                'entry_bg': '#313244',
                'entry_fg': '#cdd6f4',
                'accent': '#89b4fa',
                'success': '#a6e3a1',
                'warning': '#f9e2af',
                'error': '#f38ba8',
                'info': '#89dceb',
                'button_bg': '#313244',
                'button_fg': '#cdd6f4',
                'hover_bg': '#89b4fa',
                'hover_fg': '#1e1e2e',
                'border_color': '#45475a',
                'text_bg': '#313244',
                'text_fg': '#cdd6f4',
                'canvas_bg': '#313244',
                'listbox_bg': '#313244',
                'listbox_fg': '#cdd6f4',
                'select_bg': '#89b4fa',
                'select_fg': '#1e1e2e'
            },
            'dark_blue': {
                'name': 'Dark Blue',
                'bg': '#1a202c',
                'fg': '#e2e8f0',
                'entry_bg': '#2d3748',
                'entry_fg': '#e2e8f0',
                'accent': '#3182ce',
                'success': '#38a169',
                'warning': '#d69e2e',
                'error': '#e53e3e',
                'info': '#3182ce',
                'button_bg': '#2d3748',
                'button_fg': '#e2e8f0',
                'hover_bg': '#3182ce',
                'hover_fg': '#ffffff',
                'border_color': '#4a5568',
                'text_bg': '#2d3748',
                'text_fg': '#e2e8f0',
                'canvas_bg': '#2d3748',
                'listbox_bg': '#2d3748',
                'listbox_fg': '#e2e8f0',
                'select_bg': '#3182ce',
                'select_fg': '#ffffff'
            },
            'dark_green': {
                'name': 'Dark Green',
                'bg': '#1a202c',
                'fg': '#e2e8f0',
                'entry_bg': '#2d3748',
                'entry_fg': '#e2e8f0',
                'accent': '#38a169',
                'success': '#38a169',
                'warning': '#d69e2e',
                'error': '#e53e3e',
                'info': '#3182ce',
                'button_bg': '#2d3748',
                'button_fg': '#e2e8f0',
                'hover_bg': '#38a169',
                'hover_fg': '#ffffff',
                'border_color': '#4a5568',
                'text_bg': '#2d3748',
                'text_fg': '#e2e8f0',
                'canvas_bg': '#2d3748',
                'listbox_bg': '#2d3748',
                'listbox_fg': '#e2e8f0',
                'select_bg': '#38a169',
                'select_fg': '#ffffff'
            },
            'dark_purple': {
                'name': 'Dark Purple',
                'bg': '#2a1a2e',
                'fg': '#e2e8f0',
                'entry_bg': '#3a2e3a',
                'entry_fg': '#e2e8f0',
                'accent': '#805ad5',
                'success': '#38a169',
                'warning': '#d69e2e',
                'error': '#e53e3e',
                'info': '#3182ce',
                'button_bg': '#3a2e3a',
                'button_fg': '#e2e8f0',
                'hover_bg': '#805ad5',
                'hover_fg': '#ffffff',
                'border_color': '#5a2d5a',
                'text_bg': '#3a2e3a',
                'text_fg': '#e2e8f0',
                'canvas_bg': '#3a2e3a',
                'listbox_bg': '#3a2e3a',
                'listbox_fg': '#e2e8f0',
                'select_bg': '#805ad5',
                'select_fg': '#ffffff'
            },
            'high_contrast': {
                'name': 'High Contrast',
                'bg': '#000000',
                'fg': '#ffffff',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'accent': '#ffff00',
                'success': '#00ff00',
                'warning': '#ffff00',
                'error': '#ff0000',
                'info': '#00ffff',
                'button_bg': '#ffffff',
                'button_fg': '#000000',
                'hover_bg': '#ffff00',
                'hover_fg': '#000000',
                'border_color': '#ffffff',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'canvas_bg': '#ffffff',
                'listbox_bg': '#ffffff',
                'listbox_fg': '#000000',
                'select_bg': '#ffff00',
                'select_fg': '#000000'
            }
        }
        
        # Load custom themes
        self.custom_themes = self.load_custom_themes()
        
        # Current theme - load from preference
        self.current_theme = self.load_theme_preference()
        
    def load_custom_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load custom themes from file"""
        try:
            if os.path.exists(self.custom_themes_file):
                with open(self.custom_themes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading custom themes: {e}")
            return {}
    
    def save_custom_themes(self) -> bool:
        """Save custom themes to file"""
        try:
            with open(self.custom_themes_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_themes, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving custom themes: {e}")
        return False

    def get_all_themes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available themes (default + custom)"""
        all_themes = self.default_themes.copy()
        all_themes.update(self.custom_themes)
        return all_themes
    
    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific theme by name"""
        all_themes = self.get_all_themes()
        return all_themes.get(theme_name)
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Create a new custom theme"""
        try:
            # Validate required colors
            required_colors = ['bg', 'fg', 'entry_bg', 'entry_fg', 'accent']
            for color in required_colors:
                if color not in colors:
                    raise ValueError(f"Missing required color: {color}")
            
            # Add default colors if not provided
            default_colors = {
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545',
                'info': '#17a2b8',
                'button_bg': colors.get('entry_bg', '#ffffff'),
                'button_fg': colors.get('fg', '#000000'),
                'hover_bg': colors.get('accent', '#007acc'),
                'hover_fg': colors.get('fg', '#000000'),
                'border_color': colors.get('accent', '#007acc'),
                'text_bg': colors.get('entry_bg', '#ffffff'),
                'text_fg': colors.get('fg', '#000000'),
                'canvas_bg': colors.get('entry_bg', '#ffffff'),
                'listbox_bg': colors.get('entry_bg', '#ffffff'),
                'listbox_fg': colors.get('fg', '#000000'),
                'select_bg': colors.get('accent', '#007acc'),
                'select_fg': colors.get('fg', '#000000')
            }
            
            for key, value in default_colors.items():
                if key not in colors:
                    colors[key] = value
            
            # Create theme object
            theme = {
                'name': name,
                'custom': True,
                'created': datetime.now().isoformat(),
                **colors
            }
            
            self.custom_themes[name] = theme
            return self.save_custom_themes()
                
        except Exception as e:
            print(f"Error creating custom theme: {e}")
            return False
    
    def update_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Update an existing custom theme"""
        if name not in self.custom_themes:
            return False
        
        try:
            # Update colors
            for key, value in colors.items():
                self.custom_themes[name][key] = value
            
            self.custom_themes[name]['modified'] = datetime.now().isoformat()
            return self.save_custom_themes()
            
        except Exception as e:
            print(f"Error updating custom theme: {e}")
            return False
    
    def delete_custom_theme(self, name: str) -> bool:
        """Delete a custom theme"""
        if name not in self.custom_themes:
            return False
        
        try:
            del self.custom_themes[name]
            return self.save_custom_themes()
            
        except Exception as e:
            print(f"Error deleting custom theme: {e}")
            return False
    
    def export_theme(self, theme_name: str, filepath: str) -> bool:
        """Export a theme to a JSON file"""
        try:
            theme = self.get_theme(theme_name)
            if not theme:
                return False
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, filepath: str) -> bool:
        """Import a theme from a JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme = json.load(f)
            
            if 'name' not in theme:
                return False
            
            # Add timestamp
            theme['imported'] = datetime.now().isoformat()
            theme['custom'] = True
            
            self.custom_themes[theme['name']] = theme
            return self.save_custom_themes()
            
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply a theme to the launcher GUI"""
        try:
            theme = self.get_theme(theme_name)
            if not theme:
                return False
            
            # Update current theme
            self.current_theme = theme_name
            
            # Apply theme to launcher GUI
            if self.launcher_gui:
                # Update launcher GUI theme state
                self.launcher_gui.current_theme = theme_name
                self.launcher_gui._dark_mode = theme_name != 'light'
                
                # Apply theme to root window
                self.launcher_gui.root.configure(bg=theme['bg'])
                
                # Apply ttk styles
                style = ttk.Style()
                if theme_name == 'light':
                    style.theme_use('default')
                else:
                    style.theme_use('clam')
                
                # Configure ttk styles
                style.configure('.', 
                    background=theme['bg'], 
                    foreground=theme['fg']
                )
                style.configure('TLabel', 
                    background=theme['bg'], 
                    foreground=theme['fg']
                )
                style.configure('TFrame', 
                    background=theme['bg']
                )
                style.configure('TButton', 
                    background=theme['button_bg'], 
                    foreground=theme['button_fg']
                )
                style.configure('TNotebook', 
                    background=theme['bg']
                )
                style.configure('TNotebook.Tab', 
                    background=theme['button_bg'], 
                    foreground=theme['button_fg']
                )
                style.configure('TEntry', 
                    fieldbackground=theme['entry_bg'], 
                    foreground=theme['entry_fg'], 
                    insertcolor=theme['fg']
                )
                
                # Restyle all tabs
                if hasattr(self.launcher_gui, 'restyle_all_tabs'):
                    self.launcher_gui.restyle_all_tabs()
                
                # Update theme toggle button
                if hasattr(self.launcher_gui, '_update_theme_button'):
                    self.launcher_gui._update_theme_button()
                
                # Update registered windows
                if hasattr(self.launcher_gui, 'update_registered_windows_theme'):
                    self.launcher_gui.update_registered_windows_theme()
            
            # Save theme preference
            self.save_theme_preference(theme_name)
            
            return True
            
        except Exception as e:
            print(f"Error applying theme: {e}")
            return False
    
    def save_theme_preference(self, theme_name: str) -> bool:
        """Save theme preference to config"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'launcher_config.json')
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config['theme'] = theme_name
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving theme preference: {e}")
            return False
    
    def load_theme_preference(self) -> str:
        """Load theme preference from config"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'launcher_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('theme', 'light')
            return 'light'
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return 'light'
    
    def get_theme_preview(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get a preview of theme colors"""
        theme = self.get_theme(theme_name)
        if not theme:
            return None
        
        return {
            'name': theme.get('name', theme_name),
            'bg': theme.get('bg', '#000000'),
            'fg': theme.get('fg', '#ffffff'),
            'accent': theme.get('accent', '#007acc'),
            'custom': theme.get('custom', False)
        }
    
    def validate_color(self, color: str) -> bool:
        """Validate if a color string is valid"""
        try:
            if not color.startswith('#'):
                return False
            if len(color) != 7:
                return False
            int(color[1:], 16)
            return True
        except:
            return False
    
    def create_theme_editor_window(self):
        """Create and show the theme editor window with enhanced UX"""
        try:
            editor = ThemeEditorWindow(self)
            editor.show()
            return True
        except Exception as e:
            self.launcher_gui.log(f"[ThemeManager] Error creating theme editor: {e}")
            return False

class ThemeEditorWindow:
    """Theme editor window for creating and editing themes"""
    
    def __init__(self, theme_manager: EnhancedThemeManager):
        self.theme_manager = theme_manager
        self.window = None
        self.current_theme_data = {}
        self.color_vars = {}
        
    def show(self):
        """Show the theme editor window with enhanced accessibility"""
        self.window = tk.Toplevel()
        self.window.title("🎨 Theme Editor - Z-Waifu Launcher")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # Make window modal and center it
        self.window.transient(self.theme_manager.launcher_gui.root)
        self.window.grab_set()
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'launcher_icon.png')
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.window.iconphoto(True, icon)
        except Exception:
            pass
        
        # Add status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.create_interface()
        self.load_theme_list()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Focus on window
        self.window.focus_set()
        
        # Update status
        self.status_var.set("Theme Editor loaded successfully")
        
    def create_interface(self):
        """Create the theme editor interface with enhanced UX"""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and description
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="🎨 Theme Editor", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Create and customize themes for your Z-Waifu Launcher", 
                 font=("Arial", 9), foreground="gray").pack(anchor=tk.W)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Theme list
        left_frame = ttk.LabelFrame(content_frame, text="📋 Available Themes")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Theme listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.theme_listbox = tk.Listbox(list_frame, width=30, height=20, font=("Arial", 9))
        theme_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.theme_listbox.yview)
        self.theme_listbox.configure(yscrollcommand=theme_scrollbar.set)
        
        self.theme_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        theme_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.theme_listbox.bind('<<ListboxSelect>>', self.on_theme_select)
        
        # Theme management buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="🆕 New Theme", command=self.new_theme).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(button_frame, text="📋 Duplicate", command=self.duplicate_theme).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_theme).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Right panel - Color editor
        right_frame = ttk.LabelFrame(content_frame, text="🎨 Color Editor")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Color editor
        self.create_color_editor(right_frame)
        
        # Bottom action buttons
        bottom_frame = ttk.LabelFrame(self.window, text="Actions")
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Left side buttons
        left_buttons = ttk.Frame(bottom_frame)
        left_buttons.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(left_buttons, text="📥 Import Theme", command=self.import_theme).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="📤 Export Theme", command=self.export_theme).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttk.Frame(bottom_frame)
        right_buttons.pack(side=tk.RIGHT, padx=5, pady=5)
        
        ttk.Button(right_buttons, text="💾 Save Theme", command=self.save_theme).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="✅ Apply Theme", command=self.apply_theme).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="❌ Close", command=self.window.destroy).pack(side=tk.LEFT)
        
    def create_color_editor(self, parent):
        """Create the color editor interface with enhanced organization"""
        # Scrollable frame for colors
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Color definitions organized by category
        color_categories = {
            "Basic Colors": [
                ('bg', 'Background'),
                ('fg', 'Foreground'),
            ],
            "Entry Colors": [
                ('entry_bg', 'Entry Background'),
                ('entry_fg', 'Entry Foreground'),
            ],
            "Accent Colors": [
                ('accent', 'Accent Color'),
                ('success', 'Success Color'),
                ('warning', 'Warning Color'),
                ('error', 'Error Color'),
                ('info', 'Info Color'),
            ],
            "Button Colors": [
                ('button_bg', 'Button Background'),
                ('button_fg', 'Button Foreground'),
                ('hover_bg', 'Hover Background'),
                ('hover_fg', 'Hover Foreground'),
            ],
            "Border & Text": [
                ('border_color', 'Border Color'),
                ('text_bg', 'Text Background'),
                ('text_fg', 'Text Foreground'),
            ],
            "Component Colors": [
                ('canvas_bg', 'Canvas Background'),
                ('listbox_bg', 'Listbox Background'),
                ('listbox_fg', 'Listbox Foreground'),
                ('select_bg', 'Selection Background'),
                ('select_fg', 'Selection Foreground')
            ]
        }
        
        # Create color entries organized by category
        for category, colors in color_categories.items():
            # Category header
            category_frame = ttk.LabelFrame(scrollable_frame, text=f"📁 {category}")
            category_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
            
            for key, label in colors:
                frame = ttk.Frame(category_frame)
                frame.pack(fill=tk.X, pady=2, padx=5)
                
                # Label with tooltip-like description
                label_frame = ttk.Frame(frame)
                label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                ttk.Label(label_frame, text=label, font=("Arial", 9)).pack(anchor=tk.W)
                
                # Color input frame
                color_frame = ttk.Frame(frame)
                color_frame.pack(side=tk.RIGHT)
                
                var = tk.StringVar(value='#000000')
                self.color_vars[key] = var
                
                # Color entry with validation
                entry = ttk.Entry(color_frame, textvariable=var, width=10, font=("Arial", 9))
                entry.pack(side=tk.LEFT, padx=(5, 5))
                entry.bind('<FocusOut>', lambda e, k=key: self.validate_color_entry(k))
                
                # Color picker button
                color_button = tk.Button(color_frame, text="🎨", width=4, height=1,
                                       command=lambda k=key: self.choose_color(k),
                                       font=("Arial", 8))
                color_button.pack(side=tk.LEFT)
                
                # Store button reference for color updates
                setattr(self, f'color_button_{key}', color_button)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def choose_color(self, color_key):
        """Open color chooser for a specific color with enhanced feedback"""
        try:
            current_color = self.color_vars[color_key].get()
            color = colorchooser.askcolor(color=current_color, title=f"Choose {color_key} color")
            if color[1]:
                self.color_vars[color_key].set(color[1])
                self.update_color_preview(color_key, color[1])
                self.status_var.set(f"Color {color_key} updated to {color[1]}")
        except Exception as e:
            self.status_var.set(f"Error choosing color: {e}")

    def validate_color_entry(self, color_key):
        """Validate color entry and provide feedback"""
        try:
            color_value = self.color_vars[color_key].get()
            if self.theme_manager.validate_color(color_value):
                self.update_color_preview(color_key, color_value)
                self.status_var.set(f"Color {color_key} validated: {color_value}")
            else:
                # Reset to a valid color if invalid
                self.color_vars[color_key].set('#000000')
                self.update_color_preview(color_key, '#000000')
                self.status_var.set(f"Invalid color format for {color_key}, reset to default")
        except Exception as e:
            self.status_var.set(f"Error validating color: {e}")
    
    def update_color_preview(self, color_key, color_value):
        """Update color preview button"""
        button = getattr(self, f'color_button_{color_key}', None)
        if button:
            button.configure(bg=color_value)
    
    def load_theme_list(self):
        """Load available themes into the listbox with enhanced display"""
        try:
            self.theme_listbox.delete(0, tk.END)
            all_themes = self.theme_manager.get_all_themes()
            
            for theme_name in sorted(all_themes.keys()):
                theme = all_themes[theme_name]
                is_custom = theme.get('custom', False)
                is_current = theme_name == self.theme_manager.load_theme_preference()
                
                # Create display name with indicators
                display_name = f"{theme['name']}"
                if is_custom:
                    display_name += " (Custom)"
                if is_current:
                    display_name += " ✓"
                
                self.theme_listbox.insert(tk.END, display_name)
                
                # Set background color based on theme
                bg_color = theme.get('bg', '#ffffff')
                fg_color = theme.get('fg', '#000000')
                
                # Ensure good contrast for listbox items
                if bg_color.lower() in ['#ffffff', '#f0f0f0', '#e0e0e0']:
                    item_bg = bg_color
                    item_fg = fg_color
                else:
                    item_bg = '#f0f0f0'
                    item_fg = '#000000'
                
                self.theme_listbox.itemconfig(tk.END, {
                    'bg': item_bg,
                    'fg': item_fg
                })
            
            # Select current theme if available
            current_theme = self.theme_manager.load_theme_preference()
            all_theme_names = sorted(all_themes.keys())
            if current_theme in all_theme_names:
                current_index = all_theme_names.index(current_theme)
                self.theme_listbox.selection_set(current_index)
                self.theme_listbox.see(current_index)
            
            self.status_var.set(f"Loaded {len(all_themes)} themes")
            
        except Exception as e:
            self.status_var.set(f"Error loading themes: {e}")
    
    def on_theme_select(self, event):
        """Handle theme selection with enhanced feedback"""
        try:
            selection = self.theme_listbox.curselection()
            if not selection:
                return
            
            # Get theme name from selection
            all_themes = self.theme_manager.get_all_themes()
            theme_names = sorted(all_themes.keys())
            selected_theme = theme_names[selection[0]]
            
            # Load theme data
            theme_data = all_themes[selected_theme]
            self.load_theme_data(selected_theme, theme_data)
            
            # Update status
            theme_name = theme_data.get('name', selected_theme)
            self.status_var.set(f"Selected theme: {theme_name}")
            
        except Exception as e:
            self.status_var.set(f"Error selecting theme: {e}")
    
    def load_theme_data(self, theme_name, theme_data):
        """Load theme data into the editor with enhanced feedback"""
        try:
            self.current_theme_data = theme_data.copy()
            self.current_theme_data['name'] = theme_name
            
            # Update color variables
            for key, var in self.color_vars.items():
                if key in theme_data:
                    var.set(theme_data[key])
                    self.update_color_preview(key, theme_data[key])
                else:
                    # Set default color if not present
                    default_color = '#000000' if key == 'fg' else '#ffffff'
                    var.set(default_color)
                    self.update_color_preview(key, default_color)
            
            # Update status
            theme_name_display = theme_data.get('name', theme_name)
            self.status_var.set(f"Loaded theme: {theme_name_display}")
            
        except Exception as e:
            self.status_var.set(f"Error loading theme data: {e}")
    
    def update_preview(self):
        """Update the theme preview"""
        # This could show a preview of how the theme would look
        # For now, just update the color buttons
        for key, var in self.color_vars.items():
            color = var.get()
            if self.theme_manager.validate_color(color):
                self.update_color_preview(key, color)
    
    def new_theme(self):
        """Create a new theme"""
        name = tk.simpledialog.askstring("New Theme", "Enter theme name:")
        if name:
            # Start with current theme colors
            colors = {}
            for key, var in self.color_vars.items():
                colors[key] = var.get()
            
            if self.theme_manager.create_custom_theme(name, colors):
                self.load_theme_list()
                messagebox.showinfo("Success", f"Theme '{name}' created successfully!")
            else:
                messagebox.showerror("Error", "Failed to create theme!")
    
    def duplicate_theme(self):
        """Duplicate the selected theme"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a theme to duplicate!")
            return
        
        all_themes = self.theme_manager.get_all_themes()
        theme_names = sorted(all_themes.keys())
        selected_theme = theme_names[selection[0]]
        
        new_name = tk.simpledialog.askstring("Duplicate Theme", 
                                           f"Enter name for duplicate of '{selected_theme}':")
        if new_name:
            theme_data = all_themes[selected_theme].copy()
            theme_data['name'] = new_name
            
            if self.theme_manager.create_custom_theme(new_name, theme_data):
                self.load_theme_list()
                messagebox.showinfo("Success", f"Theme '{new_name}' created successfully!")
            else:
                messagebox.showerror("Error", "Failed to create theme!")
    
    def delete_theme(self):
        """Delete the selected theme"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a theme to delete!")
            return
        
        all_themes = self.theme_manager.get_all_themes()
        theme_names = sorted(all_themes.keys())
        selected_theme = theme_names[selection[0]]
        
        if selected_theme in self.theme_manager.default_themes:
            messagebox.showwarning("Warning", "Cannot delete default themes!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_theme}'?"):
            if self.theme_manager.delete_custom_theme(selected_theme):
                self.load_theme_list()
                messagebox.showinfo("Success", f"Theme '{selected_theme}' deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete theme!")
    
    def import_theme(self):
        """Import a theme from file"""
        filepath = tk.filedialog.askopenfilename(
            title="Import Theme",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            if self.theme_manager.import_theme(filepath):
                self.load_theme_list()
                messagebox.showinfo("Success", "Theme imported successfully!")
            else:
                messagebox.showerror("Error", "Failed to import theme!")
    
    def export_theme(self):
        """Export the selected theme"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a theme to export!")
            return
        
        all_themes = self.theme_manager.get_all_themes()
        theme_names = sorted(all_themes.keys())
        selected_theme = theme_names[selection[0]]
        
        filepath = tk.filedialog.asksaveasfilename(
            title="Export Theme",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            if self.theme_manager.export_theme(selected_theme, filepath):
                messagebox.showinfo("Success", f"Theme exported to {filepath}")
            else:
                messagebox.showerror("Error", "Failed to export theme!")
    
    def save_theme(self):
        """Save the current theme"""
        if not self.current_theme_data:
            messagebox.showwarning("Warning", "No theme selected!")
            return
        
        # Collect current colors
        colors = {}
        for key, var in self.color_vars.items():
            colors[key] = var.get()
        
        theme_name = self.current_theme_data.get('name', '')
        
        if theme_name in self.theme_manager.default_themes:
            # Create a custom copy
            new_name = tk.simpledialog.askstring("Save Theme", 
                                               f"Enter name for custom copy of '{theme_name}':")
            if new_name:
                if self.theme_manager.create_custom_theme(new_name, colors):
                    self.load_theme_list()
                    messagebox.showinfo("Success", f"Theme '{new_name}' saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save theme!")
        else:
            # Update existing custom theme
            if self.theme_manager.update_custom_theme(theme_name, colors):
                self.load_theme_list()
                messagebox.showinfo("Success", f"Theme '{theme_name}' updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update theme!")
    
    def apply_theme(self):
        """Apply the current theme"""
        if not self.current_theme_data:
            messagebox.showwarning("Warning", "No theme selected!")
            return
        
        theme_name = self.current_theme_data.get('name', '')
        
        if self.theme_manager.apply_theme(theme_name):
            messagebox.showinfo("Success", f"Theme '{theme_name}' applied successfully!")
        else:
            messagebox.showerror("Error", "Failed to apply theme!") 