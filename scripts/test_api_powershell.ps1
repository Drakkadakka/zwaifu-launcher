# Z-Waifu Launcher API Authentication Test Script (PowerShell)
# This script uses PowerShell to test the API authentication system

param(
    [string]$AdminKey = "",
    [string]$ApiBaseUrl = "http://localhost:8081"
)

# Function to print colored output
function Write-TestResult {
    param(
        [string]$Status,
        [string]$Message,
        [string]$Details = ""
    )
    
    switch ($Status) {
        "PASS" { 
            Write-Host "✅ PASS $Message" -ForegroundColor Green
        }
        "FAIL" { 
            Write-Host "❌ FAIL $Message" -ForegroundColor Red
        }
        "INFO" { 
            Write-Host "ℹ️  INFO $Message" -ForegroundColor Blue
        }
        "WARN" { 
            Write-Host "⚠️  WARN $Message" -ForegroundColor Yellow
        }
    }
    
    if ($Details) {
        Write-Host "   Details: $Details" -ForegroundColor Gray
    }
    Write-Host ""
}

# Function to test server availability
function Test-ServerAvailability {
    Write-TestResult "INFO" "Testing server availability..."
    
    try {
        $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/status" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-TestResult "WARN" "Server responded with unexpected status" "Status: $($response.StatusCode)"
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-TestResult "PASS" "Server is running and requires authentication" "Status: 401"
        }
        elseif ($_.Exception.Message -like "*Unable to connect*") {
            Write-TestResult "FAIL" "Server is not running" "Make sure the API server is started on port 8081"
        }
        else {
            Write-TestResult "FAIL" "Unexpected error" $_.Exception.Message
        }
    }
}

# Function to test missing authentication
function Test-MissingAuthentication {
    Write-TestResult "INFO" "Testing missing authentication headers..."
    
    $endpoints = @("/api/status", "/api/processes", "/api/start/Oobabooga", "/api/stop/Z-Waifu")
    
    foreach ($endpoint in $endpoints) {
        $method = if ($endpoint -like "*start*" -or $endpoint -like "*stop*") { "POST" } else { "GET" }
        
        try {
            $response = Invoke-WebRequest -Uri "$ApiBaseUrl$endpoint" -Method $method -TimeoutSec 5 -ErrorAction Stop
            Write-TestResult "FAIL" "Missing auth not properly rejected" "Endpoint: $endpoint, Expected: 401, Got: $($response.StatusCode)"
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 401) {
                Write-TestResult "PASS" "Missing auth properly rejected" "Endpoint: $endpoint, Status: 401"
            }
            else {
                Write-TestResult "FAIL" "Error testing endpoint" "Endpoint: $endpoint, Error: $($_.Exception.Message)"
            }
        }
    }
}

# Function to test invalid authentication headers
function Test-InvalidAuthentication {
    Write-TestResult "INFO" "Testing invalid authentication headers..."
    
    $invalidHeaders = @(
        @{ "Authorization" = "Invalid" },
        @{ "Authorization" = "Bearer" },
        @{ "Authorization" = "Bearer invalid_key" },
        @{ "Authorization" = "Basic dXNlcjpwYXNz" }
    )
    
    foreach ($header in $invalidHeaders) {
        try {
            $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/status" -Headers $header -TimeoutSec 5 -ErrorAction Stop
            Write-TestResult "FAIL" "Invalid auth not properly rejected" "Header: $($header.Authorization), Expected: 401, Got: $($response.StatusCode)"
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 401) {
                Write-TestResult "PASS" "Invalid auth properly rejected" "Header: $($header.Authorization), Status: 401"
            }
            else {
                Write-TestResult "FAIL" "Error testing invalid header" "Header: $($header.Authorization), Error: $($_.Exception.Message)"
            }
        }
    }
}

# Function to generate API key using admin key
function Test-AdminKeyGeneration {
    if (-not $AdminKey) {
        Write-TestResult "WARN" "Admin key not provided, skipping API key generation"
        return $null
    }
    
    Write-TestResult "INFO" "Generating API key using admin key..."
    
    try {
        $headers = @{
            "Authorization" = "Bearer $AdminKey"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/keys/generate" -Method POST -Headers $headers -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            $apiKey = $data.api_key
            $expiresIn = $data.expires_in
            
            Write-TestResult "PASS" "API key generated successfully" "Key: $($apiKey.Substring(0, 16))..., Expires in: ${expiresIn}s"
            return $apiKey
        }
        else {
            Write-TestResult "FAIL" "Failed to generate API key" "Status: $($response.StatusCode), Response: $($response.Content)"
            return $null
        }
    }
    catch {
        Write-TestResult "FAIL" "Error generating API key" $_.Exception.Message
        return $null
    }
}

