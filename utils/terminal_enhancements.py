"""
Terminal Enhancement Utilities
Advanced features for the Z-Waifu Launcher terminal system
"""

import re
import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox
import queue


class OutputType(Enum):
    """Types of output that can be detected"""
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    INFO = "info"
    DEBUG = "debug"
    COMMAND = "command"
    OUTPUT = "output"
    UNKNOWN = "unknown"


@dataclass
class OutputEntry:
    """Enhanced output entry with metadata"""
    timestamp: float
    line: str
    stream: str
    original: str
    output_type: OutputType
    severity: int  # 0-10 scale
    tags: List[str]
    metadata: Dict[str, Any]


class OutputAnalyzer:
    """Analyzes terminal output for patterns and metadata"""
    
    def __init__(self):
        self.patterns = {
            'error': [
                r'error|exception|failed|failure|crash|abort|panic',
                r'\[ERROR\]|\[ERR\]|\[FATAL\]',
                r'Traceback|Exception|Error:',
                r'return code [1-9]|exit code [1-9]'
            ],
            'warning': [
                r'warning|warn|deprecated|deprecation',
                r'\[WARNING\]|\[WARN\]',
                r'Warning:|Deprecated:'
            ],
            'success': [
                r'success|successful|completed|done|finished|ready',
                r'\[SUCCESS\]|\[OK\]|\[DONE\]',
                r'Success:|Completed:'
            ],
            'info': [
                r'info|information|note|notice',
                r'\[INFO\]|\[NOTE\]',
                r'Info:|Note:'
            ],
            'debug': [
                r'debug|trace|verbose',
                r'\[DEBUG\]|\[TRACE\]',
                r'Debug:|Trace:'
            ],
            'command': [
                r'^\s*>\s+',  # Command prompt
                r'^\s*\$\s+',  # Shell prompt
                r'^\s*#\s+',   # Comment
                r'^\s*\[.*\]\s*$'  # Timestamp line
            ]
        }
        
        self.compiled_patterns = {}
        for category, pattern_list in self.patterns.items():
            self.compiled_patterns[category] = [re.compile(p, re.IGNORECASE) for p in pattern_list]
    
    def analyze_line(self, line: str, stream: str = 'stdout') -> OutputEntry:
        """Analyze a single line of output"""
        try:
            # Determine output type
            output_type = self._detect_output_type(line)
            
            # Calculate severity
            severity = self._calculate_severity(line, output_type)
            
            # Extract tags
            tags = self._extract_tags(line)
            
            # Extract metadata
            metadata = self._extract_metadata(line, stream)
            
            return OutputEntry(
                timestamp=time.time(),
                line=line,
                stream=stream,
                original=line,
                output_type=output_type,
                severity=severity,
                tags=tags,
                metadata=metadata
            )
        except Exception as e:
            print(f"Error analyzing line: {e}")
            return OutputEntry(
                timestamp=time.time(),
                line=line,
                stream=stream,
                original=line,
                output_type=OutputType.UNKNOWN,
                severity=0,
                tags=[],
                metadata={'error': str(e)}
            )
    
    def _detect_output_type(self, line: str) -> OutputType:
        """Detect the type of output based on patterns"""
        try:
            line_lower = line.lower()
            
            # Check each pattern category
            for category, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    if pattern.search(line):
                        return OutputType(category)
            
            # Default to output type
            return OutputType.OUTPUT
        except Exception as e:
            print(f"Error detecting output type: {e}")
            return OutputType.UNKNOWN
    
    def _calculate_severity(self, line: str, output_type: OutputType) -> int:
        """Calculate severity level (0-10)"""
        try:
            base_severity = {
                OutputType.ERROR: 8,
                OutputType.WARNING: 5,
                OutputType.SUCCESS: 2,
                OutputType.INFO: 3,
                OutputType.DEBUG: 1,
                OutputType.COMMAND: 0,
                OutputType.OUTPUT: 0,
                OutputType.UNKNOWN: 0
            }
            
            severity = base_severity.get(output_type, 0)
            
            # Adjust based on keywords
            if 'fatal' in line.lower() or 'critical' in line.lower():
                severity = 10
            elif 'severe' in line.lower():
                severity = 9
            elif 'minor' in line.lower() or 'trivial' in line.lower():
                severity = max(0, severity - 2)
            
            return severity
        except Exception as e:
            print(f"Error calculating severity: {e}")
            return 0
    
    def _extract_tags(self, line: str) -> List[str]:
        """Extract tags from the line"""
        try:
            tags = []
            
            # Extract common tags
            if 'loading' in line.lower():
                tags.append('loading')
            if 'initializing' in line.lower():
                tags.append('initialization')
            if 'connecting' in line.lower():
                tags.append('connection')
            if 'downloading' in line.lower():
                tags.append('download')
            if 'uploading' in line.lower():
                tags.append('upload')
            if 'processing' in line.lower():
                tags.append('processing')
            if 'memory' in line.lower():
                tags.append('memory')
            if 'cpu' in line.lower():
                tags.append('cpu')
            if 'network' in line.lower():
                tags.append('network')
            if 'file' in line.lower():
                tags.append('file')
            if 'database' in line.lower():
                tags.append('database')
            
            return tags
        except Exception as e:
            print(f"Error extracting tags: {e}")
            return []
    
    def _extract_metadata(self, line: str, stream: str) -> Dict[str, Any]:
        """Extract metadata from the line"""
        try:
            metadata = {
                'stream': stream,
                'length': len(line),
                'has_timestamp': bool(re.search(r'\[\d{2}:\d{2}:\d{2}\]', line)),
                'has_numbers': bool(re.search(r'\d+', line)),
                'has_urls': bool(re.search(r'https?://', line)),
                'has_paths': bool(re.search(r'[\\/][^\\/\s]+[\\/]', line))
            }
            
            # Extract numbers
            numbers = re.findall(r'\d+', line)
            if numbers:
                metadata['numbers'] = [int(n) for n in numbers]
            
            # Extract URLs
            urls = re.findall(r'https?://[^\s]+', line)
            if urls:
                metadata['urls'] = urls
            
            # Extract file paths
            paths = re.findall(r'[\\/][^\\/\s]+[\\/][^\\/\s]+', line)
            if paths:
                metadata['paths'] = paths
            
            return metadata
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {'stream': stream, 'length': len(line), 'error': str(e)}


