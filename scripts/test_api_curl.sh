#!/bin/bash

# Z-Waifu Launcher API Authentication Test Script
# This script uses curl to test the API authentication system

API_BASE_URL="http://localhost:8081"
ADMIN_KEY=""
API_KEY=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    local details=$3
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC} $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ FAIL${NC} $message"
    elif [ "$status" = "INFO" ]; then
        echo -e "${BLUE}ℹ️  INFO${NC} $message"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  WARN${NC} $message"
    fi
    
    if [ ! -z "$details" ]; then
        echo "   Details: $details"
    fi
    echo
}

# Function to test server availability
test_server_availability() {
    print_status "INFO" "Testing server availability..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/status" 2>/dev/null)
    
    if [ "$response" = "401" ]; then
        print_status "PASS" "Server is running and requires authentication" "Status: $response"
    elif [ "$response" = "000" ]; then
        print_status "FAIL" "Server is not running" "Make sure the API server is started on port 8081"
    else
        print_status "WARN" "Server responded with unexpected status" "Status: $response"
    fi
}

# Function to test missing authentication
test_missing_auth() {
    print_status "INFO" "Testing missing authentication headers..."
    
    endpoints=("/api/status" "/api/processes" "/api/start/Oobabooga" "/api/stop/Z-Waifu")
    
    for endpoint in "${endpoints[@]}"; do
        method="GET"
        if [[ "$endpoint" == *"start"* ]] || [[ "$endpoint" == *"stop"* ]]; then
            method="POST"
        fi
        
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$API_BASE_URL$endpoint" 2>/dev/null)
        
        if [ "$response" = "401" ]; then
            print_status "PASS" "Missing auth properly rejected" "Endpoint: $endpoint, Status: $response"
        else
            print_status "FAIL" "Missing auth not properly rejected" "Endpoint: $endpoint, Expected: 401, Got: $response"
        fi
    done
}

# Function to test invalid authentication headers
test_invalid_auth() {
    print_status "INFO" "Testing invalid authentication headers..."
    
    invalid_headers=(
        "Invalid"
        "Bearer"
        "Bearer invalid_key"
        "Basic dXNlcjpwYXNz"
    )
    
    for i in "${!invalid_headers[@]}"; do
        header="${invalid_headers[$i]}"
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: $header" \
            "$API_BASE_URL/api/status" 2>/dev/null)
        
        if [ "$response" = "401" ]; then
            print_status "PASS" "Invalid auth properly rejected" "Header: $header, Status: $response"
        else
            print_status "FAIL" "Invalid auth not properly rejected" "Header: $header, Expected: 401, Got: $response"
        fi
    done
}

# Function to generate API key using admin key
generate_api_key() {
    if [ -z "$ADMIN_KEY" ]; then
        print_status "WARN" "Admin key not provided, skipping API key generation"
        return
    fi
    
    print_status "INFO" "Generating API key using admin key..."
    
    response=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $ADMIN_KEY" \
        -H "Content-Type: application/json" \
        "$API_BASE_URL/api/keys/generate" 2>/dev/null)
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        API_KEY=$(echo "$body" | grep -o '"api_key":"[^"]*"' | cut -d'"' -f4)
        expires_in=$(echo "$body" | grep -o '"expires_in":[0-9]*' | cut -d':' -f2)
        
        print_status "PASS" "API key generated successfully" "Key: ${API_KEY:0:16}..., Expires in: ${expires_in}s"
    else
        print_status "FAIL" "Failed to generate API key" "Status: $http_code, Response: $body"
    fi
}

# Function to test valid API key
test_valid_api_key() {
    if [ -z "$API_KEY" ]; then
        print_status "WARN" "No API key available, skipping valid key tests"
        return
    fi
    
    print_status "INFO" "Testing valid API key..."
    
    endpoints=("/api/status" "/api/processes")
    
    for endpoint in "${endpoints[@]}"; do
        response=$(curl -s -w "%{http_code}" \
            -H "Authorization: Bearer $API_KEY" \
            "$API_BASE_URL$endpoint" 2>/dev/null)
        
        http_code="${response: -3}"
        body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            print_status "PASS" "Valid API key accepted" "Endpoint: $endpoint, Status: $http_code"
            
            # Check if response is valid JSON
            if echo "$body" | jq . >/dev/null 2>&1; then
                print_status "PASS" "Response is valid JSON" "Endpoint: $endpoint"
            else
                print_status "FAIL" "Response is not valid JSON" "Endpoint: $endpoint"
            fi
        else
            print_status "FAIL" "Valid API key rejected" "Endpoint: $endpoint, Status: $http_code"
        fi
    done
}