# Function to test valid API key
function Test-ValidApiKey {
    param([string]$ApiKey)
    
    if (-not $ApiKey) {
        Write-TestResult "WARN" "No API key available, skipping valid key tests"
        return
    }
    
    Write-TestResult "INFO" "Testing valid API key..."
    
    $endpoints = @("/api/status", "/api/processes")
    
    foreach ($endpoint in $endpoints) {
        try {
            $headers = @{ "Authorization" = "Bearer $ApiKey" }
            $response = Invoke-WebRequest -Uri "$ApiBaseUrl$endpoint" -Headers $headers -TimeoutSec 5 -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                Write-TestResult "PASS" "Valid API key accepted" "Endpoint: $endpoint, Status: $($response.StatusCode)"
                
                # Check if response is valid JSON
                try {
                    $jsonData = $response.Content | ConvertFrom-Json
                    Write-TestResult "PASS" "Response is valid JSON" "Endpoint: $endpoint"
                }
                catch {
                    Write-TestResult "FAIL" "Response is not valid JSON" "Endpoint: $endpoint"
                }
            }
            else {
                Write-TestResult "FAIL" "Valid API key rejected" "Endpoint: $endpoint, Status: $($response.StatusCode)"
            }
        }
        catch {
            Write-TestResult "FAIL" "Error testing endpoint" "Endpoint: $endpoint, Error: $($_.Exception.Message)"
        }
    }
}

# Function to test process operations
function Test-ProcessOperations {
    param([string]$ApiKey)
    
    if (-not $ApiKey) {
        Write-TestResult "WARN" "No API key available, skipping process operation tests"
        return
    }
    
    Write-TestResult "INFO" "Testing process operations..."
    
    $headers = @{
        "Authorization" = "Bearer $ApiKey"
        "Content-Type" = "application/json"
    }
    
    # Test process start
    try {
        $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/start/Oobabooga" -Method POST -Headers $headers -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -in @(200, 400, 500)) {
            Write-TestResult "PASS" "Process start operation completed" "Status: $($response.StatusCode)"
        }
        else {
            Write-TestResult "FAIL" "Process start operation failed" "Status: $($response.StatusCode), Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..."
        }
    }
    catch {
        Write-TestResult "FAIL" "Error testing process start" $_.Exception.Message
    }
    
    # Test process stop
    try {
        $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/stop/Z-Waifu" -Method POST -Headers $headers -TimeoutSec 5 -ErrorAction Stop
        
        if ($response.StatusCode -in @(200, 400, 500)) {
            Write-TestResult "PASS" "Process stop operation completed" "Status: $($response.StatusCode)"
        }
        else {
            Write-TestResult "FAIL" "Process stop operation failed" "Status: $($response.StatusCode), Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..."
        }
    }
    catch {
        Write-TestResult "FAIL" "Error testing process stop" $_.Exception.Message
    }
}

# Function to test invalid process types
function Test-InvalidProcessTypes {
    param([string]$ApiKey)
    
    if (-not $ApiKey) {
        Write-TestResult "WARN" "No API key available, skipping invalid process type tests"
        return
    }
    
    Write-TestResult "INFO" "Testing invalid process types..."
    
    $invalidProcesses = @("InvalidProcess", "malicious_script", "Oobabooga' OR 1=1--", "Z-Waifu; DROP TABLE users;", "")
    
    $headers = @{
        "Authorization" = "Bearer $ApiKey"
        "Content-Type" = "application/json"
    }
    
    foreach ($processType in $invalidProcesses) {
        try {
            $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/start/$processType" -Method POST -Headers $headers -TimeoutSec 5 -ErrorAction Stop
            Write-TestResult "FAIL" "Invalid process type not properly rejected" "Type: '$processType', Expected: 400, Got: $($response.StatusCode)"
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 400) {
                Write-TestResult "PASS" "Invalid process type properly rejected" "Type: '$processType', Status: 400"
            }
            else {
                Write-TestResult "FAIL" "Error testing invalid process type" "Type: '$processType', Error: $($_.Exception.Message)"
            }
        }
    }
}

# Function to test rate limiting
function Test-RateLimiting {
    param([string]$ApiKey)
    
    if (-not $ApiKey) {
        Write-TestResult "WARN" "No API key available, skipping rate limiting tests"
        return
    }
    
    Write-TestResult "INFO" "Testing rate limiting..."
    
    $headers = @{ "Authorization" = "Bearer $ApiKey" }
    $rateLimited = $false
    
    for ($i = 1; $i -le 15; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$ApiBaseUrl/api/status" -Headers $headers -TimeoutSec 5 -ErrorAction Stop
            
            if ($response.StatusCode -eq 429) {
                $rateLimited = $true
                Write-TestResult "PASS" "Rate limiting is working" "Hit rate limit after $i requests"
                break
            }
        }
        catch {
            if ($_.Exception.Response.StatusCode -eq 429) {
                $rateLimited = $true
                Write-TestResult "PASS" "Rate limiting is working" "Hit rate limit after $i requests"
                break
            }
        }
        
        Start-Sleep -Milliseconds 100
    }
    
    if (-not $rateLimited) {
        Write-TestResult "WARN" "Rate limiting not triggered" "Made 15 requests without hitting limit"
    }
}

# Main function
function Main {
    Write-Host "🔐 Z-Waifu Launcher API Authentication Test (PowerShell)" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Get admin key if not provided
    if (-not $AdminKey) {
        $AdminKey = Read-Host "Enter admin key (or press Enter to skip admin key tests)"
    }
    
    # Run tests
    Test-ServerAvailability
    Test-MissingAuthentication
    Test-InvalidAuthentication
    
    $apiKey = Test-AdminKeyGeneration
    
    if ($apiKey) {
        Test-ValidApiKey -ApiKey $apiKey
        Test-ProcessOperations -ApiKey $apiKey
        Test-InvalidProcessTypes -ApiKey $apiKey
        Test-RateLimiting -ApiKey $apiKey
    }
    
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-TestResult "INFO" "Test completed" "Check the output above for results"
}

# Run main function
Main 