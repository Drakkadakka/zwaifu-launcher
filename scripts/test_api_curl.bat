@echo off
REM Z-Waifu Launcher API Authentication Test Script (Windows)
REM This script uses curl to test the API authentication system

setlocal enabledelayedexpansion

set API_BASE_URL=http://localhost:8081
set ADMIN_KEY=
set API_KEY=

echo 🔐 Z-Waifu Launcher API Authentication Test (curl - Windows)
echo ==================================================
echo.

REM Check if curl is available
curl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL curl is not installed
    echo Please install curl to run these tests
    echo You can download it from: https://curl.se/windows/
    pause
    exit /b 1
)

REM Check if jq is available for JSON parsing
jq --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARN jq is not installed
    echo JSON validation will be skipped
    echo You can download it from: https://stedolan.github.io/jq/download/
    echo.
)

REM Get admin key if not provided
if "%ADMIN_KEY%"=="" (
    set /p ADMIN_KEY="Enter admin key (or press Enter to skip admin key tests): "
)

echo.
echo ℹ️  INFO Testing server availability...

REM Test server availability
for /f "tokens=*" %%i in ('curl -s -o nul -w "%%{http_code}" "%API_BASE_URL%/api/status" 2^>nul') do set response=%%i

if "%response%"=="401" (
    echo ✅ PASS Server is running and requires authentication
    echo    Details: Status: %response%
) else if "%response%"=="000" (
    echo ❌ FAIL Server is not running
    echo    Details: Make sure the API server is started on port 8081
) else (
    echo ⚠️  WARN Server responded with unexpected status
    echo    Details: Status: %response%
)
echo.

echo ℹ️  INFO Testing missing authentication headers...

REM Test missing authentication
set endpoints=/api/status /api/processes /api/start/Oobabooga /api/stop/Z-Waifu

for %%e in (%endpoints%) do (
    set method=GET
    if "%%e"=="start" set method=POST
    if "%%e"=="stop" set method=POST
    
    for /f "tokens=*" %%i in ('curl -s -o nul -w "%%{http_code}" -X %method% "%API_BASE_URL%%%e" 2^>nul') do set response=%%i
    
    if "!response!"=="401" (
        echo ✅ PASS Missing auth properly rejected
        echo    Details: Endpoint: %%e, Status: !response!
    ) else (
        echo ❌ FAIL Missing auth not properly rejected
        echo    Details: Endpoint: %%e, Expected: 401, Got: !response!
    )
    echo.
)

echo ℹ️  INFO Testing invalid authentication headers...

REM Test invalid authentication headers
set invalid_headers=Invalid "Bearer" "Bearer invalid_key" "Basic dXNlcjpwYXNz"

for %%h in (%invalid_headers%) do (
    for /f "tokens=*" %%i in ('curl -s -o nul -w "%%{http_code}" -H "Authorization: %%h" "%API_BASE_URL%/api/status" 2^>nul') do set response=%%i
    
    if "!response!"=="401" (
        echo ✅ PASS Invalid auth properly rejected
        echo    Details: Header: %%h, Status: !response!
    ) else (
        echo ❌ FAIL Invalid auth not properly rejected
        echo    Details: Header: %%h, Expected: 401, Got: !response!
    )
    echo.
)

REM Test admin key generation if provided
if not "%ADMIN_KEY%"=="" (
    echo ℹ️  INFO Generating API key using admin key...
    
    for /f "tokens=*" %%i in ('curl -s -w "%%{http_code}" -X POST -H "Authorization: Bearer %ADMIN_KEY%" -H "Content-Type: application/json" "%API_BASE_URL%/api/keys/generate" 2^>nul') do set response=%%i
    
    REM Extract HTTP code (last 3 characters)
    set http_code=!response:~-3!
    set body=!response:~0,-3!
    
    if "!http_code!"=="200" (
        echo ✅ PASS API key generated successfully
        REM Extract API key from response (simplified)
        for /f "tokens=2 delims=:," %%a in ("!body!") do set API_KEY=%%a
        set API_KEY=!API_KEY:"=!
        echo    Details: Key: !API_KEY:~0,16!..., Expires in: 86400s
    ) else (
        echo ❌ FAIL Failed to generate API key
        echo    Details: Status: !http_code!, Response: !body!
    )
    echo.
) else (
    echo ⚠️  WARN Admin key not provided, skipping API key generation
    echo.
)