class SyntaxHighlighter:
    """Provides syntax highlighting for terminal output"""
    
    def __init__(self):
        self.colors = {
            'error': '#ff6b6b',
            'warning': '#ffd93d',
            'success': '#6bcf7f',
            'info': '#4dabf7',
            'debug': '#adb5bd',
            'command': '#ffa726',
            'output': '#ffffff',
            'unknown': '#ffffff'
        }
        
        self.tags_configured = False
    
    def configure_tags(self, text_widget: tk.Text):
        """Configure color tags for the text widget"""
        try:
            if not self.tags_configured:
                for output_type, color in self.colors.items():
                    text_widget.tag_configure(output_type, foreground=color)
                self.tags_configured = True
        except Exception as e:
            print(f"Error configuring tags: {e}")
    
    def highlight_text(self, text_widget: tk.Text, start_pos: str, end_pos: str):
        """Apply syntax highlighting to text"""
        try:
            self.configure_tags(text_widget)
            
            # Get the text to highlight
            text = text_widget.get(start_pos, end_pos)
            
            # Analyze each line
            analyzer = OutputAnalyzer()
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip():
                    entry = analyzer.analyze_line(line)
                    tag = entry.output_type.value
                    
                    # Calculate line position
                    line_start = f"{start_pos}+{i}l"
                    line_end = f"{start_pos}+{i+1}l"
                    
                    # Apply tag
                    text_widget.tag_add(tag, line_start, line_end)
        except Exception as e:
            print(f"Error highlighting text: {e}")


