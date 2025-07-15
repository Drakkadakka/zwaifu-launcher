@echo off
setlocal enabledelayedexpansion

REM ================================
REM Z-Waifu Launcher GUI - WinRAR Zipper
REM ================================

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
) else (
    echo WARNING: Not running with administrator privileges
    echo Some operations may fail. Consider running as administrator.
    echo.
)

REM Change to project root directory (parent of scripts)
cd /d "%~dp0.."

REM Set version and output
set "VERSION=1.0.0"
set "DIST_NAME=Z-Waifu-Launcher-GUI-v%VERSION%"
set "OUTPUT_FILE=%DIST_NAME%.rar"

REM Check for WinRAR
set "WINRAR_PATH="
if exist "C:\Program Files\WinRAR\WinRAR.exe" set "WINRAR_PATH=C:\Program Files\WinRAR\WinRAR.exe"
if exist "C:\Program Files (x86)\WinRAR\WinRAR.exe" set "WINRAR_PATH=C:\Program Files (x86)\WinRAR\WinRAR.exe"
if not defined WINRAR_PATH (
    where rar >nul 2>nul
    if %errorlevel% neq 0 (
        echo WinRAR not found! Trying alternative methods...
        echo.
    )
)

REM Create exclude list
set "EXCLUDE_FILE=zwaifu_exclude.txt"
(
echo venv
echo logs
echo __pycache__
echo .git
echo .idea
echo .vscode
echo *.pyc
echo *.log
echo *.tmp
echo *.rar
echo *.zip
echo *.7z
echo Z-Waifu-Launcher-GUI-*.zip
echo Z-Waifu-Launcher-GUI-*.rar
echo text-generation-webui-main
echo z-waif-1.14-R4
echo MMVCServerSIO
echo MMVCServerSIO.rar
echo backups
echo security_backups
echo .mypy_cache
echo advanced_statistics_*.json
echo api_key.json
echo debug_output.txt
echo zwaifu_launcher_gui.py.backup
echo ZWAIFU-PROJECT.zip
echo zwaifu_exclude.txt
echo *.egg-info
echo build
echo dist
echo .Python
echo .installed.cfg
echo *.egg
echo .DS_Store
echo Thumbs.db
echo *.swp
echo *.swo
echo config_backup_*.json

) > %EXCLUDE_FILE%

REM Remove old archive if exists
if exist "%OUTPUT_FILE%" del "%OUTPUT_FILE%"

REM Archive using WinRAR with complete project structure
echo Creating archive with all project files...
echo Current directory: %CD%

REM List what we're including
echo.
echo Including directories:
if exist "utils" echo - utils/
if exist "config" echo - config/
if exist "docs" echo - docs/
if exist "scripts" echo - scripts/
if exist "plugins" echo - plugins/
if exist "static" echo - static/
if exist "templates" echo - templates/
if exist "ai_tools" echo - ai_tools/
if exist "data" echo - data/

echo.
echo Including core files:
if exist "zwaifu_launcher_gui.py" echo - zwaifu_launcher_gui.py
if exist "launch_launcher.py" echo - launch_launcher.py
if exist "launch_launcher.bat" echo - launch_launcher.bat
if exist "README.md" echo - README.md
if exist "LICENSE" echo - LICENSE
if exist "LAUNCHER_README.md" echo - LAUNCHER_README.md
if exist "SECURITY.md" echo - SECURITY.md
if exist "security_config.json" echo - security_config.json
if exist "example_api_usage.py" echo - example_api_usage.py
if exist "get_admin_key.py" echo - get_admin_key.py
if exist "security_fixes.py" echo - security_fixes.py
if exist "security_audit.py" echo - security_audit.py
if exist "setup_static_analysis.py" echo - setup_static_analysis.py
if exist "monitor_regressions.py" echo - monitor_regressions.py
if exist "mobile_qr.png" echo - mobile_qr.png
if exist ".gitignore" echo - .gitignore

echo.
echo Attempting to create archive...

REM Try multiple methods to create the archive
set "ARCHIVE_CREATED=0"

REM Method 1: WinRAR GUI
if defined WINRAR_PATH (
    echo Method 1: Trying WinRAR GUI...
    "%WINRAR_PATH%" a -r -x@%EXCLUDE_FILE% -ep1 -y -v0 "%OUTPUT_FILE%" .
    if not errorlevel 1 (
        set "ARCHIVE_CREATED=1"
        echo WinRAR GUI method succeeded!
    ) else (
        echo WinRAR GUI method failed, trying next method...
    )
)

REM Method 2: rar command line
if "%ARCHIVE_CREATED%"=="0" (
    echo Method 2: Trying rar command line...
    rar a -r -x@%EXCLUDE_FILE% -ep1 -y -v0 "%OUTPUT_FILE%" .
    if not errorlevel 1 (
        set "ARCHIVE_CREATED=1"
        echo rar command line method succeeded!
    ) else (
        echo rar command line method failed, trying next method...
    )
)

