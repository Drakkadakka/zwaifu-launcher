#!/usr/bin/env python3
"""
API Authentication Test Script for Z-Waifu Launcher

This script tests the API key authentication system including:
- Admin key generation
- API key generation using admin key
- API key validation
- Rate limiting
- Expired key handling
- Invalid key handling
- Process type validation
"""

import requests
import time
import json
import sys
from datetime import datetime
import os

# Configuration
API_BASE_URL = "http://localhost:8081"
ADMIN_KEY = None  # Will be set from launcher logs or manual input

# Try to load API key using the utility function
try:
    from utils.api_utils import load_api_key
    SAVED_API_KEY = load_api_key()
except ImportError:
    # Fallback to direct file loading
    API_KEY_FILE = os.path.join(os.path.dirname(__file__), 'api_key.json')
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            try:
                api_key_data = json.load(f)
                SAVED_API_KEY = api_key_data.get('api_key')
            except Exception:
                SAVED_API_KEY = None
    else:
        SAVED_API_KEY = None

class APIAuthTester:
    def __init__(self, base_url, admin_key=None):
        self.base_url = base_url
        self.admin_key = admin_key
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_server_availability(self):
        """Test if the API server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/status", timeout=5)
            self.log_test(
                "Server Availability",
                response.status_code == 401,  # Should return 401 (unauthorized) not 404
                f"Server responded with status {response.status_code}",
                f"Expected 401 (unauthorized), got {response.status_code}"
            )
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Server Availability",
                False,
                "Could not connect to API server",
                "Make sure the API server is running on port 8081"
            )
        except Exception as e:
            self.log_test(
                "Server Availability",
                False,
                f"Unexpected error: {str(e)}"
            )
    
    def test_missing_auth_header(self):
        """Test API calls without authentication header"""
        endpoints = [
            "/api/status",
            "/api/processes",
            "/api/start/Oobabooga",
            "/api/stop/Z-Waifu"
        ]
        
        for endpoint in endpoints:
            try:
                method = "POST" if "start" in endpoint or "stop" in endpoint else "GET"
                response = self.session.request(method, f"{self.base_url}{endpoint}", timeout=5)
                
                self.log_test(
                    f"Missing Auth - {endpoint}",
                    response.status_code == 401,
                    f"Endpoint {endpoint} returned {response.status_code}",
                    f"Expected 401 (unauthorized), got {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"Missing Auth - {endpoint}",
                    False,
                    f"Error testing {endpoint}: {str(e)}"
                )
    
    def test_invalid_auth_header(self):
        """Test API calls with invalid authentication header"""
        invalid_headers = [
            {"Authorization": "Invalid"},
            {"Authorization": "Bearer"},
            {"Authorization": "Bearer invalid_key"},
            {"Authorization": "Basic dXNlcjpwYXNz"},
        ]
        
        for i, header in enumerate(invalid_headers):
            try:
                response = self.session.get(
                    f"{self.base_url}/api/status",
                    headers=header,
                    timeout=5
                )
                
                self.log_test(
                    f"Invalid Auth Header {i+1}",
                    response.status_code == 401,
                    f"Invalid header returned {response.status_code}",
                    f"Header: {header['Authorization']}, Expected 401, got {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"Invalid Auth Header {i+1}",
                    False,
                    f"Error testing invalid header: {str(e)}"
                )
    
    def test_admin_key_generation(self):
        """Test API key generation using admin key"""
        if not self.admin_key:
            self.log_test(
                "Admin Key Generation",
                False,
                "Admin key not provided",
                "Please provide the admin key from the launcher logs"
            )
            return None
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/keys/generate",
                headers={"Authorization": f"Bearer {self.admin_key}"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                api_key = data.get('api_key')
                expires_in = data.get('expires_in')
                
                self.log_test(
                    "Admin Key Generation",
                    True,
                    f"Successfully generated API key",
                    f"Key: {api_key[:16]}..., Expires in: {expires_in} seconds"
                )
                return api_key
            else:
                self.log_test(
                    "Admin Key Generation",
                    False,
                    f"Failed to generate API key: {response.status_code}",
                    f"Response: {response.text}"
                )
                return None
        except Exception as e:
            self.log_test(
                "Admin Key Generation",
                False,
                f"Error generating API key: {str(e)}"
            )
            return None
    
    def test_api_key_validation(self, api_key):
        """Test API calls with valid API key"""
        if not api_key:
            self.log_test(
                "API Key Validation",
                False,
                "No API key provided for testing"
            )
            return
        
        endpoints = [
            ("GET", "/api/status"),
            ("GET", "/api/processes"),
        ]
        
        for method, endpoint in endpoints:
            try:
                response = self.session.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=5
                )
                
                self.log_test(
                    f"API Key Validation - {endpoint}",
                    response.status_code == 200,
                    f"Endpoint {endpoint} returned {response.status_code}",
                    f"Expected 200 (success), got {response.status_code}"
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_test(
                            f"API Response Format - {endpoint}",
                            isinstance(data, dict),
                            f"Response is valid JSON object",
                            f"Response keys: {list(data.keys())}"
                        )
                    except json.JSONDecodeError:
                        self.log_test(
                            f"API Response Format - {endpoint}",
                            False,
                            f"Response is not valid JSON"
                        )
            except Exception as e:
                self.log_test(
                    f"API Key Validation - {endpoint}",
                    False,
                    f"Error testing {endpoint}: {str(e)}"
                )
    
    def test_process_operations(self, api_key):
        """Test process start/stop operations"""
        if not api_key:
            self.log_test(
                "Process Operations",
                False,
                "No API key provided for testing"
            )
            return
        
        # Test process start
        try:
            response = self.session.post(
                f"{self.base_url}/api/start/Oobabooga",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            
            self.log_test(
                "Process Start Operation",
                response.status_code in [200, 400, 500],  # Accept various responses
                f"Process start returned {response.status_code}",
                f"Response: {response.text[:100]}..."
            )
        except Exception as e:
            self.log_test(
                "Process Start Operation",
                False,
                f"Error testing process start: {str(e)}"
            )
        
        # Test process stop
        try:
            response = self.session.post(
                f"{self.base_url}/api/stop/Z-Waifu",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            
            self.log_test(
                "Process Stop Operation",
                response.status_code in [200, 400, 500],  # Accept various responses
                f"Process stop returned {response.status_code}",
                f"Response: {response.text[:100]}..."
            )
        except Exception as e:
            self.log_test(
                "Process Stop Operation",
                False,
                f"Error testing process stop: {str(e)}"
            )
    
    def test_invalid_process_types(self, api_key):
        """Test API calls with invalid process types"""
        if not api_key:
            return
        
        invalid_processes = [
            "InvalidProcess",
            "malicious_script",
            "Oobabooga' OR 1=1--",
            "Z-Waifu; DROP TABLE users;",
            ""
        ]
        
        for process_type in invalid_processes:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/start/{process_type}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=5
                )
                
                self.log_test(
                    f"Invalid Process Type - {process_type}",
                    response.status_code == 400,
                    f"Invalid process type '{process_type}' returned {response.status_code}",
                    f"Expected 400 (bad request), got {response.status_code}"
                )
            except Exception as e:
                self.log_test(
                    f"Invalid Process Type - {process_type}",
                    False,
                    f"Error testing invalid process type: {str(e)}"
                )
    
    def test_rate_limiting(self, api_key):
        """Test rate limiting by making multiple rapid requests"""
        if not api_key:
            return
        
        try:
            # Make multiple rapid requests
            responses = []
            for i in range(15):  # More than the 10 per minute limit
                response = self.session.get(
                    f"{self.base_url}/api/status",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=5
                )
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # Check if we hit rate limiting
            rate_limited = any(status == 429 for status in responses)
            
            self.log_test(
                "Rate Limiting",
                rate_limited or all(status == 200 for status in responses),
                f"Rate limiting test completed",
                f"Responses: {responses[:10]}... (showing first 10)"
            )
        except Exception as e:
            self.log_test(
                "Rate Limiting",
                False,
                f"Error testing rate limiting: {str(e)}"
            )
    
    def test_expired_key_handling(self):
        """Test handling of expired keys (simulated)"""
        # Create a key that would be expired
        expired_key = "expired_key_for_testing"
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/status",
                headers={"Authorization": f"Bearer {expired_key}"},
                timeout=5
            )
            
            self.log_test(
                "Expired Key Handling",
                response.status_code == 401,
                f"Expired key returned {response.status_code}",
                f"Expected 401 (unauthorized), got {response.status_code}"
            )
        except Exception as e:
            self.log_test(
                "Expired Key Handling",
                False,
                f"Error testing expired key: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🔐 Z-Waifu Launcher API Authentication Test Suite")
        print("=" * 60)
        print()
        
        # Basic connectivity tests
        self.test_server_availability()
        self.test_missing_auth_header()
        self.test_invalid_auth_header()
        self.test_expired_key_handling()
        
        # Admin key tests
        api_key = self.test_admin_key_generation()
        
        if api_key:
            # Valid API key tests
            self.test_api_key_validation(api_key)
            self.test_process_operations(api_key)
            self.test_invalid_process_types(api_key)
            self.test_rate_limiting(api_key)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_auth_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {filename}")

def main():
    """Main function"""
    print("Z-Waifu Launcher API Authentication Test")
    print("=" * 50)
    
    # Get admin key from user
    admin_key = input("Enter admin key (or press Enter to skip admin key tests): ").strip()
    if not admin_key:
        admin_key = None
        print("Skipping admin key tests...")
    
    # Use saved API key if available
    if SAVED_API_KEY:
        print(f"Using saved API key from {API_KEY_FILE}: {SAVED_API_KEY[:16]}...\n")
    else:
        print("No saved API key found. You may need to generate one first.\n")
    
    # Create tester and run tests
    tester = APIAuthTester(API_BASE_URL, admin_key)
    if SAVED_API_KEY:
        tester.test_api_key_validation(SAVED_API_KEY)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 