class OutputFilter:
    """Filters output entries based on various criteria"""
    
    def __init__(self):
        self.filters = {}
        self.enabled_filters = set()
        self.create_builtin_filters()
    
    def add_filter(self, name: str, filter_func: Callable[[OutputEntry], bool], description: str = ""):
        """Add a custom filter"""
        try:
            self.filters[name] = {
                'function': filter_func,
                'description': description,
                'enabled': False
            }
        except Exception as e:
            print(f"Error adding filter: {e}")
    
    def remove_filter(self, name: str):
        """Remove a filter"""
        try:
            if name in self.filters:
                del self.filters[name]
                self.enabled_filters.discard(name)
        except Exception as e:
            print(f"Error removing filter: {e}")
    
    def enable_filter(self, name: str):
        """Enable a filter"""
        try:
            if name in self.filters:
                self.filters[name]['enabled'] = True
                self.enabled_filters.add(name)
        except Exception as e:
            print(f"Error enabling filter: {e}")
    
    def disable_filter(self, name: str):
        """Disable a filter"""
        try:
            if name in self.filters:
                self.filters[name]['enabled'] = False
                self.enabled_filters.discard(name)
        except Exception as e:
            print(f"Error disabling filter: {e}")
    
    def apply_filters(self, entries: List[OutputEntry]) -> List[OutputEntry]:
        """Apply all enabled filters to entries"""
        try:
            filtered_entries = entries
            
            for name in self.enabled_filters:
                if name in self.filters:
                    filter_func = self.filters[name]['function']
                    filtered_entries = [entry for entry in filtered_entries if filter_func(entry)]
            
            return filtered_entries
        except Exception as e:
            print(f"Error applying filters: {e}")
            return entries
    
    def create_builtin_filters(self):
        """Create built-in filters"""
        try:
            # Error filter
            self.add_filter(
                'errors_only',
                lambda entry: entry.output_type == OutputType.ERROR,
                'Show only error messages'
            )
            
            # Warning filter
            self.add_filter(
                'warnings_only',
                lambda entry: entry.output_type == OutputType.WARNING,
                'Show only warning messages'
            )
            
            # High severity filter
            self.add_filter(
                'high_severity',
                lambda entry: entry.severity >= 7,
                'Show only high severity messages'
            )
            
            # Command filter
            self.add_filter(
                'commands_only',
                lambda entry: entry.output_type == OutputType.COMMAND,
                'Show only command lines'
            )
            
            # Success filter
            self.add_filter(
                'success_only',
                lambda entry: entry.output_type == OutputType.SUCCESS,
                'Show only success messages'
            )
            
            # Info filter
            self.add_filter(
                'info_only',
                lambda entry: entry.output_type == OutputType.INFO,
                'Show only info messages'
            )
        except Exception as e:
            print(f"Error creating built-in filters: {e}")