# Function to test process operations
test_process_operations() {
    if [ -z "$API_KEY" ]; then
        print_status "WARN" "No API key available, skipping process operation tests"
        return
    fi
    
    print_status "INFO" "Testing process operations..."
    
    # Test process start
    response=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        "$API_BASE_URL/api/start/Oobabooga" 2>/dev/null)
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [[ "$http_code" =~ ^(200|400|500)$ ]]; then
        print_status "PASS" "Process start operation completed" "Status: $http_code"
    else
        print_status "FAIL" "Process start operation failed" "Status: $http_code, Response: $body"
    fi
    
    # Test process stop
    response=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        "$API_BASE_URL/api/stop/Z-Waifu" 2>/dev/null)
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [[ "$http_code" =~ ^(200|400|500)$ ]]; then
        print_status "PASS" "Process stop operation completed" "Status: $http_code"
    else
        print_status "FAIL" "Process stop operation failed" "Status: $http_code, Response: $body"
    fi
}

# Function to test invalid process types
test_invalid_process_types() {
    if [ -z "$API_KEY" ]; then
        print_status "WARN" "No API key available, skipping invalid process type tests"
        return
    fi
    
    print_status "INFO" "Testing invalid process types..."
    
    invalid_processes=("InvalidProcess" "malicious_script" "Oobabooga' OR 1=1--" "Z-Waifu; DROP TABLE users;" "")
    
    for process_type in "${invalid_processes[@]}"; do
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -X POST \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json" \
            "$API_BASE_URL/api/start/$process_type" 2>/dev/null)
        
        if [ "$response" = "400" ]; then
            print_status "PASS" "Invalid process type properly rejected" "Type: '$process_type', Status: $response"
        else
            print_status "FAIL" "Invalid process type not properly rejected" "Type: '$process_type', Expected: 400, Got: $response"
        fi
    done
}

# Function to test rate limiting
test_rate_limiting() {
    if [ -z "$API_KEY" ]; then
        print_status "WARN" "No API key available, skipping rate limiting tests"
        return
    fi
    
    print_status "INFO" "Testing rate limiting..."
    
    # Make multiple rapid requests
    rate_limited=false
    for i in {1..15}; do
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: Bearer $API_KEY" \
            "$API_BASE_URL/api/status" 2>/dev/null)
        
        if [ "$response" = "429" ]; then
            rate_limited=true
            break
        fi
        
        sleep 0.1
    done
    
    if [ "$rate_limited" = true ]; then
        print_status "PASS" "Rate limiting is working" "Hit rate limit after $i requests"
    else
        print_status "WARN" "Rate limiting not triggered" "Made 15 requests without hitting limit"
    fi
}

# Main function
main() {
    echo "🔐 Z-Waifu Launcher API Authentication Test (curl)"
    echo "=================================================="
    echo
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        print_status "FAIL" "curl is not installed" "Please install curl to run these tests"
        exit 1
    fi
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        print_status "WARN" "jq is not installed" "JSON validation will be skipped"
    fi
    
    # Get admin key if not provided
    if [ -z "$ADMIN_KEY" ]; then
        echo -n "Enter admin key (or press Enter to skip admin key tests): "
        read -r ADMIN_KEY
    fi
    
    # Run tests
    test_server_availability
    test_missing_auth
    test_invalid_auth
    generate_api_key
    test_valid_api_key
    test_process_operations
    test_invalid_process_types
    test_rate_limiting
    
    echo "=================================================="
    print_status "INFO" "Test completed" "Check the output above for results"
}

# Run main function
main 