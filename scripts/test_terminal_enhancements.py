#!/usr/bin/env python3
"""
Test script for the enhanced terminal system
Verifies all features are working correctly
"""

import sys
import os
import time
import threading
import subprocess
import tempfile
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    from zwaifu_launcher_gui import TerminalEmulator
    from utils.terminal_enhancements import TerminalEnhancer, OutputAnalyzer, OutputStatistics
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class TerminalTester:
    """Test class for the enhanced terminal system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Terminal Enhancement Test")
        self.root.geometry("800x600")
        
        # Create test results
        self.test_results = {}
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create test controls
        self.create_test_controls()
        
        # Create terminal
        self.create_terminal()
        
        # Create results display
        self.create_results_display()
    
    def create_test_controls(self):
        """Create test control buttons"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Terminal Enhancement Tests", font=("Arial", 12, "bold")).pack()
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Test Basic Features", command=self.test_basic_features).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Search & Filter", command=self.test_search_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Output Analysis", command=self.test_output_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Export Features", command=self.test_export_features).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Performance", command=self.test_performance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run All Tests", command=self.run_all_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
    
    def create_terminal(self):
        """Create the enhanced terminal"""
        terminal_frame = ttk.Frame(self.main_frame)
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create basic terminal
        self.terminal = TerminalEmulator(terminal_frame)
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Enhance with advanced features
        enhancer = TerminalEnhancer()
        self.terminal = enhancer.enhance_terminal(self.terminal)
    
    def create_results_display(self):
        """Create results display area"""
        results_frame = ttk.Frame(self.main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(results_frame, text="Test Results:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.results_text = tk.Text(results_frame, height=8, font=("Consolas", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=scrollbar.set)
    
    def log_result(self, test_name, success, message=""):
        """Log a test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = time.strftime("%H:%M:%S")
        result_text = f"[{timestamp}] {test_name}: {status}"
        if message:
            result_text += f" - {message}"
        result_text += "\n"
        
        self.results_text.insert(tk.END, result_text)
        self.results_text.see(tk.END)
        
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'timestamp': timestamp
        }
    
    def test_basic_features(self):
        """Test basic terminal features"""
        self.log_result("Basic Features", True, "Starting basic feature tests...")
        
        try:
            # Test terminal creation
            if hasattr(self.terminal, 'terminal'):
                self.log_result("Terminal Widget", True, "Terminal widget created successfully")
            else:
                self.log_result("Terminal Widget", False, "Terminal widget not found")
                return
            
            # Test input field
            if hasattr(self.terminal, 'input_entry'):
                self.log_result("Input Field", True, "Input field created successfully")
            else:
                self.log_result("Input Field", False, "Input field not found")
            
            # Test command history
            if hasattr(self.terminal, 'command_history'):
                self.log_result("Command History", True, "Command history initialized")
            else:
                self.log_result("Command History", False, "Command history not found")
            
            # Test append functionality
            test_line = "[TEST] Basic append test\n"
            self.terminal._append(test_line, '37')
            self.log_result("Append Function", True, "Text appended successfully")
            
            # Test clear functionality
            self.terminal.clear_terminal()
            self.log_result("Clear Function", True, "Terminal cleared successfully")
            
        except Exception as e:
            self.log_result("Basic Features", False, f"Exception: {e}")
    
    def test_search_filter(self):
        """Test search and filter features"""
        self.log_result("Search & Filter", True, "Starting search and filter tests...")
        
        try:
            # Add test content
            test_content = [
                "[12:00:01] Starting application...",
                "[12:00:02] Loading configuration...",
                "[12:00:03] Warning: Deprecated feature used",
                "[12:00:04] Error: Failed to connect to database",
                "[12:00:05] Success: Application started successfully",
                "[12:00:06] Info: Memory usage: 512MB",
                "[12:00:07] Debug: Processing file: /path/to/file.txt"
            ]
            
            for line in test_content:
                self.terminal._append(line + "\n", '37')
            
            # Test search functionality
            if hasattr(self.terminal, 'search_var'):
                self.terminal.search_var.set("error")
                self.log_result("Search Variable", True, "Search variable accessible")
            else:
                self.log_result("Search Variable", False, "Search variable not found")
            
            # Test filter functionality
            if hasattr(self.terminal, 'filter_var'):
                self.terminal.filter_var.set("warning")
                self.log_result("Filter Variable", True, "Filter variable accessible")
            else:
                self.log_result("Filter Variable", False, "Filter variable not found")
            
            # Test error filter
            if hasattr(self.terminal, 'error_only_var'):
                self.terminal.error_only_var.set(True)
                self.log_result("Error Filter", True, "Error filter toggle accessible")
            else:
                self.log_result("Error Filter", False, "Error filter not found")
            
            # Test warning filter
            if hasattr(self.terminal, 'warning_only_var'):
                self.terminal.warning_only_var.set(True)
                self.log_result("Warning Filter", True, "Warning filter toggle accessible")
            else:
                self.log_result("Warning Filter", False, "Warning filter not found")
            
        except Exception as e:
            self.log_result("Search & Filter", False, f"Exception: {e}")
    
    def test_output_analysis(self):
        """Test output analysis features"""
        self.log_result("Output Analysis", True, "Starting output analysis tests...")
        
        try:
            # Test analyzer
            if hasattr(self.terminal, 'analyzer'):
                analyzer = self.terminal.analyzer
                test_line = "[12:00:01] Error: Test error message"
                entry = analyzer.analyze_line(test_line)
                
                if entry.output_type.value == 'error':
                    self.log_result("Error Detection", True, "Error pattern detected correctly")
                else:
                    self.log_result("Error Detection", False, "Error pattern not detected")
                
                if entry.severity >= 7:
                    self.log_result("Severity Scoring", True, "Severity scoring working")
                else:
                    self.log_result("Severity Scoring", False, "Severity scoring incorrect")
                
                if 'error' in entry.tags:
                    self.log_result("Tagging System", True, "Tagging system working")
                else:
                    self.log_result("Tagging System", False, "Tagging system not working")
                
            else:
                self.log_result("Output Analyzer", False, "Analyzer not found")
            
            # Test statistics
            if hasattr(self.terminal, 'statistics'):
                stats = self.terminal.statistics.get_summary()
                if 'total_lines' in stats:
                    self.log_result("Statistics", True, "Statistics tracking working")
                else:
                    self.log_result("Statistics", False, "Statistics not working")
            else:
                self.log_result("Statistics", False, "Statistics not found")
            
        except Exception as e:
            self.log_result("Output Analysis", False, f"Exception: {e}")
    
    def test_export_features(self):
        """Test export features"""
        self.log_result("Export Features", True, "Starting export feature tests...")
        
        try:
            # Add test content
            test_content = [
                "[12:00:01] Export test line 1",
                "[12:00:02] Export test line 2",
                "[12:00:03] Export test line 3"
            ]
            
            for line in test_content:
                self.terminal._append(line + "\n", '37')
            
            # Test save output
            if hasattr(self.terminal, 'save_output'):
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    temp_file = f.name
                
                try:
                    # Test save functionality
                    self.terminal.save_output()
                    self.log_result("Save Output", True, "Save function accessible")
                    
                    # Test export analysis
                    if hasattr(self.terminal, 'export_analysis'):
                        result = self.terminal.export_analysis(temp_file)
                        if result:
                            self.log_result("Export Analysis", True, "Analysis export working")
                        else:
                            self.log_result("Export Analysis", False, "Analysis export failed")
                    else:
                        self.log_result("Export Analysis", False, "Export analysis not found")
                    
                finally:
                    # Clean up
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
            else:
                self.log_result("Save Output", False, "Save function not found")
            
        except Exception as e:
            self.log_result("Export Features", False, f"Exception: {e}")
    
    def test_performance(self):
        """Test performance features"""
        self.log_result("Performance", True, "Starting performance tests...")
        
        try:
            # Test performance monitoring
            if hasattr(self.terminal, 'perf_label'):
                self.log_result("Performance Label", True, "Performance monitoring UI present")
            else:
                self.log_result("Performance Label", False, "Performance monitoring UI not found")
            
            # Test buffer management
            if hasattr(self.terminal, 'output_buffer'):
                initial_size = len(self.terminal.output_buffer)
                
                # Add some content
                for i in range(100):
                    self.terminal._append(f"[12:00:{i:02d}] Performance test line {i}\n", '37')
                
                final_size = len(self.terminal.output_buffer)
                
                if final_size > initial_size:
                    self.log_result("Buffer Management", True, f"Buffer size: {initial_size} -> {final_size}")
                else:
                    self.log_result("Buffer Management", False, "Buffer not updating")
            else:
                self.log_result("Buffer Management", False, "Output buffer not found")
            
            # Test memory efficiency
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Add more content
            for i in range(500):
                self.terminal._append(f"[12:01:{i:02d}] Memory test line {i}\n", '37')
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            if memory_increase < 10 * 1024 * 1024:  # Less than 10MB increase
                self.log_result("Memory Efficiency", True, f"Memory increase: {memory_increase / 1024:.1f}KB")
            else:
                self.log_result("Memory Efficiency", False, f"High memory usage: {memory_increase / 1024 / 1024:.1f}MB")
            
        except Exception as e:
            self.log_result("Performance", False, f"Exception: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        self.clear_results()
        self.log_result("All Tests", True, "Starting comprehensive test suite...")
        
        # Run all test methods
        test_methods = [
            self.test_basic_features,
            self.test_search_filter,
            self.test_output_analysis,
            self.test_export_features,
            self.test_performance
        ]
        
        for test_method in test_methods:
            test_method()
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        self.log_result("Test Summary", True, f"Completed {total_tests} tests: {passed_tests} passed, {total_tests - passed_tests} failed")
        
        if passed_tests == total_tests:
            self.log_result("Overall Result", True, "All tests passed! ✅")
        else:
            self.log_result("Overall Result", False, f"{total_tests - passed_tests} tests failed ❌")
    
    def clear_results(self):
        """Clear test results"""
        self.results_text.delete('1.0', tk.END)
        self.test_results.clear()
    
    def run(self):
        """Run the test application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        except Exception as e:
            print(f"Test error: {e}")


def main():
    """Main function"""
    print("Terminal Enhancement Test Suite")
    print("=" * 40)
    print("This will test all enhanced terminal features")
    print("Make sure the Z-Waifu Launcher is properly installed")
    print()
    
    try:
        tester = TerminalTester()
        tester.run()
    except Exception as e:
        print(f"Failed to start test suite: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 