REM Method 3: PowerShell Compress-Archive (Windows 10+)
if "%ARCHIVE_CREATED%"=="0" (
    echo Method 3: Trying PowerShell Compress-Archive...
    powershell -Command "Get-ChildItem -Path '.' -Exclude @(Get-Content '%EXCLUDE_FILE%') | Compress-Archive -DestinationPath '%OUTPUT_FILE%' -Force"
    if not errorlevel 1 (
        set "ARCHIVE_CREATED=1"
        echo PowerShell method succeeded!
    ) else (
        echo PowerShell method failed, trying next method...
    )
)

REM Method 4: 7-Zip if available (create RAR format)
if "%ARCHIVE_CREATED%"=="0" (
    echo Method 4: Trying 7-Zip with RAR format...
    where 7z >nul 2>nul
    if not errorlevel 1 (
        7z a -r -x@%EXCLUDE_FILE% -tRAR -v0 "%OUTPUT_FILE%" .
        if not errorlevel 1 (
            set "ARCHIVE_CREATED=1"
            echo 7-Zip RAR method succeeded!
        ) else (
            echo 7-Zip RAR method failed.
        )
    ) else (
        echo 7-Zip not found.
    )
)

REM Method 5: Manual file copy and RAR creation
if "%ARCHIVE_CREATED%"=="0" (
    echo Method 5: Trying manual file copy and RAR creation...
    echo Creating temporary directory...
    mkdir "%DIST_NAME%" 2>nul
    
    echo Copying files...
    xcopy /E /I /Y /EXCLUDE:%EXCLUDE_FILE% . "%DIST_NAME%"
    
    echo Creating RAR file...
    if defined WINRAR_PATH (
        "%WINRAR_PATH%" a -r -ep1 -y -v0 "%OUTPUT_FILE%" "%DIST_NAME%\*"
    ) else (
        rar a -r -ep1 -y -v0 "%OUTPUT_FILE%" "%DIST_NAME%\*"
    )
    
    if exist "%OUTPUT_FILE%" (
        set "ARCHIVE_CREATED=1"
        echo Manual RAR method succeeded!
    ) else (
        echo Manual RAR method failed.
    )
    
    echo Cleaning up temporary directory...
    rmdir /S /Q "%DIST_NAME%" 2>nul
)

REM Clean up
del %EXCLUDE_FILE%

REM Check if archive was created successfully
if "%ARCHIVE_CREATED%"=="0" (
    echo.
    echo ERROR: All archive creation methods failed!
    echo.
    echo Troubleshooting tips:
    echo 1. Run this script as administrator
    echo 2. Install WinRAR or 7-Zip
    echo 3. Check if you have write permissions in this directory
    echo 4. Try running the Python distribution script instead
    echo.
    echo Attempting to run Python distribution script as fallback...
    python scripts/create_distribution.py
    if exist "Z-Waifu-Launcher-GUI-v%VERSION%.zip" (
        echo Python script succeeded! Created: Z-Waifu-Launcher-GUI-v%VERSION%.zip
        echo Converting to RAR format...
        if defined WINRAR_PATH (
            "%WINRAR_PATH%" a -ep1 -y -v0 "%OUTPUT_FILE%" "Z-Waifu-Launcher-GUI-v%VERSION%.zip"
            if exist "%OUTPUT_FILE%" (
                del "Z-Waifu-Launcher-GUI-v%VERSION%.zip"
                echo Successfully converted to RAR format!
                del %EXCLUDE_FILE%
                pause
                exit /b 0
            )
        ) else (
            rar a -ep1 -y -v0 "%OUTPUT_FILE%" "Z-Waifu-Launcher-GUI-v%VERSION%.zip"
            if exist "%OUTPUT_FILE%" (
                del "Z-Waifu-Launcher-GUI-v%VERSION%.zip"
                echo Successfully converted to RAR format!
                del %EXCLUDE_FILE%
                pause
                exit /b 0
            )
        )
    )
    echo.
    del %EXCLUDE_FILE%
    pause
    exit /b 1
)

if not exist "%OUTPUT_FILE%" (
    echo ERROR: Archive file not found after successful creation!
    del %EXCLUDE_FILE%
    pause
    exit /b 1
)

echo.
echo Done! Created: %OUTPUT_FILE%
echo Archive size: 
for %%A in ("%OUTPUT_FILE%") do echo %%~zA bytes

REM Show what's included in the archive
echo.
echo Archive created successfully!
echo File: %OUTPUT_FILE%
for %%A in ("%OUTPUT_FILE%") do echo Size: %%~zA bytes
echo.
echo Distribution includes:
echo - Main launcher application
echo - Complete utility modules (utils/)
echo - Plugin system (plugins/)
echo - Web interface and templates (static/, templates/)
echo - AI tools configuration (ai_tools/)
echo - Complete documentation (docs/)
echo - Test suite and scripts (scripts/)
echo - Configuration files (config/)
echo - Data files (data/)
echo - Linux support files:
echo   - launch_launcher.sh (Linux launcher)
echo   - run.sh (Simple Linux launcher)
echo   - install_linux.sh (Linux installer)
echo   - zwaifu-launcher.desktop (Desktop entry)
echo   - test_linux_compatibility.py (Compatibility test)
echo   - README_LINUX.md (Linux documentation)
echo   - LINUX_SETUP.md (Setup guide)
pause 