class OutputStatistics:
    """Collects and provides statistics about output"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all statistics"""
        try:
            self.total_lines = 0
            self.error_count = 0
            self.warning_count = 0
            self.success_count = 0
            self.info_count = 0
            self.debug_count = 0
            self.command_count = 0
            self.output_count = 0
            self.unknown_count = 0
            self.severity_sum = 0
            self.tag_counts = {}
            self.stream_counts = {'stdout': 0, 'stderr': 0}
        except Exception as e:
            print(f"Error resetting statistics: {e}")
    
    def update(self, entry: OutputEntry):
        """Update statistics with a new entry"""
        try:
            self.total_lines += 1
            self.severity_sum += entry.severity
            
            # Count by output type
            if entry.output_type == OutputType.ERROR:
                self.error_count += 1
            elif entry.output_type == OutputType.WARNING:
                self.warning_count += 1
            elif entry.output_type == OutputType.SUCCESS:
                self.success_count += 1
            elif entry.output_type == OutputType.INFO:
                self.info_count += 1
            elif entry.output_type == OutputType.DEBUG:
                self.debug_count += 1
            elif entry.output_type == OutputType.COMMAND:
                self.command_count += 1
            elif entry.output_type == OutputType.OUTPUT:
                self.output_count += 1
            else:
                self.unknown_count += 1
            
            # Count by stream
            if entry.stream in self.stream_counts:
                self.stream_counts[entry.stream] += 1
            
            # Count tags
            for tag in entry.tags:
                self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of statistics"""
        try:
            avg_severity = self.severity_sum / max(self.total_lines, 1)
            
            return {
                'total_lines': self.total_lines,
                'error_count': self.error_count,
                'warning_count': self.warning_count,
                'success_count': self.success_count,
                'info_count': self.info_count,
                'debug_count': self.debug_count,
                'command_count': self.command_count,
                'output_count': self.output_count,
                'unknown_count': self.unknown_count,
                'average_severity': round(avg_severity, 2),
                'stream_counts': self.stream_counts,
                'tag_counts': self.tag_counts
            }
        except Exception as e:
            print(f"Error getting statistics summary: {e}")
            return {}


class TerminalEnhancer:
    """Main class for enhancing terminal functionality"""
    
    def __init__(self):
        self.analyzer = OutputAnalyzer()
        self.highlighter = SyntaxHighlighter()
        self.filter = OutputFilter()
        self.statistics = OutputStatistics()
    
    def analyze_output(self, line: str, stream: str = 'stdout') -> OutputEntry:
        """Analyze a line of output"""
        try:
            entry = self.analyzer.analyze_line(line, stream)
            self.statistics.update(entry)
            return entry
        except Exception as e:
            print(f"Error analyzing output: {e}")
            return OutputEntry(
                timestamp=time.time(),
                line=line,
                stream=stream,
                original=line,
                output_type=OutputType.UNKNOWN,
                severity=0,
                tags=[],
                metadata={'error': str(e)}
            )
    
    def enhance_terminal(self, terminal_widget):
        """Enhance a terminal widget with advanced features"""
        try:
            # Store original append method
            original_append = terminal_widget._append
            
            def enhanced_append(text, color_code):
                # Analyze the line
                entry = self.analyzer.analyze_line(text)
                self.statistics.update(entry)
                
                # Use appropriate color based on analysis
                if entry.output_type == OutputType.ERROR:
                    color_tag = 'error'
                elif entry.output_type == OutputType.WARNING:
                    color_tag = 'warning'
                elif entry.output_type == OutputType.SUCCESS:
                    color_tag = 'success'
                elif entry.output_type == OutputType.INFO:
                    color_tag = 'info'
                elif entry.output_type == OutputType.DEBUG:
                    color_tag = 'debug'
                elif entry.output_type == OutputType.COMMAND:
                    color_tag = 'command'
                else:
                    color_tag = 'output'
                
                # Configure tags if needed
                self.highlighter.configure_tags(terminal_widget)
                
                # Call original append with enhanced color
                original_append(text, color_tag)
            
            # Replace the append method
            terminal_widget._append = enhanced_append
            
            return terminal_widget
        except Exception as e:
            print(f"Error enhancing terminal: {e}")
            return terminal_widget
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics"""
        try:
            return self.statistics.get_summary()
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def reset_statistics(self):
        """Reset statistics"""
        try:
            self.statistics.reset()
        except Exception as e:
            print(f"Error resetting statistics: {e}")
    
    def export_analysis(self, filename: str):
        """Export analysis data to file"""
        try:
            data = {
                'statistics': self.statistics.get_summary(),
                'filters': {name: info['description'] for name, info in self.filter.filters.items()},
                'enabled_filters': list(self.filter.enabled_filters),
                'export_time': time.time()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error exporting analysis: {e}")


def create_enhanced_terminal(parent) -> tk.Frame:
    """Create an enhanced terminal widget"""
    try:
        enhancer = TerminalEnhancer()
        terminal_frame = tk.Frame(parent)
        
        # Create text widget
        text_widget = tk.Text(terminal_frame, wrap=tk.WORD, bg='#1e1e1e', fg='#ffffff')
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Enhance the terminal
        enhancer.enhance_terminal(text_widget)
        
        return terminal_frame
    except Exception as e:
        print(f"Error creating enhanced terminal: {e}")
        return tk.Frame(parent)


def analyze_output_file(filename: str) -> Dict[str, Any]:
    """Analyze an output file and return statistics"""
    try:
        enhancer = TerminalEnhancer()
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                enhancer.analyze_output(line.strip())
        
        return enhancer.get_statistics()
    except Exception as e:
        print(f"Error analyzing output file: {e}")
        return {}


def create_filter_dialog(parent) -> tk.Toplevel:
    """Create a dialog for managing filters"""
    try:
        dialog = tk.Toplevel(parent)
        dialog.title("Output Filters")
        dialog.geometry("400x300")
        
        # Create filter list
        filter_frame = tk.Frame(dialog)
        filter_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Available Filters:").pack(anchor=tk.W)
        
        # Create listbox for filters
        filter_listbox = tk.Listbox(filter_frame, height=10)
        filter_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Create buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def enable_selected_filter():
            selection = filter_listbox.curselection()
            if selection:
                filter_name = filter_listbox.get(selection[0])
                # Enable filter logic here
        
        def disable_selected_filter():
            selection = filter_listbox.curselection()
            if selection:
                filter_name = filter_listbox.get(selection[0])
                # Disable filter logic here
        
        tk.Button(button_frame, text="Enable", command=enable_selected_filter).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Disable", command=disable_selected_filter).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        return dialog
    except Exception as e:
        print(f"Error creating filter dialog: {e}")
        return tk.Toplevel(parent) 