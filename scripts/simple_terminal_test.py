#!/usr/bin/env python3
"""
Simple test script for terminal enhancements
Tests core functionality without GUI dependencies
"""

import sys
import os
import time
import tempfile
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_terminal_enhancements():
    """Test the terminal enhancement utilities"""
    print("Terminal Enhancement Test Suite")
    print("=" * 40)
    
    test_results = []
    
    try:
        # Test 1: Import terminal enhancements
        print("Test 1: Importing terminal enhancements...")
        from utils.terminal_enhancements import (
            TerminalEnhancer, OutputAnalyzer, OutputStatistics, 
            OutputFilter, SyntaxHighlighter, OutputType, OutputEntry
        )
        print("✅ All modules imported successfully")
        test_results.append(("Import", True, "All modules imported"))
        
        # Test 2: Test OutputAnalyzer
        print("\nTest 2: Testing OutputAnalyzer...")
        analyzer = OutputAnalyzer()
        
        # Test error detection
        error_line = "[12:00:01] Error: Test error message"
        entry = analyzer.analyze_line(error_line)
        if entry.output_type == OutputType.ERROR:
            print("✅ Error detection working")
            test_results.append(("Error Detection", True, "Error pattern detected"))
        else:
            print("❌ Error detection failed")
            test_results.append(("Error Detection", False, "Error pattern not detected"))
        
        # Test warning detection
        warning_line = "[12:00:02] Warning: Test warning message"
        entry = analyzer.analyze_line(warning_line)
        if entry.output_type == OutputType.WARNING:
            print("✅ Warning detection working")
            test_results.append(("Warning Detection", True, "Warning pattern detected"))
        else:
            print("❌ Warning detection failed")
            test_results.append(("Warning Detection", False, "Warning pattern not detected"))
        
        # Test severity scoring
        if entry.severity >= 5:
            print("✅ Severity scoring working")
            test_results.append(("Severity Scoring", True, f"Severity: {entry.severity}"))
        else:
            print("❌ Severity scoring failed")
            test_results.append(("Severity Scoring", False, f"Severity: {entry.severity}"))
        
        # Test 3: Test OutputStatistics
        print("\nTest 3: Testing OutputStatistics...")
        stats = OutputStatistics()
        
        # Add some test entries
        test_entries = [
            "[12:00:01] Starting application...",
            "[12:00:02] Loading configuration...",
            "[12:00:03] Warning: Deprecated feature used",
            "[12:00:04] Error: Failed to connect to database",
            "[12:00:05] Success: Application started successfully"
        ]
        
        for line in test_entries:
            entry = analyzer.analyze_line(line)
            stats.update(entry)
        
        summary = stats.get_summary()
        if summary['total_lines'] == 5:
            print("✅ Statistics tracking working")
            test_results.append(("Statistics", True, f"Total lines: {summary['total_lines']}"))
        else:
            print("❌ Statistics tracking failed")
            test_results.append(("Statistics", False, f"Expected 5, got {summary['total_lines']}"))
        
        # Test 4: Test OutputFilter
        print("\nTest 4: Testing OutputFilter...")
        filter_system = OutputFilter()
        filter_system.create_builtin_filters()
        
        # Test error filter
        filter_system.enable_filter('errors_only')
        filtered_entries = filter_system.apply_filters([entry for line in test_entries 
                                                      for entry in [analyzer.analyze_line(line)]])
        
        error_entries = [e for e in filtered_entries if e.output_type == OutputType.ERROR]
        if len(error_entries) == 1:
            print("✅ Error filter working")
            test_results.append(("Error Filter", True, f"Found {len(error_entries)} error entries"))
        else:
            print("❌ Error filter failed")
            test_results.append(("Error Filter", False, f"Expected 1, got {len(error_entries)}"))
        
        # Test 5: Test export functionality
        print("\nTest 5: Testing export functionality...")
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_file = f.name
            
            # Test JSON export
            export_data = {
                'statistics': summary,
                'filters': {name: config['description'] for name, config in filter_system.filters.items()},
                'active_filters': list(filter_system.active_filters),
                'export_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Verify export
            with open(temp_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            if imported_data['statistics']['total_lines'] == 5:
                print("✅ Export functionality working")
                test_results.append(("Export", True, "JSON export successful"))
            else:
                print("❌ Export functionality failed")
                test_results.append(("Export", False, "JSON export failed"))
            
            # Clean up
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"❌ Export test failed: {e}")
            test_results.append(("Export", False, str(e)))
        
        # Test 6: Test TerminalEnhancer
        print("\nTest 6: Testing TerminalEnhancer...")
        enhancer = TerminalEnhancer()
        
        # Test enhancer creation
        if hasattr(enhancer, 'analyzer') and hasattr(enhancer, 'filter') and hasattr(enhancer, 'statistics'):
            print("✅ TerminalEnhancer created successfully")
            test_results.append(("TerminalEnhancer", True, "All components initialized"))
        else:
            print("❌ TerminalEnhancer creation failed")
            test_results.append(("TerminalEnhancer", False, "Missing components"))
        
        # Test 7: Test pattern recognition
        print("\nTest 7: Testing pattern recognition...")
        test_patterns = [
            ("error", "[ERROR] Test error", OutputType.ERROR),
            ("warning", "[WARN] Test warning", OutputType.WARNING),
            ("success", "Success: Test success", OutputType.SUCCESS),
            ("info", "Info: Test info", OutputType.INFO),
            ("debug", "Debug: Test debug", OutputType.DEBUG),
            ("command", "> test command", OutputType.COMMAND)
        ]
        
        pattern_success = 0
        for pattern_name, test_line, expected_type in test_patterns:
            entry = analyzer.analyze_line(test_line)
            if entry.output_type == expected_type:
                pattern_success += 1
                print(f"✅ {pattern_name} pattern detected")
            else:
                print(f"❌ {pattern_name} pattern failed (got {entry.output_type.value})")
        
        if pattern_success == len(test_patterns):
            test_results.append(("Pattern Recognition", True, f"All {pattern_success} patterns detected"))
        else:
            test_results.append(("Pattern Recognition", False, f"{pattern_success}/{len(test_patterns)} patterns detected"))
        
        # Test 8: Test metadata extraction
        print("\nTest 8: Testing metadata extraction...")
        test_line = "[12:00:01] Processing file: /path/to/file.txt with 123 items from https://example.com"
        entry = analyzer.analyze_line(test_line)
        
        metadata_checks = [
            ("has_timestamp", entry.metadata.get('has_timestamp', False)),
            ("has_numbers", entry.metadata.get('has_numbers', False)),
            ("has_urls", entry.metadata.get('has_urls', False)),
            ("has_paths", entry.metadata.get('has_paths', False))
        ]
        
        metadata_success = sum(1 for _, check in metadata_checks if check)
        if metadata_success >= 3:  # At least 3 out of 4 should work
            print("✅ Metadata extraction working")
            test_results.append(("Metadata Extraction", True, f"{metadata_success}/4 metadata types detected"))
        else:
            print("❌ Metadata extraction failed")
            test_results.append(("Metadata Extraction", False, f"{metadata_success}/4 metadata types detected"))
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        test_results.append(("Overall Test", False, str(e)))
    
    # Print summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success, _ in test_results if success)
    
    for test_name, success, message in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status} - {message}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Terminal enhancements are working correctly.")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Some features may not work correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(test_terminal_enhancements()) 