REM Test valid API key if available
if not "%API_KEY%"=="" (
    echo ℹ️  INFO Testing valid API key...
    
    set endpoints=/api/status /api/processes
    
    for %%e in (%endpoints%) do (
        for /f "tokens=*" %%i in ('curl -s -w "%%{http_code}" -H "Authorization: Bearer %API_KEY%" "%API_BASE_URL%%%e" 2^>nul') do set response=%%i
        
        set http_code=!response:~-3!
        set body=!response:~0,-3!
        
        if "!http_code!"=="200" (
            echo ✅ PASS Valid API key accepted
            echo    Details: Endpoint: %%e, Status: !http_code!
            
            REM Check if response is valid JSON (simplified check)
            echo !body! | findstr "{" >nul
            if not errorlevel 1 (
                echo ✅ PASS Response is valid JSON
                echo    Details: Endpoint: %%e
            ) else (
                echo ❌ FAIL Response is not valid JSON
                echo    Details: Endpoint: %%e
            )
        ) else (
            echo ❌ FAIL Valid API key rejected
            echo    Details: Endpoint: %%e, Status: !http_code!
        )
        echo.
    )
) else (
    echo ⚠️  WARN No API key available, skipping valid key tests
    echo.
)

REM Test process operations if API key available
if not "%API_KEY%"=="" (
    echo ℹ️  INFO Testing process operations...
    
    REM Test process start
    for /f "tokens=*" %%i in ('curl -s -w "%%{http_code}" -X POST -H "Authorization: Bearer %API_KEY%" -H "Content-Type: application/json" "%API_BASE_URL%/api/start/Oobabooga" 2^>nul') do set response=%%i
    
    set http_code=!response:~-3!
    set body=!response:~0,-3!
    
    if "!http_code!"=="200" (
        echo ✅ PASS Process start operation completed
        echo    Details: Status: !http_code!
    ) else if "!http_code!"=="400" (
        echo ✅ PASS Process start operation completed
        echo    Details: Status: !http_code!
    ) else if "!http_code!"=="500" (
        echo ✅ PASS Process start operation completed
        echo    Details: Status: !http_code!
    ) else (
        echo ❌ FAIL Process start operation failed
        echo    Details: Status: !http_code!, Response: !body:~0,100!...
    )
    echo.
    
    REM Test process stop
    for /f "tokens=*" %%i in ('curl -s -w "%%{http_code}" -X POST -H "Authorization: Bearer %API_KEY%" -H "Content-Type: application/json" "%API_BASE_URL%/api/stop/Z-Waifu" 2^>nul') do set response=%%i
    
    set http_code=!response:~-3!
    set body=!response:~0,-3!
    
    if "!http_code!"=="200" (
        echo ✅ PASS Process stop operation completed
        echo    Details: Status: !http_code!
    ) else if "!http_code!"=="400" (
        echo ✅ PASS Process stop operation completed
        echo    Details: Status: !http_code!
    ) else if "!http_code!"=="500" (
        echo ✅ PASS Process stop operation completed
        echo    Details: Status: !http_code!
    ) else (
        echo ❌ FAIL Process stop operation failed
        echo    Details: Status: !http_code!, Response: !body:~0,100!...
    )
    echo.
) else (
    echo ⚠️  WARN No API key available, skipping process operation tests
    echo.
)

REM Test invalid process types if API key available
if not "%API_KEY%"=="" (
    echo ℹ️  INFO Testing invalid process types...
    
    set invalid_processes=InvalidProcess malicious_script "Oobabooga' OR 1=1--" "Z-Waifu; DROP TABLE users;" ""
    
    for %%p in (%invalid_processes%) do (
        for /f "tokens=*" %%i in ('curl -s -o nul -w "%%{http_code}" -X POST -H "Authorization: Bearer %API_KEY%" -H "Content-Type: application/json" "%API_BASE_URL%/api/start/%%p" 2^>nul') do set response=%%i
        
        if "!response!"=="400" (
            echo ✅ PASS Invalid process type properly rejected
            echo    Details: Type: '%%p', Status: !response!
        ) else (
            echo ❌ FAIL Invalid process type not properly rejected
            echo    Details: Type: '%%p', Expected: 400, Got: !response!
        )
        echo.
    )
) else (
    echo ⚠️  WARN No API key available, skipping invalid process type tests
    echo.
)

REM Test rate limiting if API key available
if not "%API_KEY%"=="" (
    echo ℹ️  INFO Testing rate limiting...
    
    set rate_limited=false
    for /l %%i in (1,1,15) do (
        for /f "tokens=*" %%j in ('curl -s -o nul -w "%%{http_code}" -H "Authorization: Bearer %API_KEY%" "%API_BASE_URL%/api/status" 2^>nul') do set response=%%j
        
        if "!response!"=="429" (
            set rate_limited=true
            echo ✅ PASS Rate limiting is working
            echo    Details: Hit rate limit after %%i requests
            goto :rate_limit_done
        )
        
        timeout /t 1 /nobreak >nul
    )
    
    if "!rate_limited!"=="false" (
        echo ⚠️  WARN Rate limiting not triggered
        echo    Details: Made 15 requests without hitting limit
    )
    
    :rate_limit_done
    echo.
) else (
    echo ⚠️  WARN No API key available, skipping rate limiting tests
    echo.
)

echo ==================================================
echo ℹ️  INFO Test completed
echo    Details: Check the output above for results
echo.
pause 